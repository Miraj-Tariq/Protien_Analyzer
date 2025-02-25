import json
import torch
import pytest
from pathlib import Path
from src.ml_model_integration.inference import ESMIntegration

@pytest.fixture
def sample_output_json(tmp_path: Path) -> Path:
    data = {
        "input_filename": "1bey.pdb",
        "processed_at": "2025-02-24T17:30:22.510946Z",
        "extracted_chains": {
            "H": {
                "sequence": "METMET",
                "length": 6
            },
            "L": {
                "sequence": "ALAMET",
                "length": 6
            }
        }
    }
    json_file = tmp_path / "1bey_output.json"
    with json_file.open("w") as f:
        json.dump(data, f)
    return json_file

@pytest.fixture(scope="module")
def esm_integration_instance():
    instance = ESMIntegration()
    return instance

def test_preprocess_input(sample_output_json: Path, esm_integration_instance):
    tokenized_inputs = esm_integration_instance.preprocess_input(sample_output_json)
    assert "H" in tokenized_inputs
    assert "L" in tokenized_inputs
    for tokens in tokenized_inputs.values():
        assert isinstance(tokens, torch.Tensor)
        assert tokens.numel() > 0

def test_run_inference(esm_integration_instance, sample_output_json: Path):
    tokenized_inputs = esm_integration_instance.preprocess_input(sample_output_json)
    output_tensors, pred_time = esm_integration_instance.run_inference(tokenized_inputs)
    assert "H" in output_tensors and "L" in output_tensors
    assert isinstance(pred_time, float) and pred_time > 0
    for tensor in output_tensors.values():
        assert isinstance(tensor, torch.Tensor)
        assert tensor.ndim >= 2
        assert tensor.shape[0] >= 1

def test_post_process(esm_integration_instance, sample_output_json: Path):
    tokenized_inputs = esm_integration_instance.preprocess_input(sample_output_json)
    output_tensors, pred_time = esm_integration_instance.run_inference(tokenized_inputs)
    metadata = esm_integration_instance.post_process(output_tensors, tokenized_inputs, pred_time)
    required_keys = {"prediction_time", "original_tokens", "model_output", "predicted_sequence"}
    assert required_keys.issubset(metadata.keys())
    assert "H" in metadata["predicted_sequence"]
    assert "L" in metadata["predicted_sequence"]
    for key in ["H", "L"]:
        assert isinstance(metadata["original_tokens"][key], tuple)
        assert isinstance(metadata["model_output"][key], tuple)
