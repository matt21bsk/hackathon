from pathlib import Path
from psycopg2.extras import execute_values
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor
from models.omop.standardized_vocabularies.vocabulary import Vocabulary
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


def load_vocabulary(
    source_hook,
    target_hook,
    vocabulary_name,
    sql_file_path,
    batch_size=20_000,
):
    logger.info(f"Chargement du vocabulaire local : {vocabulary_name}")

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
            pg_hook=target_hook, schema=Vocabulary.schema
        )

        for table in [Concept.table_name, Vocabulary.table_name]:
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
                rows, target_cur, next_concept_id
            )

        for table in [Concept.table_name, Vocabulary.table_name]:
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


def __process_batch(rows, target_cur, max_concept_id) -> tuple[int, int]:
    if not rows:
        return max_concept_id, 0

    # Création d'une table temporaire
    target_cur.execute(
        """
        CREATE TEMP TABLE tmp_vocabulary (
            vocabulary_id TEXT,
            vocabulary_name TEXT,
            vocabulary_reference TEXT,
            vocabulary_version TEXT
        ) ON COMMIT DROP;
    """
    )

    # Insertion dans la table temporaire
    execute_values(
        target_cur,
        "INSERT INTO tmp_vocabulary (vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version) VALUES %s",
        rows,
        template="(%s, %s, %s, %s)",
        page_size=1000,
    )

    # Insérer dans concept uniquement ce qui n'existe pas
    # en utilisant un SELECT depuis tmp_vocabulary et en filtrant sur les couples existants
    target_cur.execute(
        f"""
        WITH new_concepts AS (
            SELECT
                ROW_NUMBER() OVER () + {max_concept_id} AS concept_id,
                tmp.vocabulary_name AS concept_name,
                'Metadata' AS domain_id,
                'None' AS vocabulary_id,
                'Vocabulary' AS concept_class_id,
                NULL AS standard_concept,
                tmp.vocabulary_id AS concept_code,
                DATE '2020-01-01' AS valid_start_date,
                DATE '2099-12-31' AS valid_end_date,
                NULL AS invalid_reason
            FROM
                tmp_vocabulary tmp
                LEFT JOIN {Concept.schema}.{Concept.table_name} c
                    ON  c.vocabulary_id = 'None' AND
                        c.concept_code = tmp.vocabulary_id
            WHERE
                c.concept_id IS NULL
        )
        INSERT INTO {Concept.schema}.{Concept.table_name} (
            {", ".join(Concept._columns())}
        )
        SELECT *
        FROM new_concepts
        RETURNING concept_id, concept_code
    """
    )
    new_concept_rows = target_cur.fetchall()
    if not new_concept_rows:
        return max_concept_id, 0

    # Mettre à jour max_concept_id
    max_concept_id = max(c[0] for c in new_concept_rows)

    # Créer un mapping concept_id <-> vocabulary_id
    concept_map = {
        concept_code: concept_id for concept_id, concept_code in new_concept_rows
    }

    # Insérer dans vocabulary avec le concept_id correspondant
    vocabulary_values = []
    for row in rows:
        vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version = row
        concept_id = concept_map.get(vocabulary_id)
        if concept_id is None:
            # Le concept existait déjà, il faudra récupérer son concept_id
            target_cur.execute(
                f"""
                SELECT concept_id
                FROM {Concept.schema}.{Concept.table_name}
                WHERE vocabulary_id = %s AND concept_code = %s
                """,
                (vocabulary_id, vocabulary_id),
            )
            concept_id = target_cur.fetchone()[0]

        vocabulary_values.append(
            (
                vocabulary_id,
                vocabulary_name,
                vocabulary_reference,
                vocabulary_version,
                concept_id,
            )
        )

    vocabulary_insert_query = f"""
        INSERT INTO {Vocabulary.schema}.{Vocabulary.table_name} (
            {", ".join(Vocabulary._columns())}
        )
        VALUES %s
        ON CONFLICT (vocabulary_id) DO NOTHING
    """
    execute_values(
        target_cur,
        vocabulary_insert_query,
        vocabulary_values,
        template=f"({', '.join(['%s'] * len(Vocabulary._columns()))})",
        page_size=1000,
    )
    return max_concept_id, len(rows)
