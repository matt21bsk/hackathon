from typing import Optional, List
from datetime import date
from omop_base_model import OmopBaseModel


class Concept(OmopBaseModel):
    table_name = "concept"

    def __init__(
        self,
        concept_id: int,
        concept_name: str,
        domain_id: str,
        vocabulary_id: str,
        concept_class_id: str,
        standard_concept: Optional[str] = None,
        concept_code: Optional[str] = None,
        valid_start_date: Optional[date] = None,
        valid_end_date: Optional[date] = None,
        invalid_reason: Optional[str] = None,
    ):
        self.concept_id = concept_id
        self.concept_name = concept_name
        self.domain_id = domain_id
        self.vocabulary_id = vocabulary_id
        self.concept_class_id = concept_class_id
        self.standard_concept = standard_concept
        self.concept_code = concept_code
        self.valid_start_date = valid_start_date
        self.valid_end_date = valid_end_date
        self.invalid_reason = invalid_reason

    # Liste ordonnée des valeurs pour COPY ou INSERT
    @property
    def _values(self) -> List:
        return [
            self.concept_id,
            self.concept_name,
            self.domain_id,
            self.vocabulary_id,
            self.concept_class_id,
            self.standard_concept,
            self.concept_code,
            self.valid_start_date,
            self.valid_end_date,
            self.invalid_reason,
        ]

    # Liste ordonnée des colonnes correspondant à la table SQL
    @classmethod
    def _columns(cls) -> List[str]:
        return [
            "concept_id",
            "concept_name",
            "domain_id",
            "vocabulary_id",
            "concept_class_id",
            "standard_concept",
            "concept_code",
            "valid_start_date",
            "valid_end_date",
            "invalid_reason",
        ]
