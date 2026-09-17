from agriagent.composer import NumberFirewallComposer
from agriagent.types import AdvisoryPacket, Intent, Language


class BadRephraser:
    def rephrase(self, text_with_placeholders, language):
        return text_with_placeholders + " invented 999"


class GoodRephraser:
    def rephrase(self, text_with_placeholders, language):
        return "Result: " + text_with_placeholders


def packet():
    return AdvisoryPacket(Language.ENGLISH, Intent.AREA_CONVERSION, "Area", "2 ropani = 0.101748 ha")


def test_reinjects_trusted_numbers():
    out = NumberFirewallComposer(GoodRephraser()).compose(packet())
    assert "2" in out and "0.101748" in out


def test_rejects_model_invented_number():
    out = NumberFirewallComposer(BadRephraser()).compose(packet())
    assert "999" not in out
