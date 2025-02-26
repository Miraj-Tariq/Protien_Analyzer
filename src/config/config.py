from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Determine the project root based on this file’s location.
BASE_PATH = Path(__file__).resolve().parents[2]

CONFIG = {
    "input_file": BASE_PATH / os.getenv("INPUT_FILE", "data/input/1bey.pdb"),
    "temp_chunks_dir": BASE_PATH / os.getenv("TEMP_CHUNKS_DIR", "data/temp_chunks"),
    "output_dir": BASE_PATH / os.getenv("OUTPUT_DIR", "data/output/extracted"),
    "inference_output_dir": BASE_PATH / os.getenv("INFERENCE_OUTPUT_DIR", "data/output/inferenced"),
    "mapping_file": BASE_PATH / os.getenv("MAPPING_FILE", "data/amino_acids_mapping.json"),
    "accepted_chains": os.getenv("ACCEPTED_CHAINS", "H,L").split(","),
    "max_workers": int(os.getenv("MAX_WORKERS", 4)),
    "max_retries": int(os.getenv("MAX_RETRIES", 3)),
    "deduplicate": os.getenv("DEDUPLICATE", "True").lower() == "true"
}
