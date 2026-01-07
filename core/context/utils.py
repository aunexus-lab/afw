# core/contect/utils.py
import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config.config import MODEL_PATH 

load_dotenv()
PG_DSN = os.getenv("PG_DSN")

def get_active_strategy_view():
    conn = psycopg2.connect(os.getenv("PG_DSN"))
    with conn.cursor() as cur:
        cur.execute("""
            SELECT materialized_view_name
            FROM enrichment_strategies
            WHERE is_active = TRUE
            LIMIT 1;
        """)
        result = cur.fetchone()
        if not result:
            raise ValueError("No active enrichment strategy found.")
        return result[0]

def get_active_strategy_id():
    conn = psycopg2.connect(os.getenv("PG_DSN"))
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM enrichment_strategies
            WHERE is_active = TRUE
            LIMIT 1;
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No active enrichment strategy found.")
        return row[0]

def is_valid_view_name(name):
    return name.isidentifier() and not any(char in name for char in [';', '--', ' '])


def get_active_strategy_id():
    """
    Returns the ID of the currently active enrichment strategy.
    Raises an exception if no active strategy is found.
    """
    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM enrichment_strategies
                WHERE is_active = TRUE
                LIMIT 1;
            """)
            row = cur.fetchone()
            if not row:
                raise ValueError("No active enrichment strategy found.")
            return row[0]

def adopt_strategy(recall):
    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            # 1. Get active strategy 
            cur.execute("SELECT id FROM enrichment_strategies WHERE is_active = TRUE LIMIT 1;")
            row = cur.fetchone()
            if not row:
                raise Exception("No active enrichment strategy found.")
            strategy_id = row[0]

            # 2. Search for the last training for the active strategy 
            cur.execute("""
                SELECT recall_macro FROM training_runs
                WHERE strategy_id = %s
                ORDER BY run_at DESC LIMIT 1;
            """, (strategy_id,))
            last_row = cur.fetchone()
            previous_recall = last_row[0] if last_row else None

            # 3. Assessment of the new training run
            return previous_recall is None or recall > previous_recall

def register_training_run(accuracy, recall, loss, notes="", training_duration=None, model_hash=False, compress=False):
    """
    Registers a new training run in the database.
    Returns True if the new model was adopted, False otherwise.
    """
    adopted = adopt_strategy(recall)
    is_better = adopted
    
    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            #Insert the new training run
            cur.execute("""
                INSERT INTO training_runs (
                    strategy_id,
                    run_at,
                    model_path,
                    accuracy,
                    recall_macro,
                    loss,
                    is_better_than_previous,
                    adopted,
                    notes,
                    training_duration_seconds,
                    model_hash,
                    model_compressed_path
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                get_active_strategy_id(),
                datetime.utcnow(),
                MODEL_PATH,
                accuracy,
                recall,
                loss,
                is_better,
                adopted,
                notes or "Trained with new batch of data",
                training_duration if training_duration is not None else None,
                get_model_hash() if model_hash else None,
                f"{MODEL_PATH}.zip" if compress else None
            ))

            if compress:
                compress_model(MODEL_PATH, f"{MODEL_PATH}.zip")
                print(f"Model compressed to {MODEL_PATH}.zip")

            print("Training run registered.")
            if adopted:
                print("New model adopted.")
            else:
                print("ℹModel not adopted — recall not better than previous.")
            conn.commit()

            return adopted
        
def compute_sha256(filepath):
    import hashlib
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_model_hash():
    """
    Computes the SHA-256 hash of the model file.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    
    return compute_sha256(MODEL_PATH)

def get_model_info():
    """
    Returns a dictionary with model metadata.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    
    return {
        "path": MODEL_PATH,
        "hash": get_model_hash(),
        "size": os.path.getsize(MODEL_PATH),
        "last_modified": datetime.fromtimestamp(os.path.getmtime(MODEL_PATH))
    }

def compress_model(model_path, output_path):
    import zipfile
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(model_path, arcname = os.path.basename(model_path))

def get_active_model_info():
    """
        Recupera la información del último modelo adoptado desde la tabla training_runs.
    """
    query = """
        SELECT 
            tr.id,
            es.name AS strategy_name,
            tr.run_at,
            tr.model_path,
            tr.model_hash,
            tr.accuracy,
            tr.recall_macro,
            tr.loss
        FROM training_runs tr
        JOIN enrichment_strategies es ON tr.strategy_id = es.id
        WHERE tr.adopted = TRUE
        ORDER BY tr.run_at DESC
        LIMIT 1;
    """

    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
            if not row:
                raise ValueError("No adopted model found in training_runs.")

            return {
                "training_run_id"   : row[0],
                "strategy_name"     : row[1],
                "run_at"            : row[2],
                "model_path"        : row[3],
                "model_hash"        : row[4],
                "accuracy"          : row[5],
                "recall_macro"      : row[6],
                "loss"              : row[7],
            }
        
def verify_model_integrity(path: str):
    import hashlib
    with open(path, "rb") as f:
        content = f.read()
    actual_hash = hashlib.sha256(content).hexdigest()
    if actual_hash != get_active_model_info()['model_hash']:
        raise RuntimeError("Model integrity check failed!")
