from typing import Optional, Dict
from datetime import datetime
from datetime import date
from omop_base_model import OmopBaseModel


class VisitOccurrence(OmopBaseModel):
    table_name = "visit_occurrence"

    def __init__(
        self,
        visit_occurrence_id: int,
        person_id: int,
        visit_start_date: date,
        visit_start_datetime: Optional[int],
        visit_end_date: date,
        visit_end_date_time: Optional[datetime],
        visit_concept_id: int = 0,
        visit_type_concept_id: int = 0,
        provider_id: Optional[int] = None,
        care_site_id: Optional[int] = None,
        visit_source_value: Optional[str] = None,
        visit_source_concept_id: Optional[int] = None,
        admitted_from_concept_id: Optional[int] = None,
        admitted_from_source_value: Optional[str] = None,
        discharged_to_concept_id: Optional[int] = None,
        discharged_to_source_value: Optional[str] = None,
        preceding_visit_occurrence_id: Optional[int] = None
    ):
        self.visit_occurrence_id = visit_occurrence_id
        self.person_id = person_id
        self.visit_concept_id = visit_concept_id
        self.visit_start_date = visit_start_date
        self.visit_start_datetime = visit_start_datetime
        self.visit_end_date = visit_end_date
        self.visit_end_date_time = visit_end_date_time
        self.visit_type_concept_id= visit_type_concept_id
        self.provider_id = provider_id
        self.care_site_id = care_site_id
        self.visit_source_value = visit_source_value
        self.visit_source_concept_id = visit_source_concept_id
        self.admitted_from_concept_id= admitted_from_concept_id
        self.admitted_from_source_value= admitted_from_source_value
        self.discharged_to_concept_id = discharged_to_concept_id
        self.discharged_to_source_value = discharged_to_source_value
        self.preceding_visit_occurrence_id = preceding_visit_occurrence_id

    @property # pour appeler la méthode sans parenthèses
    def _values(self):
        """Liste des valeurs pour COPY"""
        return [
            self.visit_occurrence_id,
            self.person_id,
            self.visit_concept_id,
            self.visit_start_date,
            self.visit_start_datetime ,
            self.visit_end_date,
            self.visit_end_date_time,
            self.visit_type_concept_id,
            self.provider_id,
            self.care_site_id,
            self.visit_source_value,
            self.visit_source_concept_id,
            self.admitted_from_concept_id,
            self.admitted_from_source_value,
            self.discharged_to_concept_id,
            self.discharged_to_source_value,
            self.preceding_visit_occurrence_id
        ]

    @classmethod # méthode de classe
    def _columns(cls):
        """Colonnes OMOP correspondant à la table visit_occurrence"""
        return [
            "person_id",
            "visit_concept_id",
            "visit_start_date",
            "visit_start_datetime",
            "visit_end_date",
            "visit_end_datetime",
            "visit_type_concept_id",
            "provider_id",
            "care_site_id",
            "visit_source_value",
            "visit_source_concept_id",
            "admitted_from_concept_id",
            "admitted_from_source_value",
            "discharged_to_concept_id",
            "discharged_to_source_value",
            "preceding_visit_occurrence_id"
        ]
