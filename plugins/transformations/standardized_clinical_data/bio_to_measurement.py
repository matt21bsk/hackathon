import io
from models.omop.standardized_clinical_data.measurement import Measurement
from models.omop.standardized_clinical_data.visit_occurrence import VisitOccurrence
from models.source.biologie import BiologieDTO
from models.source.diag import DiagDTO
from models.omop.standardized_clinical_data.person import Person
from models.omop.standardized_vocabularies.concept import Concept
from models.omop.standardized_vocabularies.concept_relationship import (
    ConceptRelationship,
)
from models.source.venue import VenueDTO
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


def load_measurement(source_hook, target_hook, truncate=False, batch_size=20_000):
    """Orchestre le transfert de la biologie vers la table measurement """
    logger.info("Début du transfert bio → measurement")

    source_conn: PgConnection
    source_cur: PgCursor
    target_conn: PgConnection
    target_cur: PgCursor

    try:
        # Execute source query (open cursor, no fetch)
        source_conn, source_cur = get_cursor_by_sql_file(
            pg_hook=source_hook,
            batch_size=batch_size,
            sql_file_path="sql/standardized_clinical_data/measurement/get_bio.sql",
        )

        # Get target cursor (open cursor, no query)
        target_conn, target_cur = get_cursor_by_schema(
            pg_hook=target_hook, schema=Measurement.schema
        )

        # Création de la table temporaire tmp_bio
        logger.info("Création de la table temporaire tmp_bio")
        target_cur.execute(
            """
            DROP TABLE IF EXISTS tmp_bio;
            CREATE TEMP TABLE tmp_bio (
                idpat TEXT,
                sej TEXT,
                date_result DATE,
                value FLOAT,
                unit_name TEXT,
                norm_lower FLOAT,
                norm_upper FLOAT,
                source_concept_name TEXT,
                verbatim TEXT,
                source_concept_code TEXT
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


            # Transformer chaque ligne en objet DiagDTO
            bios = [BiologieDTO(*row) for row in rows]
            for bio in bios :
                buffer.write("\t".join(bio.to_list()) + "\n") # renvoie les attributs de chaque DTO séparés par une tabulation ligne par ligne avec saut de ligne

            buffer.seek(0)    # ramène le curseur au début des résultats du buffer
            target_cur.copy_from(
                buffer,
                table="tmp_bio",  # destination des données
                sep="\t",            # Séparateur entre les valeurs → tabulation
                null="\\N",          # valeur nulle
                columns=BiologieDTO._columns() # ordre des colonnes  à remplir
            )
            target_conn.commit()

            buffer.truncate(0) # vide le buffer
            buffer.seek(0)   # remet le curseur au  départ
            batch_num += 1  # compteur +1  à chaque nouveau batch
            logger.info(f"Batch {batch_num} chargé dans tmp_bio")

        # Manage table
        deactivate_triggers(
            pg_cur=target_cur,
            pg_conn=target_conn,
            table_name=Measurement.table_name,
        )

        if truncate:
            truncate_table(
                pg_cur=target_cur,
                pg_conn=target_conn,
                table_name=Measurement.table_name,
            )

        logger.info("Insertion des venues dans la table OMOP measurement")
        insert_sql = f"""
        WITH loinc_mapping as (
             SELECT
                src.concept_id AS source_concept_id,
                src.concept_code AS source_concept_code,
                tgt.concept_id AS target_concept_id,
                tgt.concept_code AS target_concept_code,
                tgt.domain_id AS target_domain_id,
                tgt.standard_concept AS target_standard_concept
            FROM
                {Concept.schema}.{Concept.table_name} src
                LEFT JOIN {ConceptRelationship.schema}.{ConceptRelationship.table_name} rel
                    ON rel.concept_id_1 = src.concept_id
                    AND rel.relationship_id = 'Maps to'
                LEFT JOIN {Concept.schema}.{Concept.table_name} tgt
                    ON rel.concept_id_2 = tgt.concept_id
                    AND tgt.domain_id = 'Measurement'
                    AND tgt.standard_concept = 'S'
            WHERE
                src.domain_id = 'Measurement'
                AND src.concept_id >= 2000000000
        ),
        unit as (
            SELECT
                src.concept_id AS source_concept_id,
                src.concept_code AS source_concept_code,
                tgt.concept_id AS target_concept_id,
                tgt.concept_code AS target_concept_code,
                tgt.domain_id AS target_domain_id,
                tgt.standard_concept AS target_standard_concept
            FROM
                {Concept.schema}.{Concept.table_name} src
                LEFT JOIN {ConceptRelationship.schema}.{ConceptRelationship.table_name} rel
                    ON rel.concept_id_1 = src.concept_id
                    AND rel.relationship_id = 'Maps to'
                LEFT JOIN {Concept.schema}.{Concept.table_name} tgt
                    ON rel.concept_id_2 = tgt.concept_id
                    AND tgt.domain_id = 'Unit'
                    AND tgt.standard_concept = 'S'
            WHERE
                src.domain_id = 'Unit'
                AND src.concept_id >= 2000000000
        )
        INSERT INTO {Measurement.schema}.{Measurement.table_name}
        ({', '.join(Measurement._columns())})
        SELECT
            v.person_id                                  AS person_id,
            COALESCE(map.target_concept_id, 0)           AS measurement_concept_id,
            tmp.date_result                              AS measurement_date,
            32810                                        AS measurement_type_concept_id,
            tmp.value                                    AS value_as_number,
            COALESCE(u.target_concept_id,0)              AS unit_concept_id,
            tmp.norm_lower                               AS range_low,
            tmp.norm_upper                               AS range_high,
            v.visit_occurrence_id                        AS visit_occurrence_id,
            tmp.source_concept_name                      AS measurement_source_value,
            map.source_concept_id                        AS measurement_source_concept_id,
            tmp.unit_name                                AS unit_source_value,
            u.source_concept_id                          AS unit_source_concept_id,
            tmp.verbatim                                 AS value_source_value
        FROM
           tmp_bio tmp
           LEFT JOIN {VisitOccurrence.schema}.{VisitOccurrence.table_name} v
           ON  tmp.sej = v.visit_source_value
           LEFT JOIN loinc_mapping map
           ON tmp.source_concept_code = map.source_concept_code
           LEFT JOIN unit u
           ON tmp.unit_name = u.source_concept_code
        RETURNING  measurement_id
        """

        target_cur.execute(insert_sql)
        inserted_count = len(target_cur.fetchall()) # nombre de lignes insérées
        target_conn.commit()

        logger.info(
            f"{inserted_count} nouvelles mesures  insérés dans {Measurement.schema}.{Measurement.table_name}"
        )


        # Suppression de la table temporaire tmp_bio
        logger.info("Suppression de la table temporaire tmp_bio")
        target_cur.execute(
            """
            DROP TABLE IF EXISTS tmp_bio;
            """
        )
        target_conn.commit()

        # Réactivation des triggers
        reactivate_triggers(
            pg_cur=target_cur,
            pg_conn=target_conn,
            table_name=VisitOccurrence.table_name,
        )

    except Exception as e:
        logger.exception("Erreur pendant le chargement de measurement")
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
                logger.debug("Connexion source fermée.")
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
