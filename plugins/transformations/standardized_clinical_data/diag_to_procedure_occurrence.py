import io
from models.omop.standardized_clinical_data import condition_occurrence
from models.omop.standardized_clinical_data.condition_occurrence import ConditionOccurrence
from models.omop.standardized_clinical_data.procedure_occurrence import ProcedureOccurrence
from models.omop.standardized_clinical_data.visit_occurrence import VisitOccurrence
from models.source.acte_cim10 import ActeCim10DTO
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


def load_procedure_occurrence_from_diag(source_hook, target_hook, truncate=False, batch_size=20_000):
    """Orchestre le transfert des diagnostics vers la table OMOP procedure_occurrence."""
    logger.info("Début du transfert diag → procedure_occurrence")

    source_conn: PgConnection
    source_cur: PgCursor
    target_conn: PgConnection
    target_cur: PgCursor

    try:
        # Execute source query (open cursor, no fetch)
        source_conn, source_cur = get_cursor_by_sql_file(
            pg_hook=source_hook,
            batch_size=batch_size,
            sql_file_path="sql/standardized_clinical_data/procedure_occurrence/get_cim10_procedure.sql",
        )

        # Get target cursor (open cursor, no query)
        target_conn, target_cur = get_cursor_by_schema(
            pg_hook=target_hook, schema=ProcedureOccurrence.schema
        )

        # Création de la table temporaire tmp_diag
        logger.info("Création de la table temporaire tmp_diag")
        target_cur.execute(
            """
            DROP TABLE IF EXISTS tmp_diag;
            CREATE TEMP TABLE tmp_diag (
                idpat TEXT,
                sej TEXT,
                diag TEXT,
                date_acte DATE
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
            diags = [ActeCim10DTO(*row) for row in rows]
            for diag in diags :
                buffer.write("\t".join(diag.to_list()) + "\n") # renvoie les attributs de chaque DTO séparés par une tabulation ligne par ligne avec saut de ligne

            buffer.seek(0)    # ramène le curseur au début des résultats du buffer
            target_cur.copy_from(
                buffer,
                table="tmp_diag",  # destination des données
                sep="\t",            # Séparateur entre les valeurs → tabulation
                null="\\N",          # valeur nulle
                columns=ActeCim10DTO._columns() # ordre des colonnes  à remplir
            )
            target_conn.commit()

            buffer.truncate(0) # vide le buffer
            buffer.seek(0)   # remet le curseur au  départ
            batch_num += 1  # compteur +1  à chaque nouveau batch
            logger.info(f"Batch {batch_num} chargé dans tmp_diag")

        # Manage source table
        deactivate_triggers(
            pg_cur=target_cur,
            pg_conn=target_conn,
            table_name=ProcedureOccurrence.table_name,
        )

        if truncate:
            truncate_table(
                pg_cur=target_cur,
                pg_conn=target_conn,
                table_name=ProcedureOccurrence.table_name,
            )

        logger.info("Insertion des venues dans la table OMOP procedure_occurrence")
        insert_sql = f"""
         WITH cim10_mapping as (
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
                tgt.domain_id = 'Procedure'
                AND rel.relationship_id = 'Maps to'
                AND tgt.standard_concept = 'S'
                AND src.vocabulary_id = 'CIM10'
        )
        INSERT INTO {ProcedureOccurrence.schema}.{ProcedureOccurrence.table_name}
        ({', '.join(ProcedureOccurrence._columns())})
        SELECT
            v.person_id                                  AS person_id,
            COALESCE(cim.target_concept_id, 0)           AS preocedure_concept_id,
            tmp.date_acte                                AS procedure_date,
            32810                                        AS procedure_type_concept_id,
            V.visit_occurrence_id                        AS visit_occurrence_id,
            NULL                                         AS visit_detail_id,
            cim.source_concept_code                      AS procedure_source_value,
            cim.source_concept_id                        AS condition_source_concept_id
        FROM
           tmp_diag tmp
           JOIN {VisitOccurrence.schema}.{VisitOccurrence.table_name} v
           ON  tmp.sej = v.visit_source_value
           JOIN cim10_mapping cim
           ON tmp.diag = cim.source_concept_code
        RETURNING procedure_concept_id
        """

        target_cur.execute(insert_sql)
        inserted_count = len(target_cur.fetchall()) # nombre de lignes insérées
        target_conn.commit()

        logger.info(
            f"{inserted_count} nouveaux actes insérés dans {ProcedureOccurrence.schema}.{ProcedureOccurrence.table_name}"
        )


        # Suppression de la table temporaire tmp_diag
        logger.info("Suppression de la table temporaire tmp_diag")
        target_cur.execute(
            """
            DROP TABLE IF EXISTS tmp_diag;
            """
        )
        target_conn.commit()

        # Réactivation des triggers
        reactivate_triggers(
            pg_cur=target_cur,
            pg_conn=target_conn,
            table_name=ProcedureOccurrence.table_name,
        )

    except Exception as e:
        logger.exception("Erreur pendant le chargement de procedure_occurrence")
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
