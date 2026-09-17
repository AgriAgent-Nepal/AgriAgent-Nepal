import pytest

from agriagent.router import DeterministicRouter
from agriagent.types import Intent


@pytest.mark.parametrize(
    ("text", "intent"),
    [
        ("Convert 5 ropani to hectare", Intent.AREA_CONVERSION),
        ("2 bigha in hectare", Intent.AREA_CONVERSION),
        ("100-50-30 kg/ha fertilizer for 2 ropani", Intent.FERTILIZER_CALCULATION),
        ("100-50-30 kg/ha khad 3 kattha ko lagi", Intent.FERTILIZER_CALCULATION),
        ("टमाटरको पातमा कालो दाग छ", Intent.AGRONOMY_QUERY),
        ("Mero makai ma fauji kira jasto cha", Intent.AGRONOMY_QUERY),
        ("hello", Intent.GREETING),
    ],
)
def test_routes(text, intent):
    assert DeterministicRouter().route(text).intent == intent
