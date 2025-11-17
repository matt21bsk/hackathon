from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from models.sql_object_base_model import SQLObjectBaseModel


@dataclass
class ActeCim10DTO(SQLObjectBaseModel):

    def __init__(
        self,
        idpat: str,
        sej: str,
        diag: str,
        date_acte: Optional[datetime]

     ):
        self.idpat = idpat
        self.sej = sej
        self.diag = diag
        self.date_acte = date_acte

    @property
    def _values(self) -> List:
        """Liste des valeurs pour COPY"""
        return [
            self.idpat,
            self.sej,
            self.diag,
            self.date_acte
        ]

    @classmethod
    def _columns(cls) -> List[str]:
        """Colonnes correspondant à la requête pour l'insertion depuis le fichier sql dans la table temporaire"""
        return ["idpat", "sej", "diag","date_acte"]
