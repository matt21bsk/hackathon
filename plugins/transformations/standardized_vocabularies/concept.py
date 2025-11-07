from pathlib import Path
from psycopg2.extras import execute_values
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor
from models.omop.standardized_vocabularies.concept import Concept
from utils.logger import get_logger
from utils.db_utils import (
    get_cursor_by_sql_file,
    get_cursor_by_schema,
    deactivate_triggers,
    reactivate_triggers,
    get_next_concept_id,
)


logger = get_logger(__name__)

START_CUSTOM_CONCEPT_ID = 2_000_000_000


def load_concepts(
    source_hook,
    target_hook,
    vocabulary_name,
    sql_file_path,
    concept_domain_id,
    batch_size=20_000,
):
    logger.info(f"Chargement des concept locaux : {vocabulary_name}")

    source_conn: PgConnection
    source_cur: PgCursor
    target_conn: PgConnection
    target_cur: PgCursor

    try:
        source_conn, source_cur = get_cursor_by_sql_file(
            pg_hook=source_hook,
            batch_size=batch_size,
            sql_file_path=sql_file_path,
        )

        target_conn, target_cur = get_cursor_by_schema(
            pg_hook=target_hook, schema=Concept.schema
        )

        for table in [Concept.table_name]:
            deactivate_triggers(
                pg_cur=target_cur, pg_conn=target_conn, table_name=table
            )

        batch_num = 0
        next_concept_id = get_next_concept_id(
            pg_cur=target_cur, schema=Concept.schema, table_name=Concept.table_name
        )

        while True:
            rows = source_cur.fetchmany(batch_size)
            if not rows:
                break
            batch_num += 1

            next_concept_id, row_count = __process_batch(
                rows, target_cur, next_concept_id, concept_domain_id
            )

        for table in [Concept.table_name]:
            reactivate_triggers(
                pg_cur=target_cur, pg_conn=target_conn, table_name=table
            )

        # Commit global à la fin
        target_conn.commit()

    except Exception as e:
        logger.exception("Erreur pendant le chargement du vocabulaire local")
        target_conn.rollback()
        raise

    finally:
        for c in [source_cur, target_cur]:
            try:
                c.close()
            except Exception:
                pass
        for conn in [source_conn, target_conn]:
            try:
                conn.close()
            except Exception:
                pass


def __process_batch(
    rows, target_cur, max_concept_id, concept_domain_id
) -> tuple[int, int]:
    if not rows:
        return max_concept_id, 0

    # Création d'une table temporaire
    target_cur.execute(
        """
        CREATE TEMP TABLE tmp_concept (
            source_code TEXT,
            source_label TEXT,
            vocabulary_id TEXT
        ) ON COMMIT DROP;
    """
    )

    # Insertion dans la table temporaire
    execute_values(
        target_cur,
        """
        INSERT INTO tmp_concept (
            source_code,
            source_label,
            vocabulary_id
        ) VALUES %s
        """,
        rows,
        template="(%s, %s, %s)",
    )

    # Insérer dans concept uniquement ce qui n'existe pas
    # en utilisant un SELECT depuis tmp_vocabulary et en filtrant sur les couples existants
    target_cur.execute(
        f"""
        WITH new_concepts AS (
            SELECT
                ROW_NUMBER() OVER () + {max_concept_id} AS concept_id,
                tmp.source_label AS concept_name,
                '{concept_domain_id}' AS domain_id,
                tmp.vocabulary_id AS vocabulary_id,
                'Gender' AS concept_class_id,
                NULL AS standard_concept,
                tmp.source_code AS concept_code,
                DATE '2020-01-01' AS valid_start_date,
                DATE '2099-12-31' AS valid_end_date,
                NULL AS invalid_reason
            FROM
                tmp_concept tmp
                LEFT JOIN {Concept.schema}.{Concept.table_name} c
                    ON c.vocabulary_id = tmp.vocabulary_id
                    AND c.concept_code = tmp.source_code
            WHERE
                c.concept_id IS NULL
        )
        INSERT INTO {Concept.schema}.{Concept.table_name} (
            {", ".join(Concept._columns())}
        )
        SELECT *
        FROM new_concepts;
        """
    )

    return max_concept_id, len(rows)
