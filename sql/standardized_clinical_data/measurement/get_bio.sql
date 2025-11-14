select
	ld.idpat,
	ld.sej,
	lr.date_result,
	lr.value,
	dlu.unit_name,
	dlc.norm_lower,
	dlc.norm_upper,
	dlc.concept_name as source_concept_name,
	lr.verbatim,
	dlc.id as source_concept_code
from biology.lab_demands ld
	join biology.lab_results lr on ld.id = lr.demand_id
	join biology.dict_lab_units dlu on lr.unit_id = dlu.id
	join biology.dict_lab_concepts dlc on lr.concept_id = dlc.id;
