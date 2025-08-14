from src.notion_paper_manager.parsers.paper import PaperMeta

def test_paper_meta_dataclass():
    m = PaperMeta(title="t", authors=["a"], year=2024)
    assert m.title == "t"
    assert m.authors == ["a"]
    assert m.year == 2024
