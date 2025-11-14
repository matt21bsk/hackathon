select
	dlc.id as source_code,
	dlc.concept_name as source_label,
	'LV_MEASUREMENT' as vocabulary_id
from
	biology.dict_lab_concepts dlc
