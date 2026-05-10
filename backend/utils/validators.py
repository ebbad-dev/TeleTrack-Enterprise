"""
TeleTrack Enterprise — Input Validators
Validation functions for IP addresses, emails, and other inputs.
"""

import re


def validate_ip_address(ip: str) -> bool:
    """Validate IPv4 address format."""
    if not ip:
        return False
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    parts = ip.split(".")
    return all(0 <= int(part) <= 255 for part in parts)


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_mac_address(mac: str) -> bool:
    """Validate MAC address format (XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX)."""
    if not mac:
        return False
    pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return re.match(pattern, mac) is not None


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize a string input by stripping and truncating."""
    if not value:
        return ""
    return value.strip()[:max_length]


def validate_severity(severity: str) -> bool:
    """Validate severity level."""
    return severity.lower() in ("critical", "high", "medium", "low")


def validate_device_status(status: str) -> bool:
    """Validate device status."""
    return status.lower() in ("online", "offline", "degraded", "maintenance")
