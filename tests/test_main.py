import sys
import logging

from src.main import main

def test_main_with_input(tmp_path, monkeypatch, capsys):
    # Create a dummy input file.
    dummy_input = tmp_path / "dummy_input.pdb"
    dummy_input.write_text(
        """ATOM      1  N   ASP L   1     -11.979  53.307  56.156  1.00 60.18           N
ATOM      2  CA  ASP L   1     -11.409  53.134  54.804  1.00 60.18           C
ATOM      3  C   ASP L   1     -12.566  52.994  53.833  1.00 60.18           C
ATOM      4  O   ASP L   1     -13.638  52.533  54.223  1.00 60.18           O
ATOM      5  CB  ASP L   1     -10.548  51.882  54.788  1.00100.00           C
ATOM      6  CG  ASP L   1      -9.519  51.885  55.894  1.00100.00           C
ATOM      7  OD1 ASP L   1      -9.919  51.955  57.078  1.00100.00           O
ATOM      8  OD2 ASP L   1      -8.311  51.825  55.585  1.00100.00           O
TER       9      CYS L   1 """
    )

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


def test_main_without_input(monkeypatch, caplog):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    with caplog.at_level(logging.INFO):
        main()
    # Now assert that the log message is present.
    assert "No input file provided; using default from config." in caplog.text
