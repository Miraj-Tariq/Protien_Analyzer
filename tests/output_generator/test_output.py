import json
import pytest
from pathlib import Path
from src.output_generator.output import OutputFileGenerator

@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    output_dir = tmp_path / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture
def sample_extracted_chains() -> dict:
    return {
        "H": {"sequence": "MAG", "length": 3},
        "L": {"sequence": "AM", "length": 2}
    }

@pytest.fixture
def sample_input_filename() -> str:
    return "protein_ABC.pdb"

def test_generate_output_file(temp_output_dir: Path, sample_extracted_chains: dict, sample_input_filename: str):
    generator = OutputFileGenerator(output_dir=temp_output_dir)
    output_path = generator.generate_output_file(sample_extracted_chains, sample_input_filename)
    assert output_path.exists()
    with output_path.open("r") as f:
        data = json.load(f)
    assert data["input_filename"] == sample_input_filename
    assert "processed_at" in data
    assert data["extracted_chains"] == sample_extracted_chains

def test_output_file_naming(temp_output_dir: Path, sample_extracted_chains: dict, sample_input_filename: str):
    generator = OutputFileGenerator(output_dir=temp_output_dir)
    output_path = generator.generate_output_file(sample_extracted_chains, sample_input_filename)
    expected_filename = "protein_ABC_output.json"
    assert output_path.name == expected_filename
