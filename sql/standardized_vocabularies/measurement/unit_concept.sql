select distinct
	dlu.unit_name as source_code,
	concat('label','_',dlu.unit_name) as source_label,
	'LV_UNITS' as vocabulary_id
from
	biology.dict_lab_units dlu
