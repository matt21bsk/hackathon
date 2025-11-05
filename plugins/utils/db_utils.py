from pathlib import Path
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor
from utils.logger import get_logger

logger = get_logger(__name__)

START_CUSTOM_CONCEPT_ID = 2_000_000_000


def get_cursor_by_sql_file(
    pg_hook, batch_size: int, sql_file_path: str
) -> tuple[PgConnection, PgCursor]:
    """Initialise la connexion source et exécute une requête SQL."""
    pg_conn = pg_hook.get_conn()
    pg_cur = pg_conn.cursor(name="vocabulary_cursor")
    pg_cur.itersize = batch_size

    sql_path = Path(sql_file_path)
    if not sql_path.exists():
        raise FileNotFoundError(f"Le fichier SQL {sql_file_path} est introuvable.")

    with open(sql_path, "r", encoding="utf-8") as f:
        source_query = f.read().strip()

    logger.info(f"Exécution de la requête depuis {sql_file_path}")
    pg_cur.execute(source_query)
    return pg_conn, pg_cur


def get_cursor_by_schema(pg_hook, schema: str) -> tuple[PgConnection, PgCursor]:
    """Initialise la connexion cible (PostgreSQL OMOP) avec le search_path."""
    pg_conn = pg_hook.get_conn()
    pg_cur = pg_conn.cursor()
    pg_cur.execute(f"SET search_path TO {schema};")
    pg_conn.commit()
    return pg_conn, pg_cur


def deactivate_triggers(pg_cur: PgCursor, pg_conn: PgConnection, table_name: str):
    """Désactive les triggers pour accélérer l’insertion."""
    logger.info(f"Désactivation des triggers pour {table_name}")
    pg_cur.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL;")
    pg_conn.commit()


def reactivate_triggers(pg_cur: PgCursor, pg_conn: PgConnection, table_name: str):
    """Réactive les triggers après le chargement."""
    logger.info(f"Réactivation des triggers pour {table_name}")
    pg_cur.execute(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL;")
    pg_conn.commit()


def truncate_table(pg_cur: PgCursor, pg_conn: PgConnection, table_name: str):
    """Truncate table cascade"""
    logger.info(f"TRUNCATE table {table_name} CASCADE")
    pg_cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
    pg_conn.commit()


def get_next_concept_id(pg_cur: PgCursor, schema: str, table_name: str) -> int:
    """Retourne le prochain concept_id disponible (>= 2_000_000_000)."""
    pg_cur.execute(
        f"""
        SELECT COALESCE(MAX(concept_id), {START_CUSTOM_CONCEPT_ID - 1}) + 1
        FROM {schema}.{table_name}
        WHERE concept_id >= {START_CUSTOM_CONCEPT_ID};
        """
    )
    row = pg_cur.fetchone()
    if not row or row[0] is None:
        logger.warning(
            f"Aucune ligne trouvée dans {schema}.{table_name}, initialisation à {START_CUSTOM_CONCEPT_ID}"
        )
        return START_CUSTOM_CONCEPT_ID
    return int(row[0])
