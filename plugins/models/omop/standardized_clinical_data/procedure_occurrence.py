from typing import Optional, Dict
from datetime import datetime
from datetime import date
from omop_base_model import OmopBaseModel


class ProcedureOccurrence(OmopBaseModel):
    table_name = "procedure_occurrence"

    def __init__(
        self,
        procedure_occurrence_id: int,
        person_id: int,
        procedure_concept_id: int,
        procedure_date: date,
        procedure_type_concept_id: int,
        visit_occurrence__id: int,
        procedure_source_value: Optional[int] = None,
        procedure_source_concept_id: Optional[int] = None

    ):
        self.procedure_occurrence_id = procedure_occurrence_id
        self.person_id = person_id
        self.procedure_concept_id = procedure_concept_id
        self.procedure_date = procedure_date
        self.procedure_type_concept_id = procedure_type_concept_id
        self.visit_occurrence_id = visit_occurrence__id
        self.procedure_source_value = procedure_source_value
        self.procedure_source_concept_id = procedure_source_concept_id


    @property # pour appeler la méthode sans parenthèses
    def _values(self):
        """Liste des valeurs pour COPY"""
        return [
            self.procedure_occurrence_id,
            self.person_id,
            self.procedure_concept_id,
            self.procedure_date,
            self.procedure_type_concept_id,
            self.visit_occurrence_id,
            self.procedure_source_value,
            self.procedure_source_concept_id
        ]

    @classmethod # méthode de classe
    def _columns(cls):
        """Colonnes OMOP correspondant à la table visit_occurrence"""
        return [
            "person_id",
            "procedure_concept_id",
            "procedure_date",
            "procedure_type_concept_id",
            "visit_occurrence_id",
            "visit_detail_id",
            "procedure_source_value",
            "procedure_source_concept_id"
        ]
