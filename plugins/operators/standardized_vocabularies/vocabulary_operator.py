from typing import Literal
from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from transformations.standardized_vocabularies.vocabulary import (
    load_vocabulary,
)


class VocabularyLoaderOperator(BaseOperator):
    template_fields = "batch_size"

    def __init__(
        self,
        source_conn_id,
        target_conn_id,
        vocabulary_name,
        vocabulary_sql_file_path,
        batch_size: int | str = 20_000,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source_conn_id = source_conn_id
        self.target_conn_id = target_conn_id
        self.vocabulary_name = vocabulary_name
        self.vocabulary_sql_file_path = vocabulary_sql_file_path
        self.batch_size = batch_size

    def execute(self, context):
        source_hook = PostgresHook(postgres_conn_id=self.source_conn_id)
        target_hook = PostgresHook(postgres_conn_id=self.target_conn_id)

        load_vocabulary(
            source_hook=source_hook,
            target_hook=target_hook,
            vocabulary_name=self.vocabulary_name,
            sql_file_path=self.vocabulary_sql_file_path,
            batch_size=int(self.batch_size),
        )
