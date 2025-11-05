from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from models.sql_object_base_model import SQLObjectBaseModel


@dataclass
class PatientDTO(SQLObjectBaseModel):

    def __init__(
        self,
        idpat: str,
        sexe: Optional[str],
        ddn: Optional[datetime],
    ):
        self.idpat = idpat
        self.sexe = sexe
        self.ddn = ddn

    @property
    def _values(self) -> List:
        """Liste des valeurs pour COPY"""
        return [
            self.idpat,
            self.sexe,
            self.ddn,
        ]

    @classmethod
    def _columns(cls) -> List[str]:
        """Colonnes correspondant à la requête"""
        return ["idpat", "sexe", "ddn"]
