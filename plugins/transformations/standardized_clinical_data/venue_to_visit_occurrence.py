import io
from models.omop.standardized_clinical_data.visit_occurrence import VisitOccurrence
from models.source.patient import PatientDTO
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


def load_visit_occurrence(source_hook, target_hook, truncate=False, batch_size=20_000):
    """Orchestre le transfert de venues vers la table OMOP visit_occurrence."""
    logger.info("Début du transfert venue → visit_occurrence")

    source_conn: PgConnection
    source_cur: PgCursor
    target_conn: PgConnection
    target_cur: PgCursor

    try:
        # Execute source query (open cursor, no fetch)
        source_conn, source_cur = get_cursor_by_sql_file(
            pg_hook=source_hook,
            batch_size=batch_size,
            sql_file_path="sql/standardized_clinical_data/visit_occurrence/get_rss.sql"
        )

        # Get target cursor (open cursor, no query)
        target_conn, target_cur = get_cursor_by_schema(
            pg_hook=target_hook, schema=VisitOccurrence.schema
        )

        # Création de la table temporaire tmp_person
        logger.info("Création de la table temporaire tmp_venue")
        target_cur.execute(
            """
            DROP TABLE IF EXISTS tmp_venue;
            CREATE TEMP TABLE tmp_venue (
                sej TEXT PRIMARY KEY,
                idpat TEXT,
                date_debut_venue DATE,
                date_fin_venue DATE,
                um_entree TEXT,
                mode_entree TEXT,
                mode_sortie TEXT,
                um_mode_hospitalisation TEXT
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


            # Transformer chaque ligne en objet VenueDTO
            venues = [VenueDTO(*row) for row in rows]
            for venue in venues :
                buffer.write("\t".join(venue.to_list()) + "\n") # renvoie les attributs de chaque DTO séparés par une tabulation ligne par ligne avec saut de ligne

            buffer.seek(0)    # ramène le curseur au début des résultats du buffer
            target_cur.copy_from(
                buffer,
                table="tmp_venue",  # destination des données
                sep="\t",            # Séparateur entre les valeurs → tabulation
                null="\\N",          # valeur nulle
                columns=VenueDTO._columns() # ordre des colonnes  à remplir
            )
            target_conn.commit()

            buffer.truncate(0) # vide le buffer
            buffer.seek(0)   # remet le curseur au  départ
            batch_num += 1  # compteur +1  à chaque nouveau batch
            logger.info(f"Batch {batch_num} chargé dans tmp_venue")

        # Manage source table
        deactivate_triggers(
            pg_cur=target_cur,
            pg_conn=target_conn,
            table_name=VisitOccurrence.table_name,
        )

        if truncate:
            truncate_table(
                pg_cur=target_cur,
                pg_conn=target_conn,
                table_name=VisitOccurrence.table_name,
            )

        logger.info("Insertion des venues dans la table OMOP visit_occurrence")
        insert_sql = f"""
        WITH visit_from_mapping as (
            SELECT
                src.concept_id AS source_concept_id,
                REPLACE(src.concept_code, '.', '') AS source_concept_code,
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
                tgt.domain_id = 'Visit'
                AND rel.relationship_id = 'Maps to'
                AND tgt.standard_concept = 'S'
                AND src.vocabulary_id = 'LV_VISIT_FROM'
        ),
        visit_to_mapping as (
            SELECT
                src.concept_id AS source_concept_id,
                REPLACE(src.concept_code, '.', '') AS source_concept_code,
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
                tgt.domain_id = 'Visit'
                AND rel.relationship_id = 'Maps to'
                AND tgt.standard_concept = 'S'
                AND src.vocabulary_id = 'LV_VISIT_TO'
        )
        INSERT INTO {VisitOccurrence.schema}.{VisitOccurrence.table_name}
        ({', '.join(VisitOccurrence._columns())})
        SELECT
            p.person_id                                 AS person_id,
            9201                                        AS visit_concept_id,
            tmp.date_debut_venue                        AS visit_start_date,
            NULL                                        AS visit_start_datetime,
            tmp.date_fin_venue                          AS visit_end_date,
            NULL                                        AS visit_end_datetime,
            32818                                       AS visit_type_concept_id,
            NULL                                        AS provider_id,
            NULL                                        AS care_site_id,
            tmp.sej                                     AS visit_source_value,
            NULL                                        AS visit_source_concept_id,
            COALESCE(vf.target_concept_id,0)            AS admitted_from_concept_id,
            tmp.mode_entree                             AS admitted_from_source_value,
            COALESCE(vt.target_concept_id,0)            AS discharged_to_concept_id,
            tmp.mode_sortie                             AS discharged_to_source_value,
            NULL                                        AS preceding_visit_occurrence_id
        FROM
           tmp_venue tmp
           LEFT JOIN {Person.schema}.{Person.table_name} p
           ON  tmp.idpat = p.person_source_value
           LEFT JOIN visit_from_mapping vf
           ON tmp.mode_entree = vf.source_concept_code
           LEFT JOIN visit_to_mapping vt
           ON tmp.mode_sortie = vt.source_concept_code
        RETURNING  visit_occurrence_id
        """

        target_cur.execute(insert_sql)
        inserted_count = len(target_cur.fetchall()) # nombre de lignes insérées
        target_conn.commit()

        logger.info(
            f"{inserted_count} nouvelles venues  insérées dans {VisitOccurrence.schema}.{VisitOccurrence.table_name}"
        )


       # MAJ colonne preceding visit_id
        update_sql = f"""
        UPDATE {VisitOccurrence.schema}.{VisitOccurrence.table_name} v
        SET preceding_visit_occurrence_id = sub.preceding_visit_occurrence_id
        FROM (
            SELECT
                visit_occurrence_id,
                LAG(visit_occurrence_id) OVER (
                    PARTITION BY person_id
                    ORDER BY visit_start_date
                ) AS preceding_visit_occurrence_id
            FROM {VisitOccurrence.schema}.{VisitOccurrence.table_name}
        ) sub
        WHERE v.visit_occurrence_id = sub.visit_occurrence_id;
        """

        logger.info("Mise à jour du champ preceding_visit_occurrence_id dans visit_occurrence")
        target_cur.execute(update_sql)
        target_conn.commit()





        # Suppression de la table temporaire tmp_person
        logger.info("Suppression de la table temporaire tmp_venue")
        target_cur.execute(
            """
            DROP TABLE IF EXISTS tmp_venue;
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
        logger.exception("Erreur pendant le chargement de visit_occurrence")
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
