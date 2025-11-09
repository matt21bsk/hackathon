WITH rss_corrige AS (
    SELECT
        idpat,
        sej,
        CASE
            WHEN rssdentree <= rssdsortie THEN rssdentree
            ELSE rssdsortie
        END AS date_debut_corrigee,
        CASE
            WHEN rssdentree <= rssdsortie THEN rssdsortie
            ELSE rssdentree
        END AS date_fin_corrigee
    FROM
        pmsi.hackathon_rss
    WHERE
        idpat || '_' || sej != 'IDPAT344036' || '_' || 'SEJ0165083'
),
borne_venue AS (
    SELECT
        idpat,
        sej,
        MIN(date_debut_corrigee) AS date_debut_venue,
        MAX(date_fin_corrigee) AS date_fin_venue
    FROM
        rss_corrige
    GROUP BY
        idpat, sej
),
um_rang AS (
    SELECT
        pmsi.hackathon_rum.*,
        ROW_NUMBER() OVER (PARTITION BY sej ORDER BY rumdentree ASC) AS rang
    FROM
        pmsi.hackathon_rum
),
first_um AS (
    SELECT
        um_rang.*
    FROM
        um_rang
    WHERE
        um_rang.rang = 1
),
diag AS (
    SELECT
        hd.idpat,
        hd.sej,
        hd.rsstypediagnostic,
        hd.diag
    FROM
        pmsi.hackathon_diag hd
)
SELECT
    b.idpat,
    b.sej,
    b.date_debut_venue,
    b.date_fin_venue,
    d.diag,
    d.rsstypediagnostic
FROM
    borne_venue b,
    first_um um,
    diag d
WHERE
    b.sej = um.sej
    AND b.sej = d.sej
ORDER BY
    b.idpat,
    b.sej;
