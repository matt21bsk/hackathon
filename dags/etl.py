import datetime
import pendulum
from airflow.sdk import dag, Param, TaskGroup
from airflow.sdk.bases.operator import chain
from operators.standardized_clinical_data.person import PersonLoaderOperator
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
    dag_id="omop_etl_dag",
    schedule="0 0 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    max_active_runs=1,
    params={
        "truncate": Param(default=True, type="boolean"),
        "batch_size": Param(default=20_000, type="integer"),
    },
)
def OmopEtlDag():

    # Load gender vocabulary, concept and mappings
    with TaskGroup(
        "gender_loader", tooltip="Load gender vocabulary, concepts, and mappings"
    ) as gender_group:
        gender_vocabulary_loader = VocabularyLoaderOperator(
            task_id="load_gender_vocabulary",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_GENDER",
            vocabulary_sql_file_path="sql/standardized_vocabularies/person/gender_vocabulary.sql",
            batch_size="{{ params.batch_size }}",
        )

        gender_concept_loader = ConceptLoaderOperator(
            task_id="load_gender_concept",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_GENDER",
            concept_domain_id="Gender",
            concept_sql_file_path="sql/standardized_vocabularies/person/gender_concept.sql",
            batch_size="{{ params.batch_size }}",
        )

        gender_mapping_loader = MappingLoaderOperator(
            task_id="load_gender_mapping",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_GENDER",
            mapping_csv_path="mappings/gender_mapping.csv",
        )

        chain(gender_vocabulary_loader, gender_concept_loader, gender_mapping_loader)

    # Load person
    person_loader = PersonLoaderOperator(
        task_id="load_patients",
        source_conn_id="hackathon_source",
        target_conn_id="hackathon_target",
        truncate="{{ params.truncate }}",
        batch_size="{{ params.batch_size }}",
    )

    chain(gender_group, person_loader)


dag = OmopEtlDag()
