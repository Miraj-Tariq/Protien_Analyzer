from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union

from src.config.config import CONFIG
from src.utils.file_storage import store_data
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OutputFileGenerator:
    """
    Generates output data from processed information.

    This module transforms the input data into the required output format and delegates
    the storage to the generic file storage utility.
    """
    def __init__(self, output_dir: Union[str, Path] = CONFIG["output_dir"]) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory set to: {self.output_dir.resolve()}")

    def transform_data(self,
                       input_filename: str,
                       extracted_chains: Dict[str, Dict[str, Union[str, int]]]) -> Dict[str, Any]:
        """
        Transforms input data into the desired output schema.

        Args:
            input_filename (str): Name of the input PDB file.
            extracted_chains (Dict[str, Dict[str, Union[str, int]]]): Mapping of chain data.

        Returns:
            Dict[str, Any]: Transformed output data.
        """
        output_data = {
            "input_filename": str(input_filename),
            "processed_at": datetime.now().isoformat() + "Z",
            "extracted_chains": extracted_chains
        }

        return output_data

    def generate_output_file(self, extracted_chains: Dict[str, Dict[str, Union[str, int]]],
                             input_filename: str = CONFIG["input_file"]) -> Path:
        """
        Transforms data and stores it as a JSON file using the file storage utility.

        Args:
            input_filename (str): The name of the input PDB file.
            extracted_chains (Dict[str, Dict[str, Union[str, int]]]): The transformed chain data.

        Returns:
            Path: The path to the generated output JSON file.
        """
        data = self.transform_data(input_filename, extracted_chains)
        base_name = Path(input_filename).stem
        output_file_name = f"{base_name}_output.json"
        output_file_path = self.output_dir / output_file_name

        return store_data(data, output_file_path, format="json")
