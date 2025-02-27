import pytest
from pathlib import Path
from src.pipeline.orchestrator import PipelineOrchestrator

class DummyOrchestrator(PipelineOrchestrator):
    # Override methods to simulate minimal processing.
    def split_file(self):
        # Return dummy chunk file paths.
        return [Path("dummy_chunk_001.pdb"), Path("dummy_chunk_002.pdb")]

    def extract_chunks(self, chunk_files):
        # Simulate extraction results from two chunks:
        # First chunk returns {"H": ["MET"], "L": ["ALA"]}
        # Second chunk returns {"H": ["MET"], "L": ["MET"]}
        return [{"H": ["MET"], "L": ["ALA"]}, {"H": ["MET"], "L": ["MET"]}]

    # Inherit merge_extraction_results from parent (which currently just concatenates lists).

@pytest.fixture
def dummy_config(tmp_path):
    dummy_mapping_file = tmp_path / "dummy_mapping.json"
    dummy_mapping_file.write_text('{"MET": "M", "ALA": "A"}')
    config = {
        "input_file": str(tmp_path / "dummy_input.pdb"),
        "temp_chunks_dir": str(tmp_path / "temp_chunks"),
        "output_dir": str(tmp_path / "output"),
        "inference_output_dir": str(tmp_path / "inferenced"),
        "mapping_file": str(dummy_mapping_file),
        "accepted_chains": ["H", "L"],
        "max_workers": 1,
        "max_retries": 1,
        "deduplicate": True  # Note: This flag is not used in global merge.
    }
    (tmp_path / "dummy_input.pdb").write_text("DUMMY PDB CONTENT")
    return config

def test_pipeline_orchestrator(dummy_config, capsys):
    orchestrator = DummyOrchestrator(dummy_config)
    extraction_results = orchestrator.extract_chunks([])
    merged = orchestrator.merge_extraction_results(extraction_results)
    print("Merged extraction:", merged)
    capsys.readouterr()  # Clear captured output.
    # Expected result: since merge_extraction_results just concatenates,
    # chain "H" will be ["MET", "MET"] and chain "L" will be ["ALA", "MET"].
    expected = {"H": ["MET", "MET"], "L": ["ALA", "MET"]}
    assert merged == expected
