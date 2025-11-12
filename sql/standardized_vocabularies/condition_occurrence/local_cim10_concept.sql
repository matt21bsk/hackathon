SELECT
	distinct hd.diag as source_code,
	concat('Local','_','CIM10','_',hd.diag) as source_label,
	'LV_CIM10' as vocabulary_id
FROM
	pmsi.hackathon_diag hd
