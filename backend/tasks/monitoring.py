"""
TeleTrack Enterprise — Monitoring Tasks
Celery tasks for device ping, metrics collection, and health monitoring.
"""

import random
import logging
from celery import shared_task
from ping3 import ping
from extensions import db, socketio
from models import Device, Alert, DeviceMetric
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@shared_task(name='tasks.monitoring.ping_all_devices')
def ping_all_devices():
    """
    Ping all active devices. Updates status and generates alerts
    when devices go offline or come back online.
    """
    logger.info("Starting global ping cycle...")

    devices = Device.query.filter_by(is_deleted=False).all()
    offline_count = 0
    online_count = 0

    for device in devices:
        if not device.ip_address:
            continue

        try:
            response = ping(device.ip_address, timeout=2)
            was_offline = (device.status == 'offline')

            if response is not None and response is not False:
                device.status = 'online'
                device.last_ping_time = datetime.now(timezone.utc)
                online_count += 1

                # Store latency metric
                try:
                    latency_ms = round(response * 1000, 2)
                    metric = DeviceMetric(
                        device_id=device.id,
                        metric_type="latency",
                        value=latency_ms,
                        unit="ms",
                    )
                    db.session.add(metric)
                except Exception:
                    pass

                if was_offline:
                    # Device recovered — resolve related alerts
                    active_alerts = Alert.query.filter_by(
                        device_id=device.id, status='open', severity='critical'
                    ).all()
                    for alert in active_alerts:
                        if alert.message and "offline" in alert.message.lower():
                            alert.status = 'resolved'
                            alert.resolved_time = datetime.now(timezone.utc)
                            alert.resolution_note = "Auto-resolved: Device back online"

                    try:
                        from services.notification_service import notify_device_online
                        notify_device_online(device)
                    except Exception as e:
                        logger.error(f"Notification error: {e}")

                    # Emit WebSocket event
                    socketio.emit("device_status_change", {
                        "device_id": device.id,
                        "device_name": device.device_name,
                        "status": "online",
                        "ip_address": device.ip_address,
                    })
            else:
                device.status = 'offline'
                offline_count += 1

                # ─── Maintenance Mode Check ──────────────────────────
                is_in_maintenance = (
                    device.maintenance_until and 
                    device.maintenance_until > datetime.now(timezone.utc).replace(tzinfo=None)
                )

                if not was_offline and not is_in_maintenance:
                    # Device just went offline — generate alert
                    new_alert = Alert(
                        device_id=device.id,
                        alert_type="Device Offline",
                        message=f"CRITICAL: Device {device.device_name} ({device.ip_address}) went OFFLINE. Ping timed out.",
                        severity='critical',
                        status='open',
                    )
                    db.session.add(new_alert)

                    try:
                        from services.notification_service import notify_device_offline, notify_new_alert
                        notify_device_offline(device)
                        db.session.flush()
                        notify_new_alert(new_alert)
                    except Exception as e:
                        logger.error(f"Notification error: {e}")

                    # Emit WebSocket event
                    socketio.emit("device_status_change", {
                        "device_id": device.id,
                        "device_name": device.device_name,
                        "status": "offline",
                        "ip_address": device.ip_address,
                    })
                    socketio.emit("new_alert", {
                        "device_name": device.device_name,
                        "severity": "critical",
                        "message": f"Device {device.device_name} went OFFLINE",
                    })

        except Exception as e:
            logger.error(f"Error pinging device {device.ip_address}: {str(e)}")
            device.status = 'degraded'

    db.session.commit()
    logger.info(f"Ping cycle completed. {online_count} online, {offline_count} offline.")

    # Emit dashboard refresh event
    socketio.emit("dashboard_update", {
        "online": online_count,
        "offline": offline_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return f"{online_count} online, {offline_count} offline"


@shared_task(name='tasks.monitoring.collect_device_metrics')
def collect_device_metrics():
    """
    Collect simulated device metrics (CPU, memory, temperature).
    In production, this would use SNMP or device APIs.
    For demo purposes, generates realistic simulated data with
    correlation to device status.
    """
    logger.info("Starting metrics collection cycle...")

    devices = Device.query.filter_by(is_deleted=False, monitoring_enabled=True).all()
    collected = 0

    for device in devices:
        if not device.ip_address:
            continue

        try:
            # Generate realistic metrics based on device status
            if device.status == 'offline':
                continue  # No metrics for offline devices

            # Base values vary by device type
            is_degraded = device.status == 'degraded'
            base_cpu = random.uniform(35, 75) if not is_degraded else random.uniform(75, 95)
            base_mem = random.uniform(40, 70) if not is_degraded else random.uniform(70, 92)
            base_temp = random.uniform(35, 55) if not is_degraded else random.uniform(55, 78)

            # Add some noise for realism
            cpu = round(min(100, max(0, base_cpu + random.gauss(0, 5))), 1)
            memory = round(min(100, max(0, base_mem + random.gauss(0, 3))), 1)
            temperature = round(max(20, base_temp + random.gauss(0, 2)), 1)

            metrics = [
                DeviceMetric(device_id=device.id, metric_type="cpu", value=cpu, unit="%"),
                DeviceMetric(device_id=device.id, metric_type="memory", value=memory, unit="%"),
                DeviceMetric(device_id=device.id, metric_type="temperature", value=temperature, unit="°C"),
            ]

            for m in metrics:
                db.session.add(m)

            # Update device snapshot fields
            device.cpu_usage = cpu
            device.memory_usage = memory
            device.temperature = temperature

            collected += 1

            # Auto-generate alert for high temperature
            if temperature > 70 and not is_degraded:
                existing = Alert.query.filter_by(
                    device_id=device.id,
                    alert_type="High Temperature",
                    status="open",
                ).first()
                if not existing:
                    alert = Alert(
                        device_id=device.id,
                        alert_type="High Temperature",
                        severity="high",
                        message=f"Device {device.device_name} temperature is {temperature}°C (threshold: 70°C)",
                        status="open",
                    )
                    db.session.add(alert)

            # Auto-generate alert for high CPU
            if cpu > 90:
                existing = Alert.query.filter_by(
                    device_id=device.id,
                    alert_type="High CPU Usage",
                    status="open",
                ).first()
                if not existing:
                    alert = Alert(
                        device_id=device.id,
                        alert_type="High CPU Usage",
                        severity="medium",
                        message=f"Device {device.device_name} CPU usage is {cpu}% (threshold: 90%)",
                        status="open",
                    )
                    db.session.add(alert)

        except Exception as e:
            logger.error(f"Error collecting metrics for device {device.id}: {str(e)}")

    db.session.commit()
    logger.info(f"Metrics collection completed. {collected} devices measured.")
    return f"{collected} devices"


@shared_task(name='tasks.monitoring.analyze_predictive_trends')
def analyze_predictive_trends():
    """
    Predictive Analytics Engine.
    Uses Z-Score statistical anomaly detection to identify unusual patterns
    before they become outages (Phase 5).
    """
    import statistics
    from sqlalchemy import func
    
    logger.info("Starting predictive analytics cycle...")
    devices = Device.query.filter_by(is_deleted=False, monitoring_enabled=True).all()
    anomalies_found = 0

    for device in devices:
        # Check CPU, Memory, and Latency for anomalies
        for m_type in ['cpu', 'memory', 'latency']:
            # Get last 20 samples for baseline
            recent_metrics = DeviceMetric.query.filter_by(
                device_id=device.id, 
                metric_type=m_type
            ).order_by(DeviceMetric.timestamp.desc()).limit(20).all()

            if len(recent_metrics) < 10:
                continue # Need enough data for a baseline

            values = [m.value for m in recent_metrics]
            current_value = values[0]
            baseline = values[1:] # Exclude the most recent one for comparison

            mean = statistics.mean(baseline)
            stdev = statistics.stdev(baseline)

            if stdev == 0: continue

            # Calculate Z-score (standard deviations from mean)
            z_score = abs(current_value - mean) / stdev

            # Threshold: 3.0 is a common statistical anomaly (99.7% confidence)
            if z_score > 3.0:
                # Potential Anomaly Detected
                existing = Alert.query.filter_by(
                    device_id=device.id,
                    alert_type="Anomaly Detected",
                    status="open"
                ).filter(Alert.message.contains(m_type)).first()

                if not existing:
                    alert = Alert(
                        device_id=device.id,
                        alert_type="Anomaly Detected",
                        severity="warning",
                        message=f"PREDICTIVE: Unusual {m_type} pattern detected on {device.device_name}. Value {current_value} is {round(z_score, 2)}σ from baseline.",
                        status="open",
                    )
                    db.session.add(alert)
                    anomalies_found += 1
                    
                    # Log to audit for security/tracing
                    from models.supporting import AuditLog
                    audit = AuditLog(
                        action="ANOMALY_DETECTED",
                        resource="DeviceMetric",
                        resource_id=device.id,
                        new_value=f"Z-Score: {z_score} for {m_type}"
                    )
                    db.session.add(audit)

    db.session.commit()
    logger.info(f"Predictive cycle completed. {anomalies_found} anomalies flagged.")
    return f"{anomalies_found} anomalies"

