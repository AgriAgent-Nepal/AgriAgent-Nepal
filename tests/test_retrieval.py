from agriagent.retrieval import LexicalRetriever


def test_maize_query_retrieves_faw():
    retriever = LexicalRetriever.from_package_data()
    hits = retriever.search("maize fall armyworm whorl")
    assert hits
    assert hits[0].record.id == "maize-faw-001"


def test_nepali_tomato_query():
    retriever = LexicalRetriever.from_package_data()
    hits = retriever.search("टमाटर पात कालो दाग")
    assert hits
    assert hits[0].record.id == "tomato-blight-001"
