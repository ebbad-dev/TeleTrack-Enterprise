"""
TeleTrack Enterprise — Network Discovery Engine
Automated subnet scanning to discover and register devices.
"""

import ipaddress
import ping3
from celery import shared_task
from extensions import db
from models.device import Device
from services.notification_service import NotificationService

@shared_task(name='tasks.discovery.scan_subnet')
def scan_subnet(subnet_cidr, vendor="Unknown", default_type="Server", location_id=None):
    """
    Scans a given subnet (e.g., 192.168.1.0/24) for active IP addresses using ICMP pings.
    Automatically adds responding IPs to the device inventory if they don't exist.
    """
    try:
        network = ipaddress.ip_network(subnet_cidr, strict=False)
    except ValueError as e:
        return {"success": False, "error": f"Invalid subnet CIDR: {e}"}

    active_ips = []
    new_devices_count = 0

    # For testing, we might limit the scan size if it's too large
    if network.num_addresses > 1024:
        return {"success": False, "error": "Subnet too large for automated scan (Max /22)"}

    # Iterate over all hosts in the network
    for ip in network.hosts():
        ip_str = str(ip)
        try:
            # Ping with 0.5s timeout
            delay = ping3.ping(ip_str, timeout=0.5)
            if delay is not None:
                active_ips.append(ip_str)
                
                # Check if device exists
                existing = Device.query.filter_by(ip_address=ip_str, is_deleted=False).first()
                if not existing:
                    # Register new device
                    new_device = Device(
                        device_name=f"Discovered-Host-{ip_str.replace('.', '-')}",
                        ip_address=ip_str,
                        device_type=default_type,
                        status="online",
                        location_id=location_id
                    )
                    db.session.add(new_device)
                    new_devices_count += 1
        except Exception:
            pass # ignore errors on individual ping

    if new_devices_count > 0:
        db.session.commit()
        # System notification for new devices
        NotificationService.create_notification(
            user_id=1, # Admin
            title="Network Discovery Complete",
            message=f"Subnet scan on {subnet_cidr} completed. Discovered {new_devices_count} new active devices.",
            notification_type="info",
            link="/devices"
        )

    return {
        "success": True, 
        "scanned_ips": network.num_addresses - 2, 
        "active_ips": len(active_ips),
        "new_devices_registered": new_devices_count
    }
