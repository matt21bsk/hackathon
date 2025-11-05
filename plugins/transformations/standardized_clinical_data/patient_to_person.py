import io
from models.source.patient import PatientDTO
from models.omop.standardized_clinical_data.person import Person
from models.omop.standardized_vocabularies.concept import Concept
from models.omop.standardized_vocabularies.concept_relationship import (
    ConceptRelationship,
)
from utils.logger import get_logger
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor
from utils.db_utils import (
    get_cursor_by_sql_file,
    get_cursor_by_schema,
    deactivate_triggers,
    reactivate_triggers,
    truncate_table,
)

logger = get_logger(__name__)


def load_person(source_hook, target_hook, truncate=False, batch_size=20_000):
    """Orchestre le transfert de patients vers la table OMOP person."""
    logger.info("Début du transfert patient → person")

    source_conn: PgConnection
    source_cur: PgCursor
    target_conn: PgConnection
    target_cur: PgCursor

    try:
        # Execute source query (open cursor, no fetch)
        source_conn, source_cur = get_cursor_by_sql_file(
            pg_hook=source_hook,
            batch_size=batch_size,
            sql_file_path="sql/standardized_clinical_data/person/get_patient.sql",
        )

        # Get target cursor (open cursor, no query)
        target_conn, target_cur = get_cursor_by_schema(
            pg_hook=target_hook, schema=Person.schema
        )

        # Création de la table temporaire tmp_person
        logger.info("Création de la table temporaire tmp_person")
        target_cur.execute(
            """
            DROP TABLE IF EXISTS tmp_person;
            CREATE TEMP TABLE tmp_person (
                idpat TEXT PRIMARY KEY,
                sexe TEXT,
                ddn DATE
            );
        """
        )
        target_conn.commit()

        batch_num = 0
        buffer = io.StringIO()
        while True:
            rows = source_cur.fetchmany(batch_size)
            if not rows:
                break

            patients = [PatientDTO(*row) for row in rows]
            for patient in patients:
                buffer.write("\t".join(patient.to_list()) + "\n")

            buffer.seek(0)
            target_cur.copy_from(
                buffer,
                table="tmp_person",
                sep="\t",
                null="\\N",
                columns=PatientDTO._columns(),
            )
            target_conn.commit()

            buffer.truncate(0)
            buffer.seek(0)
            batch_num += 1
            logger.info(f"Batch {batch_num} chargé dans tmp_person_source")

        # Manage source table
        deactivate_triggers(
            pg_cur=target_cur,
            pg_conn=target_conn,
            table_name=Person.table_name,
        )

        if truncate:
            truncate_table(
                pg_cur=target_cur,
                pg_conn=target_conn,
                table_name=Person.table_name,
            )

        logger.info("Insertion des nouveaux patients dans la table OMOP person")
        insert_sql = f"""
        WITH gender_map AS (
            SELECT
                src.concept_id AS source_concept_id,
                src.concept_code AS source_concept_code,
                tgt.concept_id AS target_concept_id,
                tgt.concept_code AS target_concept_code,
                tgt.domain_id AS target_domain_id,
                tgt.standard_concept AS target_standard_concept
            FROM
                {ConceptRelationship.schema}.{ConceptRelationship.table_name} rel
                JOIN {Concept.schema}.{Concept.table_name} src
                    ON rel.concept_id_1 = src.concept_id
                JOIN {Concept.schema}.{Concept.table_name} tgt
                    ON rel.concept_id_2 = tgt.concept_id
            WHERE
                tgt.domain_id = 'Gender'
                AND rel.relationship_id = 'Maps to'
                AND tgt.standard_concept = 'S'
                AND src.concept_id >= 2000000000
        ),
        max_id AS (
            SELECT
                COALESCE(MAX(person_id), 0) AS base_id
            FROM
                {Person.schema}.{Person.table_name}
        ),
        new_rows AS (
            SELECT
                t.idpat,
                t.sexe,
                t.ddn
            FROM
                tmp_person t
                LEFT JOIN {Person.schema}.{Person.table_name} p
                    ON p.person_source_value = t.idpat
            WHERE
                p.person_source_value IS NULL
        ),
        numbered AS (
            SELECT
                ROW_NUMBER() OVER () AS rn,
                n.*
            FROM
                new_rows n
        )
        INSERT INTO {Person.schema}.{Person.table_name} (
            {', '.join(Person._columns())}
        )
        SELECT
            m.base_id + rn                      AS person_id,
            COALESCE(g.target_concept_id, 0)    AS gender_concept_id,
            EXTRACT(YEAR FROM n.ddn)::INT       AS year_of_birth,
            EXTRACT(MONTH FROM n.ddn)::INT      AS month_of_birth,
            EXTRACT(DAY FROM n.ddn)::INT        AS day_of_birth,
            n.ddn                               AS birth_datetime,
            0                                   AS race_concept_id,
            0                                   AS ethnicity_concept_id,
            NULL                                AS location_id,
            NULL                                AS provider_id,
            NULL                                AS care_site_id,
            n.idpat                             AS person_source_value,
            g.source_concept_code               AS gender_source_value,
            g.source_concept_id                 AS gender_source_concept_id,
            NULL                                AS race_source_value,
            NULL                                AS race_source_concept_id,
            NULL                                AS ethnicity_source_value,
            NULL                                AS ethnicity_source_concept_id
        FROM
            numbered n
            CROSS JOIN max_id m
            LEFT JOIN gender_map g
                ON n.sexe = g.source_concept_code
        RETURNING person_id;
        """

        target_cur.execute(insert_sql)
        inserted_count = len(target_cur.fetchall())
        target_conn.commit()

        logger.info(
            f"{inserted_count} nouveaux patients insérés dans {Person.schema}.{Person.table_name}"
        )

        # Suppression de la table temporaire tmp_person
        logger.info("Suppression de la table temporaire tmp_person")
        target_cur.execute(
            """
            DROP TABLE IF EXISTS tmp_person;
            """
        )
        target_conn.commit()

        # Réactivation des triggers
        reactivate_triggers(
            pg_cur=target_cur,
            pg_conn=target_conn,
            table_name=Person.table_name,
        )

    except Exception as e:
        logger.exception("Erreur pendant le chargement de person")
        raise

    finally:
        if source_cur:
            try:
                source_cur.close()
                logger.debug("Curseur source fermé.")
            except Exception:
                logger.warning("Impossible de fermer le curseur source.")
        if source_conn:
            try:
                source_conn.close()
                logger.debug("ConnexPerson.taion source fermée.")
            except Exception:
                logger.warning("Impossible de fermer la connexion source.")
        if target_cur:
            try:
                target_cur.close()
                logger.debug("Curseur cible fermé.")
            except Exception:
                logger.warning("Impossible de fermer le curseur cible.")
        if target_conn:
            try:
                target_conn.close()
                logger.debug("Connexion cible fermée.")
            except Exception:
                logger.warning("Impossible de fermer la connexion cible.")
