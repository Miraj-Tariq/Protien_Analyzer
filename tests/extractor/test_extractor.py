import pytest
from pathlib import Path
from src.extractor.extractor import BioPDBExtractor, deduplicate_adjacent


@pytest.fixture
def sample_pdb_file(tmp_path: Path) -> Path:
    """
    Creates a temporary sample PDB file for testing BioPDBExtractor.

    The file contains two chains:
      - Chain H: Two sets of MET residues (adjacent duplicates).
      - Chain L: Two residues: first ALA then MET.

    Expected behavior:
      - With deduplication enabled, chain H yields a single "MET", and overall extraction is ["MET", "ALA", "MET"].
      - Without deduplication, extraction is ["MET", "MET", "ALA", "MET"].
    """
    pdb_content = (
        "MODEL        1\n"
        "ATOM      1  N   MET H   1      11.104  13.207   2.042  1.00 20.00           N  \n"
        "ATOM      2  CA  MET H   1      12.560  13.207   2.042  1.00 20.00           C  \n"
        "ATOM      3  C   MET H   1      13.000  14.650   2.042  1.00 20.00           C  \n"
        "ATOM      4  O   MET H   1      12.560  15.500   2.042  1.00 20.00           O  \n"
        "ATOM      5  N   MET H   1      11.104  13.207   2.042  1.00 20.00           N  \n"
        "ATOM      6  CA  MET H   1      12.560  13.207   2.042  1.00 20.00           C  \n"
        "ATOM      7  C   MET H   1      13.000  14.650   2.042  1.00 20.00           C  \n"
        "ATOM      8  O   MET H   1      12.560  15.500   2.042  1.00 20.00           O  \n"
        "ATOM      9  N   ALA L   1      11.104  13.207   2.042  1.00 20.00           N  \n"
        "ATOM     10  CA  ALA L   1      12.560  13.207   2.042  1.00 20.00           C  \n"
        "ATOM     11  C   ALA L   1      13.000  14.650   2.042  1.00 20.00           C  \n"
        "ATOM     12  O   ALA L   1      12.560  15.500   2.042  1.00 20.00           O  \n"
        "ATOM     13  N   MET L   1      11.104  13.207   2.042  1.00 20.00           N  \n"
        "ATOM     14  CA  MET L   1      12.560  13.207   2.042  1.00 20.00           C  \n"
        "ATOM     15  C   MET L   1      13.000  14.650   2.042  1.00 20.00           C  \n"
        "ATOM     16  O   MET L   1      12.560  15.500   2.042  1.00 20.00           O  \n"
        "TER\n"
        "ENDMDL\n"
    )
    file_path = tmp_path / "sample.pdb"
    file_path.write_text(pdb_content)
    return file_path


def test_biopdb_extractor_with_deduplication(sample_pdb_file: Path):
    """
    Test BioPDBExtractor with deduplication enabled.

    Expected extraction:
      - From chain H: Two sets of MET residues should be deduplicated to one "MET".
      - From chain L: Residues yield "ALA" followed by "MET".
    Overall expected result: ["MET", "ALA", "MET"]
    """
    extractor = BioPDBExtractor(
        file_path=str(sample_pdb_file),
        accepted_chains=["H", "L"],
        deduplicate=True
    )
    result = extractor.extract()
    assert result == ["MET", "ALA", "MET"]


def test_biopdb_extractor_without_deduplication(sample_pdb_file: Path):
    """
    Test BioPDBExtractor with deduplication disabled.

    Expected extraction:
      - From chain H: Two sets of MET residues => ["MET", "MET"]
      - From chain L: ["ALA", "MET"]
    Overall expected result: ["MET", "MET", "ALA", "MET"]
    """
    extractor = BioPDBExtractor(
        file_path=str(sample_pdb_file),
        accepted_chains=["H", "L"],
        deduplicate=False
    )
    result = extractor.extract()
    assert result == ["MET", "MET", "ALA", "MET"]


def test_deduplicate_adjacent():
    input_list = ["MET", "MET", "ALA", "ALA", "GLY", "GLY", "SER"]
    result = deduplicate_adjacent(input_list)
    assert result == ["MET", "ALA", "GLY", "SER"]
