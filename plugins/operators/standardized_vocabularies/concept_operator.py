from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from transformations.standardized_vocabularies.concept import (
    load_concepts,
)


class ConceptLoaderOperator(BaseOperator):
    template_fields = "batch_size"

    def __init__(
        self,
        source_conn_id,
        target_conn_id,
        vocabulary_name,
        concept_domain_id,
        concept_class_id,
        concept_sql_file_path,
        batch_size: int | str = 20_000,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source_conn_id = source_conn_id
        self.target_conn_id = target_conn_id
        self.vocabulary_name = vocabulary_name
        self.concept_domain_id = concept_domain_id
        self.concept_class_id = concept_class_id
        self.concept_sql_file_path = concept_sql_file_path
        self.batch_size = batch_size

    def execute(self, context):
        source_hook = PostgresHook(postgres_conn_id=self.source_conn_id)
        target_hook = PostgresHook(postgres_conn_id=self.target_conn_id)

        load_concepts(
            source_hook=source_hook,
            target_hook=target_hook,
            vocabulary_name=self.vocabulary_name,
            concept_domain_id=self.concept_domain_id,
            concept_class_id=self.concept_class_id,
            sql_file_path=self.concept_sql_file_path,
            batch_size=int(self.batch_size),
        )
