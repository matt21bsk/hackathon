from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from transformations.standardized_vocabularies.mapping import (
    load_mappings,
)


class MappingLoaderOperator(BaseOperator):
    def __init__(
        self,
        target_conn_id,
        vocabulary_name,
        mapping_csv_path,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.target_conn_id = target_conn_id
        self.vocabulary_name = vocabulary_name
        self.mapping_csv_path = mapping_csv_path

    def execute(self, context):
        target_hook = PostgresHook(postgres_conn_id=self.target_conn_id)

        load_mappings(
            target_hook=target_hook,
            vocabulary_name=self.vocabulary_name,
            mapping_csv_path=self.mapping_csv_path,
        )
