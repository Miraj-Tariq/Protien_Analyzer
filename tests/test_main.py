import pytest
from src.main import main
from src.pipeline.orchestrator import PipelineOrchestrator


def test_main_runs(monkeypatch, capsys):
    # Monkey-patch PipelineOrchestrator to bypass heavy processing.
    monkeypatch.setattr(PipelineOrchestrator, "__init__", lambda self, config: None)
    monkeypatch.setattr(PipelineOrchestrator, "run_pipeline", lambda self: {"dummy_key": "dummy_value"})

    main()  # Run main; it should print dummy output.
    captured = capsys.readouterr().out
    assert "dummy_key" in captured
