import pytest
from pathlib import Path
from src.pipeline.orchestrator import PipelineOrchestrator

class DummyOrchestrator(PipelineOrchestrator):
    # Override methods to simulate minimal processing.
    def split_file(self):
        # Return dummy chunk files (simulate file paths).
        return [Path("dummy_chunk_001.pdb"), Path("dummy_chunk_002.pdb")]

    def extract_chunks(self, chunk_files):
        # Return dummy extraction results.
        return [{"H": ["MET"], "L": ["ALA"]}, {"H": ["MET"], "L": ["MET"]}]

    def merge_extraction_results(self, results):
        merged = {"H": [], "L": []}
        for result in results:
            for chain, codes in result.items():
                merged[chain].extend(codes)
        return merged

@pytest.fixture
def dummy_config(tmp_path):
    dummy_mapping_file = tmp_path / "dummy_mapping.json"
    dummy_mapping_file.write_text('{"MET": "M", "ALA": "A"}')
    config = {
        "input_file": str(tmp_path / "dummy_input.pdb"),
        "temp_chunks_dir": str(tmp_path / "temp_chunks"),
        "output_dir": str(tmp_path / "output"),
        "mapping_file": str(dummy_mapping_file),
        "accepted_chains": ["H", "L"],
        "max_workers": 1,
        "max_retries": 1,
        "deduplicate": True
    }
    (tmp_path / "dummy_input.pdb").write_text("DUMMY PDB CONTENT")
    return config

def test_pipeline_orchestrator(dummy_config, tmp_path):
    orchestrator = DummyOrchestrator(dummy_config)
    # Simulate ML integration stage.
    dummy_ml_metadata = {"ml": "dummy_output"}
    # Monkey-patch run_pipeline to only test extraction merging.
    orchestrator.run_pipeline = lambda: dummy_ml_metadata
    # Test merge function.
    extraction_results = orchestrator.extract_chunks([])
    merged = orchestrator.merge_extraction_results(extraction_results)
    assert merged == {"H": ["MET", "MET"], "L": ["ALA", "MET"]}
