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
        ROW_NUMBER() OVER (PARTITION BY sej ORDER BY rumdentree ASC) AS rang
    from
    	pmsi.hackathon_rum
),
first_um as (
	select
		um_rang.*
	from
		um_rang
	where
		um_rang.rang = 1
)
SELECT
    b.idpat,
    b.sej,
    b.date_debut_venue,
    b.date_fin_venue,
    um.um as um_entree,
    um.ummodehospitalisation as um_mode_hospitalisation
from
	borne_venue b,
	first_um um
where
	b.sej = um.sej
ORDER by
	b.idpat, b.sej;
