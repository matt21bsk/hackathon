from typing import Optional, List
from datetime import date
from omop_base_model import OmopBaseModel


class ConceptRelationship(OmopBaseModel):
    table_name = "concept_relationship"

    def __init__(
        self,
        concept_id_1: int,
        concept_id_2: int,
        relationship_id: str,
        valid_start_date: date,
        valid_end_date: date,
        invalid_reason: Optional[str] = None,
    ):
        self.concept_id_1 = concept_id_1
        self.concept_id_2 = concept_id_2
        self.relationship_id = relationship_id
        self.valid_start_date = valid_start_date
        self.valid_end_date = valid_end_date
        self.invalid_reason = invalid_reason

    # Liste ordonnée des valeurs pour COPY ou INSERT
    @property
    def _values(self) -> List:
        return [
            self.concept_id_1,
            self.concept_id_2,
            self.relationship_id,
            self.valid_start_date,
            self.valid_end_date,
            self.invalid_reason,
        ]

    # Liste ordonnée des colonnes correspondant à la table SQL
    @classmethod
    def _columns(cls) -> List[str]:
        return [
            "concept_id_1",
            "concept_id_2",
            "relationship_id",
            "valid_start_date",
            "valid_end_date",
            "invalid_reason",
        ]
