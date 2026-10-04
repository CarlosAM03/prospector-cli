"""Characterize CLI behavior retained while its Engine policy is unresolved."""

from models.search_result import SearchResult
import main as cli


def test_cli_preserves_historical_500_request_and_no_export(monkeypatch, capsys):
    answers = iter(["cafes", "Tijuana", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    called = []

    def search(*, query, limit):
        called.append((query, limit))
        return SearchResult(query=query)

    monkeypatch.setattr(cli, "search_businesses", search)
    cli.execute_search()
    assert len(called) == 1
    assert called[0][0].keyword == "cafes"
    assert called[0][0].location == "Tijuana"
    assert called[0][1] == 500
    assert "Businesses Found : 0" in capsys.readouterr().out
