from typing import Optional, Dict
from datetime import datetime
from datetime import date
from omop_base_model import OmopBaseModel


class ConditionOccurrence(OmopBaseModel):
    table_name = "condition_occurrence"

    def __init__(
        self,
        condition_occurrence_id: int,
        person_id: int,
        condition_concept_id: int,
        visit_occurrence__id: int,
        condition_start_date: date,
        condition_end_date: date,
        condition_type_concept_id: int,
        condition_status_concept_id: int,
        provider_id: Optional[int] = None,
        visit_detail_id: Optional[int] = None,
        condition_source_concept_id: Optional[int] = None,
        condition_source_value: Optional[int] = None,
        condition_status_source_value: Optional[str] = None
    ):
        self.condition_occurrence_id = condition_occurrence_id
        self.person_id = person_id
        self.condition_concept_id = condition_concept_id
        self.visit_occurrence_id = visit_occurrence__id
        self.condition_start_date = condition_start_date
        self.condition_end_date = condition_end_date
        self.condition_type_concept_id = condition_type_concept_id
        self.condition_status_concept_id = condition_status_concept_id
        self.visit_detail_id= visit_detail_id
        self.provider_id = provider_id
        self.condition_source_concept_id=condition_source_concept_id
        self.condition_source_value = condition_source_value
        self.condition_status_source_value=condition_status_source_value


    @property # pour appeler la méthode sans parenthèses
    def _values(self):
        """Liste des valeurs pour COPY"""
        return [
            self.condition_occurrence_id,
            self.visit_occurrence_id,
            self.condition_concept_id,
            self.person_id,
            self.condition_start_date,
            self.condition_end_date,
            self.condition_type_concept_id,
            self.condition_status_concept_id ,
            self.provider_id,
            self.visit_detail_id,
            self.condition_source_concept_id,
            self.condition_source_value,
            self.condition_status_source_value
        ]

    @classmethod # méthode de classe
    def _columns(cls):
        """Colonnes OMOP correspondant à la table visit_occurrence"""
        return [
            "person_id",
            "condition_concept_id",
            "condition_start_date",
            "condition_end_date",
            "condition_type_concept_id",
            "condition_status_concept_id",
            "provider_id",
            "visit_occurrence_id",
            "visit_detail_id",
            "condition_source_value",
            "condition_source_concept_id",
            "condition_status_source_value"
        ]
