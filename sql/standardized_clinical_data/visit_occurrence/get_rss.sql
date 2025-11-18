    WITH rss_corrige AS (
        SELECT
            idpat,
            sej,
            CASE WHEN rssdentree <= rssdsortie THEN rssdentree ELSE rssdsortie END AS date_debut_corrigee,
            CASE WHEN rssdentree <= rssdsortie THEN rssdsortie ELSE rssdentree END AS date_fin_corrigee
        from
            pmsi.hackathon_rss
        where
            idpat || '_' || sej != 'IDPAT344036' || '_' || 'SEJ0165083'
    ),
    borne_venue AS (
        SELECT
            idpat,
            sej,
            MIN(date_debut_corrigee) AS date_debut_venue,
            MAX(date_fin_corrigee) AS date_fin_venue
        from
            rss_corrige
        GROUP by
            idpat, sej
    ),
    um_rang AS (
        SELECT
            pmsi.hackathon_rum.*,
            ROW_NUMBER() OVER (PARTITION BY sej ORDER BY rumdentree ASC) AS rang_asc,
            ROW_NUMBER() OVER (PARTITION BY sej ORDER BY rumdentree DESC) as rang_desc
        from
            pmsi.hackathon_rum
    ),
    first_um as (
        select
            um_rang.*
        from
            um_rang
        where
            um_rang.rang_asc = 1
    ),
    last_um as(
        select
            um_rang.*
        from
            um_rang
        where
            um_rang.rang_desc = 1
    )
    SELECT
        b.idpat,
        b.sej,
        b.date_debut_venue,
        b.date_fin_venue,
        fum.um as um_entree,
        fum.rummodeentree as mode_entree,
        lum.rummodesortie as mode_sortie,
        fum.ummodehospitalisation as um_mode_hospitalisation
    from
        borne_venue b
        LEFT JOIN first_um fum
        on b.sej = fum.sej
        LEFT JOIN last_um lum
        on b.sej = lum.sej
    ORDER by
        b.idpat, b.sej;
