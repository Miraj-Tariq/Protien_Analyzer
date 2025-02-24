import pytest
from pathlib import Path
from src.validator.validator import PDBValidator, PDBValidationError

@pytest.fixture
def valid_pdb_file(tmp_path: Path) -> Path:
    """
    Creates a temporary valid PDB file containing a single residue with required atoms:
    N, CA, C, and O.
    """
    pdb_content = (
        "ATOM      1  N   MET A   1      11.104  13.207   2.042  1.00 20.00           N\n"
        "ATOM      2  CA  MET A   1      12.560  13.207   2.042  1.00 20.00           C\n"
        "ATOM      3  C   MET A   1      13.000  14.650   2.042  1.00 20.00           C\n"
        "ATOM      4  O   MET A   1      12.560  15.500   2.042  1.00 20.00           O\n"
        "TER\n"
    )
    file_path = tmp_path / "valid.pdb"
    file_path.write_text(pdb_content)
    return file_path

@pytest.fixture
def invalid_pdb_file(tmp_path: Path) -> Path:
    """
    Creates a temporary PDB file missing a required atom (e.g., missing O).
    """
    pdb_content = (
        "ATOM      1  N   MET A   1      11.104  13.207   2.042  1.00 20.00           N\n"
        "ATOM      2  CA  MET A   1      12.560  13.207   2.042  1.00 20.00           C\n"
        "ATOM      3  C   MET A   1      13.000  14.650   2.042  1.00 20.00           C\n"
        "TER\n"
    )
    file_path = tmp_path / "invalid.pdb"
    file_path.write_text(pdb_content)
    return file_path

def test_parser_valid_file(valid_pdb_file: Path):
    """
    Tests that the parser successfully loads and validates a valid PDB file.
    """
    parser = PDBValidator(str(valid_pdb_file))
    structure = parser.load_data()
    # Should pass default validation (required atoms).
    parser.validate()

def test_parser_invalid_file(invalid_pdb_file: Path):
    """
    Tests that the parser raises a PDBValidationError when a required atom is missing.
    """
    parser = PDBValidator(str(invalid_pdb_file))
    structure = parser.load_data()
    with pytest.raises(PDBValidationError) as excinfo:
        parser.validate()  # Expect failure due to missing 'O'
    assert "Missing required atom types" in str(excinfo.value)

def test_custom_validator(valid_pdb_file: Path):
    """
    Tests using a custom validator that always passes, combined with the default validator.
    """
    parser = PDBValidator(str(valid_pdb_file))
    structure = parser.load_data()

    def custom_validator(structure):
        # A dummy validator that does nothing (always passes).
        return

    # Should pass with both custom and default validations.
    parser.validate(validators=[custom_validator, PDBValidator.validate_required_atoms])
