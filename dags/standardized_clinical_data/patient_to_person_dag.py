import datetime
import pendulum
from airflow.sdk import dag, task, Param
from operators.standardized_clinical_data.person import PersonLoaderOperator


@dag(
    dag_id="patient_to_person_dag",
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
def PatientToPersonDag():

    person_loader = PersonLoaderOperator(
        task_id="load_patients",
        source_conn_id="hackathon_source",
        target_conn_id="hackathon_target",
        truncate="{{ params.truncate }}",
        batch_size="{{ params.batch_size }}",
    )

    person_loader


dag = PatientToPersonDag()
