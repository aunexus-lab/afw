# core/storage

Interfaces for PostgreSQL, Redis

logs_events
| Column         | Type          | Description                                                           |
| -------------- | ------------- | --------------------------------------------------------------------- |
| `id`           | `SERIAL`      | Auto-incremented primary key for internal use                         |
| `timestamp`    | `TIMESTAMPTZ` | The original timestamp extracted from the log file                    |
| `ip`           | `INET`        | The originating IP address of the event (supports IPv4/IPv6)          |
| `port`         | `INTEGER`     | The port used in the connection (if available)                        |
| `process`      | `TEXT`        | The system process name (e.g., `sshd`, `nginx`, etc.)                 |
| `user_name`    | `TEXT`        | The username involved in the event, if applicable                     |
| `action`       | `TEXT`        | Type of action (e.g., `login_attempt`, `invalid_user`, etc.)          |
| `success`      | `BOOLEAN`     | Whether the action succeeded or failed (e.g., authentication success) |
| `source`       | `TEXT`        | Log source or origin (e.g., `auth`, `nginx`, `odoo`)                  |
| `parse_status` | `TEXT`        | Parsing status: `'parsed'` or `'failed'`                              |
| `raw`          | `TEXT`        | The raw log line as originally read                                   |
| `parsed`       | `JSONB`       | Additional parsed metadata in flexible structure (e.g., host, method) |
| `created_at`   | `TIMESTAMPTZ` | Timestamp when the row was inserted into the database (default: now)  |
