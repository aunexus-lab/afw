import re
from datetime import datetime
from typing import Optional, Dict


def parse_auth_log_line(line: str) -> Optional[Dict]:
    """
    Parses a line from /var/log/auth.log and returns a structured event dict.
    """
    raw = line.strip()

    pattern = re.compile(
        r"^(?P<month>\w{3}) +(?P<day>\d{1,2}) (?P<time>\d{2}:\d{2}:\d{2}) "
        r"(?P<host>\S+) (?P<process>\w+)\[(?P<pid>\d+)\]: (?P<message>.+)$"
    )

    match = pattern.match(raw)
    if not match:
        return None

    data = match.groupdict()
    month = data["month"]
    day = int(data["day"])
    time_str = data["time"]
    year = datetime.now().year

    # Reconstruct timestamp
    timestamp_str = f"{month} {day} {year} {time_str}"
    timestamp = datetime.strptime(timestamp_str, "%b %d %Y %H:%M:%S")

    message = data["message"]
    process = data["process"]

    ip = None
    port = None
    user = None
    action = "other"
    success = None

    # Case 1: Failed password
    if "Failed password for" in message:
        action = "login_attempt"
        success = False
        m = re.search(r"Failed password for (\w+) from ([\d.]+) port (\d+)", message)
        if m:
            user, ip, port = m.groups()

    # Case 2: Accepted password
    elif "Accepted password for" in message:
        action = "login_attempt"
        success = True
        m = re.search(r"Accepted password for (\w+) from ([\d.]+) port (\d+)", message)
        if m:
            user, ip, port = m.groups()

    # Case 3: Invalid user
    elif "Invalid user" in message:
        action = "invalid_user"
        success = False
        m = re.search(r"Invalid user (\w+) from ([\d.]+) port (\d+)", message)
        if not m:
            m = re.search(r"Invalid user (\w+) from ([\d.]+)", message)
        if m:
            groups = m.groups()
            user = groups[0]
            ip = groups[1]
            if len(groups) > 2:
                port = groups[2]

    # Determine parse_status
    if ip and port:
        parse_status = "parsed"
    elif ip or user:
        parse_status = "partial"
    else:
        parse_status = "unparsed"

    return {
        "timestamp": timestamp.isoformat(),
        "ip": ip,
        "port": int(port) if port else None,
        "process": process,
        "user": user,
        "action": action,
        "success": success,
        "source": "auth",
        "raw": raw,
        "parsed": {
            "host": data.get("host"),
            "message": message,
            "ip": ip,
            "port": port,
            "user": user,
        },
        "parse_status": parse_status,
    }


def parse_with_status(line: str) -> Dict:
    """
    Always returns a structured event dict, even if the line can't be parsed.
    """
    parsed = parse_auth_log_line(line)
    if parsed:
        return parsed
    else:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ip": None,
            "port": None,
            "process": None,
            "user": None,
            "action": "unparsed",
            "success": None,
            "source": "auth",
            "raw": line.strip(),
            "parsed": {},
            "parse_status": "failed"
        }