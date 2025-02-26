from src.config.config import CONFIG, BASE_PATH

def test_config_keys():
    required_keys = {
        "input_file", "temp_chunks_dir", "output_dir", "inference_output_dir",
        "mapping_file", "accepted_chains", "max_workers", "max_retries", "deduplicate"
    }
    assert required_keys.issubset(set(CONFIG.keys()))

def test_config_values():
    # Check that paths are Path objects.
    assert isinstance(CONFIG["input_file"], type(BASE_PATH))
    # accepted_chains should be a list.
    assert isinstance(CONFIG["accepted_chains"], list)
    # max_workers and max_retries should be integers.
    assert isinstance(CONFIG["max_workers"], int)
    assert isinstance(CONFIG["max_retries"], int)
    # deduplicate should be a boolean.
    assert isinstance(CONFIG["deduplicate"], bool)
