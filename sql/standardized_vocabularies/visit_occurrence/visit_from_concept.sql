SELECT
	code as source_code,
	libelle as source_label,
	'LV_VISIT_FROM' as vocabulary_id
FROM
	pmsi.dict_mode_ent;
