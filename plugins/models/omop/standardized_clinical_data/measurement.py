from typing import Optional, Dict
from datetime import datetime
from datetime import date
from omop_base_model import OmopBaseModel


class Measurement(OmopBaseModel):
    table_name = "measurement"

    def __init__(
        self,
        measurement_id: int,
        person_id: int,
        measurement_concept_id: int,
        measurement_date: date,
        measurement_type_concept_id: int,
        value_as_number: float,
        unit_concept_id: int,
        range_low: float,
        range_high: float,
        visit_occurrence_id: int,
        measurement_source_value: str,
        measurement_source_concept_id: int,
        unit_source_value: str,
        unit_source_concept_id: int,
        value_source_value: str
    ):
        self.measurement_id= measurement_id
        self.person_id= person_id
        self.measurement_concept_id= measurement_concept_id
        self.measurement_date= measurement_date
        self.measurement_type_concept_id= measurement_type_concept_id
        self.value_as_number= value_as_number
        self.unit_concept_id=  unit_concept_id
        self.range_low= range_low
        self.range_high= range_high
        self.visit_occurrence_id= visit_occurrence_id
        self.measurement_source_value= measurement_source_value
        self.measurement_source_concept_id= measurement_source_concept_id
        self.unit_source_value= unit_source_value
        self.unit_source_concept_id= unit_source_concept_id
        self.value_source_value= value_source_value



    @property # pour appeler la méthode sans parenthèses
    def _values(self):
        """Liste des valeurs pour COPY"""
        return [
            self.measurement_id,
            self.person_id,
            self.measurement_concept_id,
            self.measurement_date,
            self.measurement_type_concept_id,
            self.value_as_number,
            self.unit_concept_id,
            self.range_low,
            self.range_high,
            self.visit_occurrence_id,
            self.measurement_source_value,
            self.measurement_source_concept_id,
            self.unit_source_value,
            self.unit_source_concept_id,
            self.value_source_value
        ]

    @classmethod # méthode de classe
    def _columns(cls):
        """Colonnes OMOP correspondant à la table measurement"""
        return [
            "person_id",
            "measurement_concept_id",
            "measurement_date",
            "measurement_type_concept_id",
            "value_as_number",
            "unit_concept_id",
            "range_low",
            "range_high",
            "visit_occurrence_id",
            "measurement_source_value",
            "measurement_source_concept_id",
            "unit_source_value",
            "unit_source_concept_id",
            "value_source_value"
        ]
