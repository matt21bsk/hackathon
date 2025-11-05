from typing import Optional, List
from datetime import date
from omop_base_model import OmopBaseModel


class SourceToConceptMap(OmopBaseModel):
    table_name = "source_to_concept_map"

    def __init__(
        self,
        source_code: str,
        source_concept_id: int,
        source_vocabulary_id: str,
        source_code_description: Optional[str],
        target_concept_id: int,
        target_vocabulary_id: str,
        valid_start_date: date,
        valid_end_date: date,
        invalid_reason: Optional[str] = None,
    ):
        self.source_code = source_code
        self.source_concept_id = source_concept_id
        self.source_vocabulary_id = source_vocabulary_id
        self.source_code_description = source_code_description
        self.target_concept_id = target_concept_id
        self.target_vocabulary_id = target_vocabulary_id
        self.valid_start_date = valid_start_date
        self.valid_end_date = valid_end_date
        self.invalid_reason = invalid_reason

    # Liste ordonnée des valeurs pour COPY ou INSERT
    @property
    def _values(self) -> List:
        return [
            self.source_code,
            self.source_concept_id,
            self.source_vocabulary_id,
            self.source_code_description,
            self.target_concept_id,
            self.target_vocabulary_id,
            self.valid_start_date,
            self.valid_end_date,
            self.invalid_reason,
        ]

    # Liste ordonnée des colonnes correspondant à la table SQL
    @classmethod
    def _columns(cls) -> List[str]:
        return [
            "source_code",
            "source_concept_id",
            "source_vocabulary_id",
            "source_code_description",
            "target_concept_id",
            "target_vocabulary_id",
            "valid_start_date",
            "valid_end_date",
            "invalid_reason",
        ]
