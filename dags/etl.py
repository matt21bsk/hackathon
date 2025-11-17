import datetime
from fastapi import params
from operators.standardized_clinical_data.measurement import MeasurementLoaderOperator
import pendulum
from airflow.sdk import dag, Param, TaskGroup
from airflow.sdk.bases.operator import chain
from operators.standardized_clinical_data.condition_occurrence import ConditionOccurrenceLoaderOperator
from operators.standardized_clinical_data.person import PersonLoaderOperator
from operators.standardized_clinical_data.procedure_occurrence import ProcedureOccurrenceLoaderOperator
from operators.standardized_clinical_data.visit_occurrence import VisitOccurrenceLoaderOperator
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
            task_id="load_local_gender_vocabulary",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_GENDER",
            vocabulary_sql_file_path="sql/standardized_vocabularies/person/gender_vocabulary.sql",
            batch_size="{{ params.batch_size }}"
        )

        gender_concept_loader = ConceptLoaderOperator(
            task_id="load_local_gender_concept",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_GENDER",
            concept_domain_id="Gender",
            concept_class_id="Gender",
            concept_sql_file_path="sql/standardized_vocabularies/person/gender_concept.sql",
            batch_size="{{ params.batch_size }}"
        )

        gender_mapping_loader = MappingLoaderOperator(
            task_id="load_gender_mapping",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_GENDER",
            mapping_csv_path="mappings/gender_mapping.csv"
        )

        chain(gender_vocabulary_loader, gender_concept_loader, gender_mapping_loader)



    # Load diagnostic type vocabulary, concept and mappings
    with TaskGroup(
        "diagnostic_type_loader", tooltip="Load diagnosic type vocabulary, concepts, and mappings"
    ) as diagnostic_type_group:
        diagnostic_type_vocabulary_loader = VocabularyLoaderOperator(
            task_id="load_local_diagnostic_type_vocabulary",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_DIAGNOSTIC_TYPE",
            vocabulary_sql_file_path="sql/standardized_vocabularies/condition_occurrence/diagnostic_type_vocabulary.sql",
            batch_size="{{ params.batch_size }}"
        )

        diagnostic_type_concept_loader = ConceptLoaderOperator(
            task_id="load_local_vocabulary_concept",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_DIAGNOSTIC_TYPE",
            concept_domain_id="Diagnostic type",
            concept_class_id="Diagnostic type",
            concept_sql_file_path="sql/standardized_vocabularies/condition_occurrence/diagnostic_type_concept.sql",
            batch_size="{{ params.batch_size }}"
        )

        diagnostic_type_mapping_loader = MappingLoaderOperator(
            task_id="load_diagnostic_type_mapping",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_DIAGNOSTIC_TYPE",
            mapping_csv_path="mappings/diagnostic_type_mapping.csv"
        )

        chain(diagnostic_type_vocabulary_loader, diagnostic_type_concept_loader, diagnostic_type_mapping_loader)


    # Load local cim10 vocabulary and concept
    with TaskGroup(
        "local_cim10_loader", tooltip="Load cim10 vocabulary, concepts"
    ) as local_cim10_group:
        local_cim10_vocabulary_loader = VocabularyLoaderOperator(
            task_id="load_local_cim10_vocabulary",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_CIM10",
            vocabulary_sql_file_path="sql/standardized_vocabularies/condition_occurrence/local_cim10_vocabulary.sql",
            batch_size="{{ params.batch_size }}"
        )

        local_cim10_concept_loader = ConceptLoaderOperator(
            task_id="load_local_cim10_concept",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_CIM10",
            concept_domain_id="Condition",
            concept_class_id="CIM 10 code",
            concept_sql_file_path="sql/standardized_vocabularies/condition_occurrence/local_cim10_concept.sql",
            batch_size="{{ params.batch_size }}"
        )

        chain(local_cim10_vocabulary_loader, local_cim10_concept_loader)

    # Load local unit vocabulary and concept
    with TaskGroup(
        "local_unit_loader", tooltip="Load unit vocabulary, concepts"
    ) as local_unit_group:
        local_unit_vocabulary_loader = VocabularyLoaderOperator(
            task_id="load_local_unit_vocabulary",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_UNIT",
            vocabulary_sql_file_path="sql/standardized_vocabularies/measurement/unit_vocabulary.sql",
            batch_size="{{ params.batch_size }}"
        )

        local_unit_concept_loader = ConceptLoaderOperator(
            task_id="load_local_unit_concept",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_UNIT",
            concept_domain_id="Unit",
            concept_class_id="Unit",
            concept_sql_file_path="sql/standardized_vocabularies/measurement/unit_concept.sql",
            batch_size="{{ params.batch_size }}"
        )

        unit_mapping_loader = MappingLoaderOperator(
            task_id="load_unit_mapping",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_UNITS",
            mapping_csv_path="mappings/mapping_unit.csv",
        )


        chain(local_unit_vocabulary_loader, local_unit_concept_loader, unit_mapping_loader)

    # Load measurement vocabulary, concept and mappings

    with TaskGroup(
        "measurement_loader", tooltip="Load measurement vocabulary, concepts, and mappings"
    ) as measurement_group:
        measurement_vocabulary_loader = VocabularyLoaderOperator(
            task_id="load_measurement_vocabulary",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_MEASUREMENT",
            vocabulary_sql_file_path="sql/standardized_vocabularies/measurement/measurement_vocabulary.sql",
            batch_size="{{ params.batch_size }}",
        )

        measurement_concept_loader = ConceptLoaderOperator(
            task_id="load_measurement_concept",
            source_conn_id="hackathon_source",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_MEASUREMENT",
            concept_domain_id="Measurement",
            concept_class_id="Lab Test",
            concept_sql_file_path="sql/standardized_vocabularies/measurement/measurement_concept.sql",
            batch_size="{{ params.batch_size }}",
        )

        measurement_mapping_loader = MappingLoaderOperator(
            task_id="load_measurement_mapping",
            target_conn_id="hackathon_target",
            vocabulary_name="LV_MEASUREMENT",
            mapping_csv_path="mappings/measurement_mapping.csv",
        )

        chain(measurement_vocabulary_loader, measurement_concept_loader, measurement_mapping_loader)

    # Load person
    person_loader = PersonLoaderOperator(
        task_id="load_patients",
        source_conn_id="hackathon_source",
        target_conn_id="hackathon_target",
        truncate="{{ params.truncate }}",
        batch_size="{{ params.batch_size }}"
    )

   # Load Visit_occurrence
    visit_occurrence_loader = VisitOccurrenceLoaderOperator(
        task_id="load_visit_occurrence",
        source_conn_id="hackathon_source",
        target_conn_id="hackathon_target",
        truncate="{{ params.truncate }}",
        batch_size="{{ params.batch_size }}"
    )

    #Load condition_occurrence
    condition_occurrence_loader = ConditionOccurrenceLoaderOperator(
        task_id="load_condition_occurrence",
        source_conn_id="hackathon_source",
        target_conn_id="hackathon_target",
        truncate="{{ params.truncate }}",
        batch_size="{{ params.batch_size }}"
    )

   #Load procedure_occurrence
    procedure_occurrence_loader = ProcedureOccurrenceLoaderOperator(
       task_id = "load_procedure_occurrence",
       source_conn_id="hackathon_source",
       target_conn_id="hackathon_target",
       truncate= "{{params.truncate}}",
       batch_size ="{{params.batch_size}}"
   )

    #Load measurement
    measurement_loader = MeasurementLoaderOperator(
        task_id="load_measurement",
        source_conn_id="hackathon_source",
        target_conn_id="hackathon_target",
        truncate="{{ params.truncate }}",
        batch_size="{{ params.batch_size }}"
    )
   #

    #parallel tasks
    parallel_tasks=[condition_occurrence_loader, procedure_occurrence_loader, measurement_loader]


    chain(gender_group, diagnostic_type_group, local_cim10_group, measurement_group, local_unit_group, person_loader, visit_occurrence_loader, parallel_tasks)


dag = OmopEtlDag()
