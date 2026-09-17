from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FertilizerGrade:
    name: str
    n: float
    p2o5: float
    k2o: float


# Mass fractions, not agronomic recommendations.
FERTILIZERS = {
    "urea": FertilizerGrade("Urea", n=0.46, p2o5=0.0, k2o=0.0),
    "dap": FertilizerGrade("DAP", n=0.18, p2o5=0.46, k2o=0.0),
    "mop": FertilizerGrade("MOP", n=0.0, p2o5=0.0, k2o=0.60),
}


@dataclass(frozen=True)
class FertilizerPlan:
    area_ha: float
    target_n_kg_ha: float
    target_p2o5_kg_ha: float
    target_k2o_kg_ha: float
    urea_kg: float
    dap_kg: float
    mop_kg: float
    supplied_n_kg: float
    supplied_p2o5_kg: float
    supplied_k2o_kg: float


def calculate_npk_program(
    *,
    area_ha: float,
    target_n_kg_ha: float,
    target_p2o5_kg_ha: float,
    target_k2o_kg_ha: float,
) -> FertilizerPlan:
    """Convert an already-approved N-P2O5-K2O recommendation into product masses.

    The function does not choose the recommendation. It only performs arithmetic.
    DAP is used to satisfy P2O5, MOP to satisfy K2O, then urea tops up N.
    """
    values = (area_ha, target_n_kg_ha, target_p2o5_kg_ha, target_k2o_kg_ha)
    if any(v < 0 for v in values):
        raise ValueError("Area and nutrient targets must be non-negative.")

    target_n = target_n_kg_ha * area_ha
    target_p = target_p2o5_kg_ha * area_ha
    target_k = target_k2o_kg_ha * area_ha

    dap = target_p / FERTILIZERS["dap"].p2o5 if target_p else 0.0
    n_from_dap = dap * FERTILIZERS["dap"].n
    remaining_n = target_n - n_from_dap
    if remaining_n < -1e-9:
        raise ValueError(
            "The requested P2O5 target supplied through DAP would exceed the requested N target. "
            "Use a different phosphorus source or formulation."
        )
    urea = max(0.0, remaining_n) / FERTILIZERS["urea"].n if remaining_n > 0 else 0.0
    mop = target_k / FERTILIZERS["mop"].k2o if target_k else 0.0

    supplied_n = dap * FERTILIZERS["dap"].n + urea * FERTILIZERS["urea"].n
    supplied_p = dap * FERTILIZERS["dap"].p2o5
    supplied_k = mop * FERTILIZERS["mop"].k2o

    return FertilizerPlan(
        area_ha=area_ha,
        target_n_kg_ha=target_n_kg_ha,
        target_p2o5_kg_ha=target_p2o5_kg_ha,
        target_k2o_kg_ha=target_k2o_kg_ha,
        urea_kg=urea,
        dap_kg=dap,
        mop_kg=mop,
        supplied_n_kg=supplied_n,
        supplied_p2o5_kg=supplied_p,
        supplied_k2o_kg=supplied_k,
    )
