import datetime
import pendulum
from airflow.sdk import dag, task
from airflow.sdk.bases.operator import chain
from operators.standardized_vocabularies.vocabulary_operator import (
    VocabularyLoaderOperator,
)
from operators.standardized_vocabularies.concept_operator import (
    ConceptLoaderOperator,
)
from operators.standardized_vocabularies.mapping_operator import (
    MappingLoaderOperator,
)


@dag(
    dag_id="standardized_vocabularies_dag",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    max_active_runs=1,
)
def VocabularyDag():

    gender_vocabulary_loader = VocabularyLoaderOperator(
        task_id="load_gender_vocabulary",
        source_conn_id="hackathon_source",
        target_conn_id="hackathon_target",
        vocabulary_name="LV_GENDER",
        vocabulary_sql_file_path="sql/standardized_vocabularies/person/gender_vocabulary.sql",
        batch_size=50_000,
    )

    gender_concept_loader = ConceptLoaderOperator(
        task_id="load_gender_concept",
        source_conn_id="hackathon_source",
        target_conn_id="hackathon_target",
        vocabulary_name="LV_GENDER",
        concept_domain_id="Gender",
        concept_class_id="Gender",
        concept_sql_file_path="sql/standardized_vocabularies/person/gender_concept.sql",
        batch_size=50_000,
    )

    gender_mapping_loader = MappingLoaderOperator(
        task_id="load_gender_mapping",
        target_conn_id="hackathon_target",
        vocabulary_name="LV_GENDER",
        mapping_csv_path="mappings/gender_mapping.csv",
    )

    chain(gender_vocabulary_loader, gender_concept_loader, gender_mapping_loader)


dag = VocabularyDag()
