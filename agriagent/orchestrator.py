from __future__ import annotations

from .agents import AgentRegistry
from .composer import NumberFirewallComposer
from .language import detect_language
from .planner import DeterministicPlanner
from .router import DeterministicRouter
from .types import AdvisoryPacket, Intent, Language


def fmt(value: float, digits: int = 4) -> str:
    s = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return s if s else "0"


class AgriAgent:
    def __init__(self):
        self.router = DeterministicRouter()
        self.planner = DeterministicPlanner()
        self.agents = AgentRegistry()
        self.composer = NumberFirewallComposer()

    def chat(self, message: str, *, debug: bool = False) -> dict:
        language = detect_language(message)
        route = self.router.route(message)
        tools = self.planner.tool_names(route.intent)

        try:
            packet = self._execute(message, language, route.intent)
        except ValueError as exc:
            packet = self._error_packet(language, route.intent, str(exc))

        packet.debug.update(
            {
                "intent": route.intent.value,
                "route_confidence": route.confidence,
                "matched_keywords": list(route.matched_keywords),
                "planned_tools": list(tools),
                "route_reason": route.reason,
            }
        )
        answer = self.composer.compose(packet)
        result = {
            "answer": answer,
            "language": language.value,
            "intent": route.intent.value,
            "citations": packet.citations,
        }
        if debug:
            result["debug"] = packet.debug
        return result

    def _execute(self, message: str, language: Language, intent: Intent) -> AdvisoryPacket:
        if intent == Intent.GREETING:
            return self._greeting(language)
        if intent == Intent.HELP:
            return self._help(language)
        if intent == Intent.AREA_CONVERSION:
            return self._area(message, language)
        if intent == Intent.FERTILIZER_CALCULATION:
            return self._fertilizer(message, language)
        if intent == Intent.AGRONOMY_QUERY:
            return self._retrieve(message, language)
        return self._error_packet(language, intent, "Please provide a little more detail.")

    def _greeting(self, language: Language) -> AdvisoryPacket:
        if language == Language.NEPALI:
            body = "नमस्ते! म AgriAgent Nepal को च्याट डेमो हुँ। बालीसम्बन्धी प्रश्न, जग्गा क्षेत्रफल रूपान्तरण वा स्वीकृत N-P2O5-K2O दरलाई खेतको क्षेत्रफलमा गणना गर्न सोध्न सक्नुहुन्छ।"
            title = "AgriAgent Nepal"
        elif language == Language.ROMANIZED_NEPALI:
            body = "Namaste! Ma AgriAgent Nepal ko chat demo ho. Bali ko prasna, jagga area conversion, wa approved N-P2O5-K2O rate lai khetko area anusar calculate garna sodhna saknuhunchha."
            title = "AgriAgent Nepal"
        else:
            body = "Hello! Ask an agronomy question, convert Nepal land units, or scale an already-approved N-P2O5-K2O recommendation to a field area."
            title = "AgriAgent Nepal"
        return AdvisoryPacket(language, Intent.GREETING, title, body)

    def _help(self, language: Language) -> AdvisoryPacket:
        if language == Language.NEPALI:
            body = "उदाहरण: '5 रोपनीलाई hectare मा बदल्नुहोस्' वा '100-50-30 kg/ha for 2 ropani'। मलको संख्यात्मक दर प्रणालीले आफैं सिफारिस गर्दैन; दर पहिले स्वीकृत स्रोतबाट आउनुपर्छ।"
        elif language == Language.ROMANIZED_NEPALI:
            body = "Udaharan: '5 ropani to hectare' wa '100-50-30 kg/ha for 2 ropani'. System le fertilizer ko numerical rate afai recommend gardaina; rate approved source bata aaunu parchha."
        else:
            body = "Examples: 'Convert 5 ropani to hectare' or '100-50-30 kg/ha for 2 ropani'. The system never invents a fertilizer recommendation; the numeric rate must already come from an approved source."
        return AdvisoryPacket(language, Intent.HELP, "How to use AgriAgent", body)

    def _area(self, message: str, language: Language) -> AdvisoryPacket:
        tool = self.agents.run("area_converter", message, language)
        out = tool.data["conversion"]
        req = tool.data["request"]
        values = [fmt(req["value"]), fmt(out["output_value"]), fmt(out["hectares"])]

        if language == Language.NEPALI:
            body = (
                f"{values[0]} {out['input_unit']} = {values[1]} {out['output_unit']}। "
                f"हेक्टरमा क्षेत्रफल {values[2]} ha हुन्छ।"
            )
            title = "जग्गा क्षेत्रफल रूपान्तरण"
        elif language == Language.ROMANIZED_NEPALI:
            body = (
                f"{values[0]} {out['input_unit']} = {values[1]} {out['output_unit']}. "
                f"Hectare ma area {values[2]} ha hunchha."
            )
            title = "Jagga area conversion"
        else:
            body = (
                f"{values[0]} {out['input_unit']} = {values[1]} {out['output_unit']}. "
                f"The field area is {values[2]} ha."
            )
            title = "Land-area conversion"
        return AdvisoryPacket(
            language, Intent.AREA_CONVERSION, title, body,
            trusted_numbers=values, citations=tool.citations,
            debug={"agent": tool.tool, "calculation": out},
        )

    def _fertilizer(self, message: str, language: Language) -> AdvisoryPacket:
        tool = self.agents.run("fertilizer_calculator", message, language)
        req = tool.data["request"]
        plan = tool.data["plan"]
        nums = {
            "area": fmt(plan["area_ha"]), "n": fmt(req["n"]), "p": fmt(req["p2o5"]), "k": fmt(req["k2o"]),
            "urea": fmt(plan["urea_kg"], 3), "dap": fmt(plan["dap_kg"], 3), "mop": fmt(plan["mop_kg"], 3),
        }
        if language == Language.NEPALI:
            title = "निर्धारित मल दरको गणना"
            body = (
                f"क्षेत्रफल {nums['area']} ha र पहिले नै स्वीकृत N-P2O5-K2O दर {nums['n']}-{nums['p']}-{nums['k']} kg/ha का लागि, "
                f"गणितीय रूपान्तरणले DAP {nums['dap']} kg, MOP {nums['mop']} kg र urea {nums['urea']} kg दिन्छ। "
                "यो नयाँ कृषि सिफारिस होइन; यसले तपाईंले दिएको स्वीकृत पोषक दरलाई मात्र क्षेत्रफलअनुसार रूपान्तरण गर्छ।"
            )
        elif language == Language.ROMANIZED_NEPALI:
            title = "Approved fertilizer rate calculation"
            body = (
                f"Area {nums['area']} ha ra pahile nai approved N-P2O5-K2O rate {nums['n']}-{nums['p']}-{nums['k']} kg/ha ko lagi, "
                f"deterministic calculation le DAP {nums['dap']} kg, MOP {nums['mop']} kg ra urea {nums['urea']} kg dinchha. "
                "Yo naya agronomy recommendation hoina; tapai le diyeko approved nutrient rate matra area anusar convert gareko ho."
            )
        else:
            title = "Approved fertilizer-rate calculation"
            body = (
                f"For {nums['area']} ha and the already-approved N-P2O5-K2O rate {nums['n']}-{nums['p']}-{nums['k']} kg/ha, "
                f"the deterministic conversion gives DAP {nums['dap']} kg, MOP {nums['mop']} kg, and urea {nums['urea']} kg. "
                "This is not a new agronomic recommendation; it only scales the nutrient rate you supplied."
            )
        return AdvisoryPacket(
            language, Intent.FERTILIZER_CALCULATION, title, body,
            trusted_numbers=list(nums.values()), citations=tool.citations,
            debug={"agent": tool.tool, **tool.data},
        )

    def _retrieve(self, message: str, language: Language) -> AdvisoryPacket:
        tool = self.agents.run("lexical_retriever", message, language)
        if not tool.ok:
            return self._error_packet(language, Intent.AGRONOMY_QUERY, tool.message)
        body = "\n\n".join(tool.data["passages"])
        title = {
            Language.ENGLISH: "Retrieved agronomy guidance",
            Language.NEPALI: "प्राप्त कृषि मार्गदर्शन",
            Language.ROMANIZED_NEPALI: "Retrieved krishi guidance",
        }[language]
        return AdvisoryPacket(
            language, Intent.AGRONOMY_QUERY, title, body, citations=tool.citations,
            debug={"agent": tool.tool, "hits": tool.data["hits"]},
        )

    def _error_packet(self, language: Language, intent: Intent, message: str) -> AdvisoryPacket:
        if language == Language.NEPALI:
            body = f"अनुरोध पूरा गर्न सकिएन: {message}"
            title = "थप जानकारी आवश्यक"
        elif language == Language.ROMANIZED_NEPALI:
            body = f"Request pura garna sakiena: {message}"
            title = "Thap jankari chahinchha"
        else:
            body = f"I could not complete that request: {message}"
            title = "More information needed"
        return AdvisoryPacket(language, intent, title, body)
