from typing import List
from models.sql_object_base_model import SQLObjectBaseModel


class OmopBaseModel(SQLObjectBaseModel):
    """
    Classe de base pour les tables OMOP cliniques.
    Fournit la conversion en liste et la définition des colonnes.
    """

    schema: str = "omop"
    table_name: str = ""
