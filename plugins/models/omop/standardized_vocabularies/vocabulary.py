from typing import Optional, List
from omop_base_model import OmopBaseModel


class Vocabulary(OmopBaseModel):
    table_name = "vocabulary"

    def __init__(
        self,
        vocabulary_id: str,
        vocabulary_name: str,
        vocabulary_reference: Optional[str] = None,
        vocabulary_version: Optional[str] = None,
        vocabulary_concept_id: int = 0,
    ):
        self.vocabulary_id = vocabulary_id
        self.vocabulary_name = vocabulary_name
        self.vocabulary_reference = vocabulary_reference
        self.vocabulary_version = vocabulary_version
        self.vocabulary_concept_id = vocabulary_concept_id

    # Liste ordonnée des valeurs pour COPY
    @property
    def _values(self) -> List:
        return [
            self.vocabulary_id,
            self.vocabulary_name,
            self.vocabulary_reference,
            self.vocabulary_version,
            self.vocabulary_concept_id,
        ]

    # Liste ordonnée des colonnes (correspondance exacte à la table SQL)
    @classmethod
    def _columns(cls) -> List[str]:
        return [
            "vocabulary_id",
            "vocabulary_name",
            "vocabulary_reference",
            "vocabulary_version",
            "vocabulary_concept_id",
        ]
