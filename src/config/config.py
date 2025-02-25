# src/config/config.py

# This configuration dictionary is designed to be plug-and-play.
# You can change values or even module implementations without modifying the core pipeline code.
from pathlib import Path

current_file = Path(__file__).resolve()
base_path = current_file.parents[2]

CONFIG = {
    "input_file": base_path / "data" / "input" / "1bey.pdb",            # Path to the input PDB file.
    "temp_chunks_dir": base_path / "data" / "temp_chunks",           # Directory to store file chunks.
    "output_dir": base_path / "data" / "output" / "extracted",                # Directory to write the final JSON output.
    "inference_output_dir": base_path / "data" / "output" / "inferenced",
    "mapping_file": base_path / "data" / "amino_acids_mapping.json",  # Path to the JSON mapping file.
    "accepted_chains": ["H", "L"],              # Chains to extract.
    "max_workers": 4,                           # Maximum workers for parallel processing.
    "max_retries": 3,                           # Maximum retries for failed chunk processing.
    "deduplicate": True                         # Whether to deduplicate adjacent residues.
}
