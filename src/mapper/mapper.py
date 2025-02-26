import json
from pathlib import Path
from typing import Dict, List, Union
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Mapper:
    """
    A generic mapper for converting 3-letter amino acid codes to 1-letter codes.

    This class loads a mapping file (JSON) from a specified path and provides a method
    to perform a one-to-one mapping on a dictionary where keys are chain identifiers and values
    are lists of 3-letter codes. If a residue code is not found in the mapping, a warning is logged
    and a default value ("X") is used.

    Attributes:
        mapping_file (Path): Path to the mapping JSON file.
        mapping (Dict[str, str]): Dictionary mapping 3-letter codes to 1-letter codes.
    """

    def __init__(self, mapping_file: Union[str, Path]) -> None:
        self.mapping_file = Path(mapping_file)
        if not self.mapping_file.exists():
            logger.error(f"Mapping file {self.mapping_file} does not exist.")
            raise FileNotFoundError(f"Mapping file {self.mapping_file} does not exist.")

        self.mapping: Dict[str, str] = self._load_mapping()

    def _load_mapping(self) -> Dict[str, str]:
        """
        Loads the mapping from the JSON file into a dictionary.

        Returns:
            Dict[str, str]: Mapping dictionary of 3-letter codes to 1-letter codes.
        """
        try:
            with self.mapping_file.open("r") as f:
                mapping_data = json.load(f)
            logger.info(f"Loaded mapping from {self.mapping_file}")

            return mapping_data
        except Exception as e:
            logger.error(f"Error loading mapping file: {e}")
            raise e

    def one_to_one_mapping(self, sequences: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Converts a dictionary of 3-letter amino acid codes to 1-letter codes.

        For each chain in the input dictionary, each 3-letter code in its list is mapped to its
        corresponding 1-letter code using the loaded mapping dictionary. If a code is missing, a warning
        is logged and "X" is used as the default value.

        Args:
            sequences (Dict[str, List[str]]): Dictionary with keys as chain identifiers and values as lists of
                                              3-letter amino acid codes.

        Returns:
            Dict[str, List[str]]: Dictionary with the same keys and values as lists of 1-letter amino acid codes.
        """
        mapped_dict: Dict[str, List[str]] = {}
        for chain, codes in sequences.items():
            mapped_seq: List[str] = []
            for code in codes:
                one_letter = self.mapping.get(code)
                if one_letter is None:
                    logger.warning(f"Mapping for residue '{code}' not found. Using default 'X'.")
                    one_letter = "X"
                mapped_seq.append(one_letter)
            mapped_dict[chain] = mapped_seq

        logger.info(f"Mapped sequences: {mapped_dict}")
        return mapped_dict
