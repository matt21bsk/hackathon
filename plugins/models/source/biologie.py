from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from models.sql_object_base_model import SQLObjectBaseModel


@dataclass
class BiologieDTO(SQLObjectBaseModel):

    def __init__(
        self,
        idpat: str,
        sej: str,
        date_result: Optional[datetime],
        value: Optional[float],
        unit_name : Optional[str],
        norm_lower: Optional[float],
        norm_upper: Optional[float],
        source_concept: Optional[str],
        verbatim: Optional[str]
    ):
        self.idpat= idpat
        self.sej=sej
        self.date_result=date_result
        self.value=value
        self.unit_name=unit_name
        self.norm_lower=norm_lower
        self.norm_upper=norm_upper
        self.source_concept=source_concept
        self.verbatim=verbatim

    @property
    def _values(self) -> List:
        """Liste des valeurs pour COPY"""
        return [
        self.idpat,
        self.sej,
        self.date_result,
        self.value,
        self.unit_name,
        self.norm_lower,
        self.norm_upper,
        self.source_concept,
        self.verbatim
        ]

    @classmethod
    def _columns(cls) -> List[str]:
        """Colonnes correspondant à la requête"""
        return [
        "idpat",
        "sej",
        "date_result",
        "value",
        "unit_name",
        "norm_lower",
        "norm_upper",
        "source_concept_name",
        "verbatim"
        ]
