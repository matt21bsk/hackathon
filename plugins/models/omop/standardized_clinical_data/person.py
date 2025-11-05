from typing import Optional, Dict
from datetime import datetime
from omop_base_model import OmopBaseModel


class Person(OmopBaseModel):
    table_name = "person"

    def __init__(
        self,
        person_id: int,
        gender_concept_id: int,
        year_of_birth: Optional[int],
        month_of_birth: Optional[int],
        day_of_birth: Optional[int],
        birth_datetime: Optional[datetime],
        race_concept_id: int = 0,
        ethnicity_concept_id: int = 0,
        location_id: Optional[int] = None,
        provider_id: Optional[int] = None,
        care_site_id: Optional[int] = None,
        person_source_value: Optional[str] = None,
        gender_source_value: Optional[str] = None,
        gender_source_concept_id: Optional[int] = None,
        race_source_value: Optional[str] = None,
        race_source_concept_id: Optional[int] = None,
        ethnicity_source_value: Optional[str] = None,
        ethnicity_source_concept_id: Optional[int] = None,
    ):
        self.person_id = person_id
        self.gender_concept_id = gender_concept_id
        self.year_of_birth = year_of_birth
        self.month_of_birth = month_of_birth
        self.day_of_birth = day_of_birth
        self.birth_datetime = birth_datetime
        self.race_concept_id = race_concept_id
        self.ethnicity_concept_id = ethnicity_concept_id
        self.location_id = location_id
        self.provider_id = provider_id
        self.care_site_id = care_site_id
        self.person_source_value = person_source_value
        self.gender_source_value = gender_source_value
        self.gender_source_concept_id = gender_source_concept_id
        self.race_source_value = race_source_value
        self.race_source_concept_id = race_source_concept_id
        self.ethnicity_source_value = ethnicity_source_value
        self.ethnicity_source_concept_id = ethnicity_source_concept_id

    @property
    def _values(self):
        """Liste des valeurs pour COPY"""
        return [
            self.person_id,
            self.gender_concept_id,
            self.year_of_birth,
            self.month_of_birth,
            self.day_of_birth,
            self.birth_datetime,
            self.race_concept_id,
            self.ethnicity_concept_id,
            self.location_id,
            self.provider_id,
            self.care_site_id,
            self.person_source_value,
            self.gender_source_value,
            self.gender_source_concept_id,
            self.race_source_value,
            self.race_source_concept_id,
            self.ethnicity_source_value,
            self.ethnicity_source_concept_id,
        ]

    @classmethod
    def _columns(cls):
        """Colonnes OMOP correspondant à la table person"""
        return [
            "person_id",
            "gender_concept_id",
            "year_of_birth",
            "month_of_birth",
            "day_of_birth",
            "birth_datetime",
            "race_concept_id",
            "ethnicity_concept_id",
            "location_id",
            "provider_id",
            "care_site_id",
            "person_source_value",
            "gender_source_value",
            "gender_source_concept_id",
            "race_source_value",
            "race_source_concept_id",
            "ethnicity_source_value",
            "ethnicity_source_concept_id",
        ]
