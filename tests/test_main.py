import sys
from src.main import main

def test_main_with_input(tmp_path, monkeypatch, capsys):
    # Create a dummy input file.
    dummy_input = tmp_path / "dummy_input.pdb"
    dummy_input.write_text("DUMMY PDB CONTENT")

    # Create a temporary input directory for testing.
    test_input_dir = tmp_path / "data" / "input"
    test_input_dir.mkdir(parents=True, exist_ok=True)

    # Override CONFIG's input_file to point to a default file in the test input directory.
    from src.config.config import CONFIG
    CONFIG["input_file"] = test_input_dir / "default.pdb"

    # Simulate command-line arguments with --input.
    monkeypatch.setattr(sys, "argv", ["main.py", "--input", str(dummy_input)])
    main()

    target_file = test_input_dir / dummy_input.name
    assert target_file.exists()
    # Check output contains the copied file message.
    captured = capsys.readouterr().out
    assert "Input file copied to:" in captured


def test_main_without_input(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    main()
    captured = capsys.readouterr().out
    assert "No input file provided" in captured
