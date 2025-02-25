from pathlib import Path
from typing import Any, Callable, List, Optional

from Bio.PDB import PDBParser

from src.utils.logger import get_logger

logger = get_logger(__name__)

class PDBValidationError(Exception):
    """
    Exception raised for errors during PDB validation.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class PDBValidator:
    """
    A class for parsing and validating a PDB chunk file using Bio.PDB.PDBParser.

    Responsibilities:
      - Load the PDB chunk file.
      - Validate the structure using generic validator functions.
    """

    def __init__(self, chunk_file: str) -> None:
        self.chunk_file = Path(chunk_file)
        if not self.chunk_file.exists():
            logger.error("Chunk file %s does not exist.", self.chunk_file)
            raise FileNotFoundError(f"Chunk file {self.chunk_file} does not exist.")
        self.structure: Optional[Any] = None

    def load_data(self) -> Any:
        """
        Loads the chunk file using Bio.PDB.PDBParser and returns the parsed structure.
        """
        parser = PDBParser(QUIET=True)
        try:
            self.structure = parser.get_structure(self.chunk_file.stem, str(self.chunk_file))
            logger.info("Successfully parsed chunk file: %s", self.chunk_file)
        except Exception as e:
            logger.error("Error parsing chunk file: %s", e)
            raise PDBValidationError(
                f"Failed to parse chunk file: {self.chunk_file}. Error: {str(e)}"
            )
        return self.structure

    def validate(self, validators: Optional[List[Callable[[Any], None]]] = None) -> None:
        """
        Runs a list of validation functions on the parsed structure.
        If no validators are provided, the default required atoms validation is applied.

        Each validator function should accept the parsed structure and raise a
        PDBValidationError if the validation fails.
        """
        if self.structure is None:
            self.load_data()

        if validators is None:
            validators = [self.validate_required_atoms]

        for validator in validators:
            try:
                validator(self.structure)
            except PDBValidationError as e:
                logger.error("Validation failed: %s", e.message)
                raise e

    @staticmethod
    def validate_required_atoms(structure: Any, required_atoms: Optional[set] = None) -> None:
        """
        Validates that the structure contains all required atom types.
        By default, required_atoms is {'C', 'CA', 'O', 'N'}.

        Raises a PDBValidationError if any required atom is missing.
        """
        if required_atoms is None:
            required_atoms = {'C', 'CA', 'O', 'N'}

        found_atoms = set()
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        atom_name = atom.get_name().strip()
                        if atom_name in required_atoms:
                            found_atoms.add(atom_name)
                    if found_atoms == required_atoms:
                        break
                if found_atoms == required_atoms:
                    break
            if found_atoms == required_atoms:
                break

        missing_atoms = required_atoms - found_atoms
        if missing_atoms:
            raise PDBValidationError(
                f"Missing required atom types: {', '.join(missing_atoms)}"
            )
        logger.info("Validation passed: All required atoms (%s) are present.", ", ".join(required_atoms))

    @staticmethod
    def validate_column_value(structure: Any, column_index: int, expected_value: str) -> None:
        """
        A generic validator that checks if a specific value exists in a designated column for ATOM records.
        NOTE: Bio.PDB does not directly expose column indices, so this serves as a placeholder.
        In a real implementation, one might parse raw lines or use specific attributes.
        """
        # For demonstration, validate based on the atom name.
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        if atom.get_name().strip() != expected_value:
                            raise PDBValidationError(
                                f"Validation failed: Expected '{expected_value}' in column {column_index} not found."
                            )
        logger.info("Validation passed for column value check: %s", expected_value)


# TESTING
# current_file = Path(__file__).resolve()
# project_root = current_file.parents[2]
#
# # Construct the path to your input file
# input_file = project_root / "data" / "temp_chunks" / "1bey_test.pdb"
#
# PDBValidator(input_file).validate()