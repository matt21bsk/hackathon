from pathlib import Path
import csv
from psycopg2.extras import execute_values
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor
from models.omop.standardized_vocabularies.concept import Concept
from models.omop.standardized_vocabularies.concept_relationship import (
    ConceptRelationship,
)
from models.omop.standardized_vocabularies.source_to_concept_map import (
    SourceToConceptMap,
)
from utils.logger import get_logger
from utils.db_utils import (
    get_cursor_by_schema,
    deactivate_triggers,
    reactivate_triggers,
)

logger = get_logger(__name__)


def load_mappings(target_hook, vocabulary_name, mapping_csv_path):
    """
    Charge les mappings depuis un fichier csv
    et insère dans :
      - omop.source_to_concept_map
      - omop.concept_relationship ('Maps to' / 'Is mapped to')
    """
    logger.info(f"Chargement des mappings depuis {mapping_csv_path}")

    target_conn: PgConnection
    target_cur: PgCursor

    try:
        target_conn, target_cur = get_cursor_by_schema(
            pg_hook=target_hook, schema=Concept.schema
        )

        for table in [ConceptRelationship.table_name, SourceToConceptMap.table_name]:
            deactivate_triggers(
                pg_cur=target_cur, pg_conn=target_conn, table_name=table
            )

        csv_path = Path(mapping_csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"Fichier mapping introuvable : {csv_path}")

        # Lecture du CSV
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            mappings = [
                {
                    k.strip(): v.strip().strip('"') if v is not None else None
                    for k, v in row.items()
                }
                for row in reader
            ]

        if not mappings:
            logger.warning("Aucun mapping trouvé dans le CSV.")
            return

        # Créer table temporaire CSV
        target_cur.execute(
            """
            CREATE TEMP TABLE tmp_mappings (
                source_concept TEXT,
                source_vocabulary_id TEXT,
                target_concept_id INT,
                target_vocabulary_id TEXT
            ) ON COMMIT DROP;
        """
        )
        pairs = [
            (
                m["source_concept"],
                m["vocabulary_id"],
                m["target_concept_id"],
                m["target_vocabulary_id"],
            )
            for m in mappings
        ]
        execute_values(
            target_cur,
            """
            INSERT INTO tmp_mappings (
                source_concept,
                source_vocabulary_id,
                target_concept_id,
                target_vocabulary_id
            ) VALUES %s""",
            pairs,
        )

        # Récupérer concept_id des sources via JOIN
        target_cur.execute(
            f"""
            SELECT
                t.source_concept,
                t.source_vocabulary_id,
                t.target_concept_id,
                t.target_vocabulary_id,
                c.concept_id AS source_concept_id
            FROM
                tmp_mappings t
                JOIN {Concept.schema}.{Concept.table_name} c
                    ON c.concept_code = t.source_concept
                    AND c.vocabulary_id = t.source_vocabulary_id
        """
        )
        rows_with_ids = target_cur.fetchall()

        if not rows_with_ids:
            logger.warning("Aucun concept local trouvé pour les mappings CSV.")
            return

        # Créer table temporaire pour source_to_concept_map
        target_cur.execute(
            """
            CREATE TEMP TABLE tmp_source_to_concept_map (
                source_code TEXT,
                source_concept_id INT,
                source_vocabulary_id TEXT,
                target_concept_id INT,
                target_vocabulary_id TEXT
            ) ON COMMIT DROP;
        """
        )
        stm_pairs = [(r[0], r[4], r[1], r[2], r[3]) for r in rows_with_ids]
        execute_values(
            target_cur,
            """
            INSERT INTO tmp_source_to_concept_map (
                source_code,
                source_concept_id,
                source_vocabulary_id,
                target_concept_id,
                target_vocabulary_id
            ) VALUES %s
            """,
            stm_pairs,
        )

        # Insérer uniquement les mappings qui n'existent pas encore
        target_cur.execute(
            f"""
            INSERT INTO {SourceToConceptMap.schema}.{SourceToConceptMap.table_name} (
                {', '.join(SourceToConceptMap._columns())}
            )
            SELECT
                t.source_code,
                t.source_concept_id,
                t.source_vocabulary_id,
                NULL,  -- source_code_description
                t.target_concept_id,
                t.target_vocabulary_id,
                '2020-01-01',  -- valid_start_date
                '2099-12-31',  -- valid_end_date
                NULL           -- invalid_reason
            FROM
                tmp_source_to_concept_map t
                LEFT JOIN {SourceToConceptMap.schema}.{SourceToConceptMap.table_name} stm
                    ON stm.source_concept_id = t.source_concept_id
                    AND stm.target_concept_id = t.target_concept_id
            WHERE
                stm.source_concept_id IS NULL
        """
        )

        # Créer table temporaire pour concept_relationship
        target_cur.execute(
            """
            CREATE TEMP TABLE tmp_concept_relationships (
                concept_id_1 INT,
                concept_id_2 INT,
                relationship_id TEXT
            ) ON COMMIT DROP;
        """
        )

        rel_pairs = []
        for r in rows_with_ids:
            source_id = r[4]
            target_id = r[2]
            rel_pairs.append((source_id, target_id, "Maps to"))
            rel_pairs.append((target_id, source_id, "Is mapped to"))

        execute_values(
            target_cur,
            """
            INSERT INTO tmp_concept_relationships (
                concept_id_1,
                concept_id_2,
                relationship_id
            ) VALUES %s
            """,
            rel_pairs,
        )

        # Insérer uniquement les relations qui n'existent pas
        target_cur.execute(
            f"""
            INSERT INTO {ConceptRelationship.schema}.{ConceptRelationship.table_name} (
                {', '.join(ConceptRelationship._columns())}
            )
            SELECT
                t.concept_id_1,
                t.concept_id_2,
                t.relationship_id,
                '2020-01-01',  -- valid_start_date
                '2099-12-31',  -- valid_end_date
                NULL           -- invalid_reason
            FROM
                tmp_concept_relationships t
                LEFT JOIN {ConceptRelationship.schema}.{ConceptRelationship.table_name} cr
                    ON cr.concept_id_1 = t.concept_id_1
                    AND cr.concept_id_2 = t.concept_id_2
                    AND cr.relationship_id = t.relationship_id
            WHERE
                cr.concept_id_1 IS NULL
        """
        )

        # Réactiver les triggers
        for table in [ConceptRelationship.table_name, SourceToConceptMap.table_name]:
            reactivate_triggers(
                pg_cur=target_cur, pg_conn=target_conn, table_name=table
            )

        logger.info(f"{len(stm_pairs)} mappings traités dans source_to_concept_map")
        logger.info(f"{len(rel_pairs)} relations traitées dans concept_relationship")

    except Exception as e:
        logger.exception(
            f"Erreur pendant le chargement des mappings de {vocabulary_name}"
        )
        target_conn.rollback()
        raise

    finally:
        try:
            target_cur.close()
        except Exception:
            pass
        try:
            target_conn.close()
        except Exception:
            pass
