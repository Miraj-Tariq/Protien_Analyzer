import json
import time
import torch
import pytest
from pathlib import Path
from src.ai_ml_integration.inference import ESMIntegration

@pytest.fixture
def sample_output_json(tmp_path: Path) -> Path:
    """
    Creates a temporary sample JSON file mimicking the output from the Output File Generation module.
    """
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
    # Create an instance of ESMIntegration.
    # Note: In a real unit test, you might want to mock heavy model calls.
    instance = ESMIntegration()
    return instance

def test_preprocess_input(sample_output_json: Path, esm_integration_instance):
    """
    Test that preprocess_input correctly tokenizes input sequences.
    """
    tokenized_inputs = esm_integration_instance.preprocess_input(sample_output_json)
    # Expect keys "H" and "L"
    assert "H" in tokenized_inputs
    assert "L" in tokenized_inputs
    # Check that token tensors are torch.Tensor and non-empty.
    for tokens in tokenized_inputs.values():
        assert isinstance(tokens, torch.Tensor)
        assert tokens.numel() > 0

def test_run_inference(esm_integration_instance, sample_output_json: Path):
    """
    Test the run_inference function by preprocessing input and running the model.
    """
    tokenized_inputs = esm_integration_instance.preprocess_input(sample_output_json)
    output_tensors, pred_time = esm_integration_instance.run_inference(tokenized_inputs)
    # Verify that outputs are returned for each chain.
    assert "H" in output_tensors and "L" in output_tensors
    # Check that prediction time is a positive float.
    assert isinstance(pred_time, float) and pred_time > 0
    # Ensure each output tensor is a torch.Tensor and 2D.
    for tensor in output_tensors.values():
        assert isinstance(tensor, torch.Tensor)
        assert tensor.ndim >= 2, "Output tensor should be at least 2D (batch dimension added)"
        assert tensor.shape[0] >= 1, "Expected batch dimension of at least 1"

def test_post_process(esm_integration_instance, sample_output_json: Path):
    """
    Test the post_process function by running the full inference pipeline.
    """
    tokenized_inputs = esm_integration_instance.preprocess_input(sample_output_json)
    output_tensors, pred_time = esm_integration_instance.run_inference(tokenized_inputs)
    metadata = esm_integration_instance.post_process(output_tensors, tokenized_inputs, pred_time)
    # Verify that metadata contains all required keys.
    required_keys = {"prediction_time", "original_tokens", "model_output", "predicted_sequence"}
    assert required_keys.issubset(metadata.keys())
    # Check that predicted_sequence is a dict with keys "H" and "L".
    assert "H" in metadata["predicted_sequence"]
    assert "L" in metadata["predicted_sequence"]
    # Verify that original_tokens and model_output contain shape info (tuple-like).
    for key in ["H", "L"]:
        assert isinstance(metadata["original_tokens"][key], tuple)
        assert isinstance(metadata["model_output"][key], tuple)
