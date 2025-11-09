from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from models.sql_object_base_model import SQLObjectBaseModel


@dataclass
class DiagDTO(SQLObjectBaseModel):

    def __init__(
        self,
        idpat: str,
        sej: Optional[str],
        date_debut_venue: Optional[datetime],
        date_fin_venue: Optional[datetime],
        diag: Optional[str],
        rss_type_diagnostic: Optional[str]


    ):
        self.idpat = idpat
        self.sej = sej
        self.date_debut_venue = date_debut_venue
        self.date_fin_venue = date_fin_venue
        self.diag = diag
        self.rss_type_diagnostic = rss_type_diagnostic

    @property
    def _values(self) -> List:
        """Liste des valeurs pour COPY"""
        return [
            self.idpat,
            self.sej,
            self.date_debut_venue,
            self.date_fin_venue,
            self.diag,
            self.rss_type_diagnostic
        ]

    @classmethod
    def _columns(cls) -> List[str]:
        """Colonnes correspondant à la requête pour l'insertion depuis le fichier sql dans la table temporaire"""
        return ["idpat", "sej", "date_debut_venue", "date_fin_venue", "diag", "rsstypediagnostic"]
