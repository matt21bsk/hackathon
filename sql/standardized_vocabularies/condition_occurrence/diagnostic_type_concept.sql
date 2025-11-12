SELECT
    'DP' AS source_code,
    'Diagnostic primaire' AS source_label,
    'LV_DIAGNOSTIC_TYPE' AS vocabulary_id
UNION ALL
SELECT
    'DR' AS source_code,
    'Diagnostic relié' AS source_label,
    'LV_DIAGNOSTIC_TYPE' AS vocabulary_id
UNION ALL
SELECT
    'DAS' AS source_code,
    'Diagnostic associé significatif' AS source_label,
    'LV_DIAGNOSTIC_TYPE' AS vocabulary_id
UNION ALL
SELECT
    'DAD' AS source_code,
    'Diagnostic associé documentaire' AS source_label,
    'LV_DIAGNOSTIC_TYPE' AS vocabulary_id;

