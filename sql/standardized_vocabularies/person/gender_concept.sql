SELECT
    'GENDER:M' AS source_code,
    'Sexe masculin' AS source_label,
    'LV_GENDER' AS vocabulary_id
UNION ALL
SELECT
    'GENDER:F',
    'Sexe féminin',
    'LV_GENDER' AS vocabulary_id
UNION ALL
SELECT
    'GENDER:I',
    'Sexe indéterminé',
    'LV_GENDER' AS vocabulary_id;
