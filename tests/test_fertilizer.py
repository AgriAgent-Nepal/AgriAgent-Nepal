import pytest

from agriagent.calculators.fertilizer import calculate_npk_program


def test_npk_mass_balance():
    plan = calculate_npk_program(
        area_ha=1.0,
        target_n_kg_ha=100,
        target_p2o5_kg_ha=50,
        target_k2o_kg_ha=30,
    )
    assert plan.supplied_n_kg == pytest.approx(100.0)
    assert plan.supplied_p2o5_kg == pytest.approx(50.0)
    assert plan.supplied_k2o_kg == pytest.approx(30.0)


def test_rejects_dap_n_over_target():
    with pytest.raises(ValueError):
        calculate_npk_program(
            area_ha=1.0,
            target_n_kg_ha=1,
            target_p2o5_kg_ha=100,
            target_k2o_kg_ha=0,
        )
