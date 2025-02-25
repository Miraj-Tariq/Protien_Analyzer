from src.config.config import CONFIG

def test_config_keys():
    required_keys = {
        "input_file", "temp_chunks_dir", "output_dir", "inference_output_dir",
        "mapping_file", "accepted_chains", "max_workers", "max_retries", "deduplicate"
    }
    assert required_keys.issubset(set(CONFIG.keys()))
