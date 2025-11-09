from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from models.sql_object_base_model import SQLObjectBaseModel


@dataclass
class VenueDTO(SQLObjectBaseModel):

    def __init__(
        self,
        idpat: Optional[str],
        sej: str,
        date_debut_venue: Optional[datetime],
        date_fin_venue: Optional[datetime],
        um_entree : Optional[str],
        um_mode_hospitalisation: Optional[str]
    ):
        self.sej = sej
        self.idpat = idpat
        self.date_debut_venue= date_debut_venue
        self.date_fin_venue= date_fin_venue
        self.um_entree = um_entree
        self.um_mode_hospitalisation = um_mode_hospitalisation

    @property
    def _values(self) -> List:
        """Liste des valeurs pour COPY"""
        return [
            self.sej,
            self.idpat,
            self.date_debut_venue,
            self.date_fin_venue,
            self.um_entree,
            self.um_mode_hospitalisation
        ]

    @classmethod
    def _columns(cls) -> List[str]:
        """Colonnes correspondant à la requête"""
        return [
            "sej",
            "idpat",
            "date_debut_venue",
            "date_fin_venue",
            "um_entree",
            "um_mode_hospitalisation"
            ]
