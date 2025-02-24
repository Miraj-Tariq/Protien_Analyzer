import json
from pathlib import Path
from typing import Dict, List, Union
from src.utils.logger import logger

class Mapper:
    """
    A generic mapper for converting 3-letter amino acid codes to 1-letter codes.

    This class loads a mapping file (JSON) from a specified path and provides a method
    to perform a one-to-one mapping on a list of 3-letter codes. If a residue code is not
    found in the mapping, a warning is logged and a default value ("X") is used.

    Attributes:
        mapping_file (Path): Path to the mapping JSON file.
        mapping (Dict[str, str]): Dictionary mapping 3-letter codes to 1-letter codes.
    """

    def __init__(self, mapping_file: Union[str, Path]) -> None:
        self.mapping_file = Path(mapping_file)
        if not self.mapping_file.exists():
            logger.error("Mapping file %s does not exist.", self.mapping_file)
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
            logger.info("Loaded mapping from %s", self.mapping_file)
            return mapping_data
        except Exception as e:
            logger.error("Error loading mapping file: %s", e)
            raise e

    def one_to_one_mapping(self, sequence: List[str]) -> List[str]:
        """
        Converts a list of 3-letter amino acid codes to 1-letter codes.

        For each code in the input sequence, the method looks up its corresponding 1-letter
        code in the mapping dictionary. If the code is missing, a warning is logged and "X"
        is used as a default.

        Args:
            sequence (List[str]): List of 3-letter amino acid codes.

        Returns:
            List[str]: List of 1-letter amino acid codes.
        """
        mapped_sequence: List[str] = []
        for code in sequence:
            one_letter = self.mapping.get(code)
            if one_letter is None:
                logger.warning("Mapping for residue '%s' not found. Using default 'X'.", code)
                one_letter = "X"
            mapped_sequence.append(one_letter)
        logger.info("Mapped sequence: %s", mapped_sequence)
        return mapped_sequence



# TESTING
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

# Construct the path to your input file
input_file = project_root / "data" / "amino_acids_mapping.json"

print(Mapper(input_file).one_to_one_mapping(
['GLN', 'VAL', 'GLN', 'LEU', 'GLN', 'GLU', 'SER', 'GLY', 'PRO', 'GLY', 'LEU', 'VAL', 'ARG', 'PRO', 'SER', 'GLN', 'THR', 'LEU', 'SER', 'LEU', 'THR', 'CYS', 'THR', 'VAL', 'SER', 'GLY', 'PHE', 'THR', 'PHE', 'THR', 'ASP', 'PHE', 'TYR', 'MET', 'ASN', 'TRP', 'VAL', 'ARG', 'GLN', 'PRO', 'GLY', 'ARG', 'GLY', 'LEU', 'GLU', 'TRP', 'ILE', 'GLY', 'PHE', 'ILE', 'ARG', 'ASP', 'LYS', 'ALA', 'LYS', 'GLY', 'TYR', 'THR', 'GLU', 'TYR', 'ASN', 'PRO', 'SER', 'VAL', 'LYS', 'GLY', 'ARG', 'VAL', 'THR', 'MET', 'LEU', 'VAL', 'ASP', 'THR', 'SER', 'LYS', 'ASN', 'GLN', 'PHE', 'SER', 'LEU', 'ARG', 'LEU', 'SER', 'VAL', 'THR', 'ALA', 'ASP', 'THR', 'ALA', 'VAL', 'TYR', 'CYS', 'ALA', 'ARG', 'GLU', 'GLY', 'HIS', 'THR', 'ALA', 'PRO', 'PHE', 'ASP', 'TYR', 'TRP', 'GLY', 'GLN', 'GLY', 'SER', 'LEU', 'VAL', 'THR', 'VAL', 'SER', 'ALA', 'SER', 'THR', 'LYS', 'GLY', 'PRO', 'SER', 'VAL', 'PHE', 'PRO', 'LEU', 'ALA', 'PRO', 'ALA', 'LEU', 'GLY', 'CYS', 'LEU', 'VAL', 'LYS', 'ASP', 'TYR', 'PHE', 'PRO', 'GLU', 'PRO', 'VAL', 'THR', 'VAL', 'SER', 'TRP', 'ASN', 'SER', 'GLY', 'ALA', 'LEU', 'THR', 'SER', 'GLY', 'VAL', 'HIS', 'THR', 'PHE', 'PRO', 'ALA', 'VAL', 'LEU', 'GLN', 'SER', 'GLY', 'LEU', 'TYR', 'SER', 'LEU', 'SER', 'VAL', 'THR', 'VAL', 'PRO', 'SER', 'LEU', 'GLY', 'THR', 'GLN', 'THR', 'TYR', 'ILE', 'CYS', 'ASN', 'VAL', 'ASN', 'HIS', 'LYS', 'PRO', 'SER', 'ASN', 'THR', 'LYS', 'VAL', 'ASP', 'LYS', 'VAL']
))