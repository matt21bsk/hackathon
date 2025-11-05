from typing import List


class SQLObjectBaseModel:
    """
    Classe de base pour les tables SQL.
    Fournit la conversion en liste et la définition des colonnes.
    """

    @property
    def _values(self) -> List:
        """Doit être surchargé dans la sous-classe"""
        raise NotImplementedError("_values doit être défini dans la sous-classe")

    @classmethod
    def _columns(cls) -> List[str]:
        """Doit être surchargé dans la sous-classe"""
        raise NotImplementedError("_columns doit être défini dans la sous-classe")

    def to_list(self, null_placeholder: str | None = "\\N") -> List:
        """Retourne les valeurs prêtes pour COPY, avec gestion des nulls"""
        return [str(v) if v is not None else null_placeholder for v in self._values]

    @classmethod
    def omop_columns(cls) -> List[str]:
        """Retourne la liste des colonnes OMOP de la table"""
        return cls._columns()
