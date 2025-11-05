import datetime
import pendulum
from airflow.sdk import dag, Param
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator


@dag(
    dag_id="omop_etl_trigger_dag",
    start_date=pendulum.datetime(2025, 10, 27, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=datetime.timedelta(minutes=120),
    params={
        "truncate": Param(default=True, type="boolean"),
        "batch_size": Param(default=20_000, type="integer"),
    },
)
def OmopEtlDag():

    # Déclenche le DAG des vocabulaires
    trigger_vocab = TriggerDagRunOperator(
        task_id="trigger_standardized_vocabularies",
        trigger_dag_id="standardized_vocabularies_dag",
        wait_for_completion=True,
    )

    # Déclenche le DAG patient → person
    trigger_patient = TriggerDagRunOperator(
        task_id="trigger_patient_to_person",
        trigger_dag_id="patient_to_person_dag",
        wait_for_completion=True,
    )

    # Ordre d'exécution : vocabulaire -> patient
    trigger_vocab >> trigger_patient


dag = OmopEtlDag()
