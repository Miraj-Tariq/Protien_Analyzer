import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union
from src.utils.logger import logger


class OutputFileGenerator:
    """
    A module to generate a JSON output file containing processing metadata and extracted chain data.

    The JSON schema includes:
      - input_filename: Name of the input file.
      - processed_at: Date and time of processing (ISO8601 format).
      - extracted_chains: An object containing:
            "H": { "sequence": "<concatenated string>", "length": <number> },
            "L": { "sequence": "<concatenated string>", "length": <number> }

    The output file is automatically named based on the input filename (e.g., protein_ABC_output.json)
    and is stored in the project_root/data/output/ directory.
    """

    def __init__(self, output_dir: Union[str, Path] = "data/output") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Output directory set to: %s", self.output_dir.resolve())

    def generate_output_file(self, input_filename: str, extracted_chains: Dict[str, List[str]]) -> Path:
        """
        Generates a JSON output file with the given input filename and extracted chain data.

        Args:
            input_filename (str): The name of the input PDB file.
            extracted_chains (Dict[str, List[str]]): A dictionary with keys as chain identifiers
                (e.g., "H", "L") and values as lists of 1-letter amino acid codes.

        Returns:
            Path: The path to the generated JSON output file.
        """
        # Build the JSON object according to the schema.
        output_data = {
            "input_filename": input_filename,
            "processed_at": datetime.utcnow().isoformat() + "Z",  # Appending 'Z' for UTC
            "extracted_chains": {}
        }

        # Process each chain in extracted_chains.
        for chain, codes in extracted_chains.items():
            sequence = "".join(codes)
            output_data["extracted_chains"][chain] = {
                "sequence": sequence,
                "length": len(sequence)
            }

        # Construct the output file name. Remove extension if present.
        base_name = Path(input_filename).stem
        output_file_name = f"{base_name}_output.json"
        output_file_path = self.output_dir / output_file_name

        try:
            with output_file_path.open("w") as outfile:
                json.dump(output_data, outfile, indent=4)
            logger.info("Output file generated: %s", output_file_path.resolve())
        except Exception as e:
            logger.error("Error writing output file: %s", e)
            raise e

        return output_file_path


# TESTING
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

# Construct the path to your input file
output_dir = project_root / "data" / "output"

OutputFileGenerator(output_dir).generate_output_file(
    "1bey.pdb",
{'H': ['Q', 'V', 'Q', 'L', 'Q', 'E', 'S', 'G', 'P', 'G', 'L', 'V', 'R', 'P', 'S', 'Q', 'T', 'L', 'S', 'L', 'T', 'a', 'T', 'V', 'S', 'G', 'F', 'T', 'F', 'T', 'C', 'F', 'Y', 'M', 'N', 'W', 'V', 'R', 'Q', 'P', 'G', 'R', 'G', 'L', 'E', 'W', 'I', 'G', 'F', 'I', 'R', 'C', 'K', 'A', 'K', 'G', 'Y', 'T', 'E', 'Y', 'N', 'P', 'S', 'V', 'K', 'G', 'R', 'V', 'T', 'M', 'L', 'V', 'C', 'T', 'S', 'K', 'N', 'Q', 'F', 'S', 'L', 'R', 'L', 'S', 'V', 'T', 'A', 'C', 'T', 'A', 'V', 'Y', 'a', 'A', 'R', 'E', 'G', 'H', 'T', 'A', 'P', 'F', 'C', 'Y', 'W', 'G', 'Q', 'G', 'S', 'L', 'V', 'T', 'V', 'S', 'A', 'S', 'T', 'K', 'G', 'P', 'S', 'V', 'F', 'P', 'L', 'A', 'P', 'A', 'L', 'G', 'a', 'L', 'V', 'K', 'C', 'Y', 'F', 'P', 'E', 'P', 'V', 'T', 'V', 'S', 'W', 'N', 'S', 'G', 'A', 'L', 'T', 'S', 'G', 'V', 'H', 'T', 'F', 'P', 'A', 'V', 'L', 'Q', 'S', 'G', 'L', 'Y', 'S', 'L', 'S', 'V', 'T', 'V', 'P', 'S', 'L', 'G', 'T', 'Q', 'T', 'Y', 'I', 'a', 'N', 'V', 'N', 'H', 'K', 'P', 'S', 'N', 'T', 'K', 'V', 'C', 'K', 'V'], 'L': ['C', 'I', 'Q', 'M', 'T', 'Q', 'S', 'P', 'S', 'L', 'S', 'A', 'S', 'V', 'G', 'C', 'R', 'V', 'T', 'I', 'T', 'a', 'K', 'A', 'S', 'Q', 'N', 'I', 'C', 'K', 'Y', 'L', 'N', 'W', 'Y', 'Q', 'K', 'P', 'G', 'K', 'A', 'P', 'K', 'L', 'I', 'Y', 'N', 'T', 'N', 'L', 'Q', 'T', 'G', 'V', 'P', 'S', 'R', 'F', 'S', 'G', 'S', 'G', 'S', 'G', 'T', 'C', 'F', 'T', 'F', 'T', 'I', 'S', 'L', 'Q', 'P', 'E', 'C', 'I', 'A', 'T', 'Y', 'a', 'L', 'Q', 'H', 'I', 'S', 'R', 'P', 'R', 'T', 'F', 'G', 'Q', 'G', 'T', 'K', 'V', 'E', 'I', 'K', 'R', 'T', 'V', 'A', 'P', 'S', 'V', 'F', 'I', 'F', 'P', 'S', 'C', 'E', 'Q', 'L', 'K', 'S', 'G', 'T', 'A', 'S', 'V', 'a', 'L', 'N', 'F', 'Y', 'P', 'R', 'E', 'A', 'K', 'V', 'Q', 'W', 'K', 'V', 'C', 'N', 'A', 'L', 'Q', 'S', 'G', 'N', 'S', 'Q', 'E', 'S', 'V', 'T', 'E', 'Q', 'C', 'S', 'K', 'C', 'S', 'T', 'Y', 'S', 'L', 'S', 'T', 'L', 'T', 'L', 'S', 'K', 'A', 'C', 'Y', 'E', 'K', 'H', 'K', 'V', 'Y', 'A', 'a', 'E', 'V', 'T', 'H', 'Q', 'G', 'L', 'S', 'P', 'V', 'T', 'K', 'S', 'F', 'N', 'R', 'G', 'E', 'a']}
)