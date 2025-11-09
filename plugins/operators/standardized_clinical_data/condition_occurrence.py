from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from transformations.standardized_clinical_data.diag_to_condition_occurrence import (
    load_condition_occurrence
)


class ConditionOccurrenceLoaderOperator(BaseOperator):
    template_fields = ("truncate", "batch_size")

    def __init__(
        self,
        source_conn_id,
        target_conn_id,
        truncate: int | str = False,
        batch_size: int | str = 20_000,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source_conn_id = source_conn_id
        self.target_conn_id = target_conn_id
        self.truncate = truncate
        self.batch_size = batch_size

    def execute(self, context):
        source_hook = PostgresHook(postgres_conn_id=self.source_conn_id)
        target_hook = PostgresHook(postgres_conn_id=self.target_conn_id)

        load_condition_occurrence(
            source_hook,
            target_hook,
            truncate=str(self.truncate).lower() in ("true", "1"),
            batch_size=int(self.batch_size),
        )
