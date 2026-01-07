import psycopg2
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
PG_DSN = os.getenv("PG_DSN")

def enrich_event(event: dict, debug: bool = False) -> dict:
    raw_ts = event.get("timestamp")

    if isinstance(raw_ts, pd.Timestamp):
        timestamp = raw_ts.to_pydatetime().astimezone(timezone.utc)
    elif isinstance(raw_ts, str):
        timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).astimezone(timezone.utc)
    else:
        raise ValueError(f"Unsupported timestamp format: {type(raw_ts)} — {raw_ts}")

    # timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")).astimezone(timezone.utc)
    ip = event.get("ip", "")
    enriched = {}

    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:

            def query_and_fetch(sql, params, key, fallback_sql=None, fallback_params=None):
                if debug:
                    print(f"\n🔍 Running query for {key}:")
                    print(cur.mogrify(sql, params).decode())

                cur.execute(sql, params)
                result = cur.fetchone()[0]

                if result in (None, 0) and fallback_sql:
                    fp = fallback_params if fallback_params else params
                    if debug:
                        print(f"⚠️ No result for {key}, running fallback:")
                        print(cur.mogrify(fallback_sql, fp).decode())
                    cur.execute(fallback_sql, fp)
                    result = cur.fetchone()[0]

                enriched[key] = float(result) if result is not None else 0.0

            # 1. IP: Block history
            # This query counts how many times the IP has been blocked in the past.
            query_and_fetch(
                """
                SELECT COUNT(*) FROM event_features_for_nn
                WHERE ip = %s::inet AND label_action = 'block';
                """,
                (ip,),
                key="ip_block_history"
            )

            # 2. IP: Last 24 hours (general fallback)
            query_and_fetch(
                """
                SELECT COUNT(*) FROM event_features_for_nn
                WHERE ip = %s::inet AND timestamp > %s;
                """,
                (ip, timestamp - timedelta(hours=24)),
                key="ip_recent_event_count",
                fallback_sql="""
                    SELECT COUNT(*) FROM event_features_for_nn
                    WHERE ip = %s::inet;
                """,
                fallback_params=(ip,)
            )

            # 3. IP: Avg score last hour (general fallback)
            query_and_fetch(
                """
                SELECT AVG(score) FROM event_features_for_nn
                WHERE ip = %s::inet AND timestamp > %s;
                """,
                (ip, timestamp - timedelta(hours=1)),
                key="ip_avg_score_last_hour",
                fallback_sql="""
                    SELECT AVG(score) FROM event_features_for_nn
                    WHERE ip = %s::inet;
                """,
                fallback_params=(ip,)
            )

            # 4. IP: Invalid_user ratio in last 24h (with fallback)
            cur.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE action = 'invalid_user')::float / NULLIF(COUNT(*), 0)
                FROM event_features_for_nn
                WHERE ip = %s::inet AND timestamp > %s;
            """, (ip, timestamp - timedelta(hours=24)))
            ratio = cur.fetchone()[0]
            if ratio is None:
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE action = 'invalid_user')::float / NULLIF(COUNT(*), 0)
                    FROM event_features_for_nn
                    WHERE ip = %s::inet;
                """, (ip,))
                ratio = cur.fetchone()[0]
            enriched["invalid_user_ratio_ip"] = round(float(ratio), 4) if ratio else 0.0

            # 5. IP: External risk and inactivity
            cur.execute("""
                SELECT score, last_event FROM ip_risk_score WHERE ip = %s;
            """, (ip,))
            row = cur.fetchone()
            if row:
                risk_score, last_seen = row
                enriched["ip_risk_score"] = float(risk_score) if risk_score else 0.0
                if last_seen:
                    days = (timestamp - last_seen).days
                    enriched["ip_inactive_days"] = days if days >= 0 else 999
                else:
                    enriched["ip_inactive_days"] = 999
            else:
                enriched["ip_risk_score"] = 0.0
                enriched["ip_inactive_days"] = 999

    return enriched
