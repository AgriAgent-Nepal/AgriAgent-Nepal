import pytest

from agriagent.calculators.area import convert_area


def test_ropani_to_hectare():
    out = convert_area(1, "ropani", "hectare")
    assert out.hectares == pytest.approx(0.050874, rel=1e-6)


def test_bigha_to_kattha():
    out = convert_area(1, "bigha", "kattha")
    assert out.output_value == pytest.approx(20.0, rel=1e-9)


def test_kattha_to_dhur():
    out = convert_area(1, "kattha", "dhur")
    assert out.output_value == pytest.approx(20.0, rel=1e-9)
