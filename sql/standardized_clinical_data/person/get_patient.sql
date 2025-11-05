WITH ddn AS (
    SELECT
        idpat,
        MIN(ddn) AS ddn
    FROM
        pmsi.hackathon_rss
    GROUP BY
        idpat
),
rum_dates AS (
    SELECT
        idpat,
        rumsexe,
        LEAST(rumdentree, rumdsortie) AS first_date
    FROM
        pmsi.hackathon_rum
)

SELECT DISTINCT ON (r.idpat)
    r.idpat,
    CASE r.rumsexe
        WHEN 1 THEN 'GENDER:M'
        WHEN 2 THEN 'GENDER:F'
        WHEN 3 THEN 'GENDER:I'
    END AS sexe,
    d.ddn
FROM
    rum_dates r
    LEFT JOIN ddn d ON r.idpat = d.idpat
ORDER BY
    r.idpat, r.first_date ASC;
