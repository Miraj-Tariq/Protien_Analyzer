import pytest
from pathlib import Path
from src.extractor.extractor import BioPDBExtractor, deduplicate_adjacent

@pytest.fixture
def sample_pdb_file(tmp_path: Path) -> Path:
    """
    Creates a temporary sample PDB file for testing BioPDBExtractor.

    The file contains two chains:
      - Chain H: Two residues with different residue IDs.
          First residue: "MET" (residue id 1)
          Second residue: "MET" (residue id 2)
      - Chain L: Two residues:
          First residue: "ALA" (residue id 1)
          Second residue: "MET" (residue id 2)

    With deduplication enabled:
      - Chain H should yield ["MET"].
      - Chain L should yield ["ALA", "MET"].
    With deduplication disabled:
      - Chain H should yield ["MET", "MET"].
      - Chain L should yield ["ALA", "MET"].
    """
    pdb_content = (
        "MODEL        1\n"
        # Chain H, residue 1: MET
        "ATOM      1  N   MET H   1      11.104  13.207   2.042  1.00 20.00           N  \n"
        "ATOM      2  CA  MET H   1      12.560  13.207   2.042  1.00 20.00           C  \n"
        "ATOM      3  C   MET H   1      13.000  14.650   2.042  1.00 20.00           C  \n"
        "ATOM      4  O   MET H   1      12.560  15.500   2.042  1.00 20.00           O  \n"
        # Chain H, residue 2: MET
        "ATOM      5  N   MET H   2      11.104  13.207   2.042  1.00 20.00           N  \n"
        "ATOM      6  CA  MET H   2      12.560  13.207   2.042  1.00 20.00           C  \n"
        "ATOM      7  C   MET H   2      13.000  14.650   2.042  1.00 20.00           C  \n"
        "ATOM      8  O   MET H   2      12.560  15.500   2.042  1.00 20.00           O  \n"
        # Chain L, residue 1: ALA
        "ATOM      9  N   ALA L   1      11.104  13.207   2.042  1.00 20.00           N  \n"
        "ATOM     10  CA  ALA L   1      12.560  13.207   2.042  1.00 20.00           C  \n"
        "ATOM     11  C   ALA L   1      13.000  14.650   2.042  1.00 20.00           C  \n"
        "ATOM     12  O   ALA L   1      12.560  15.500   2.042  1.00 20.00           O  \n"
        # Chain L, residue 2: MET
        "ATOM     13  N   MET L   2      11.104  13.207   2.042  1.00 20.00           N  \n"
        "ATOM     14  CA  MET L   2      12.560  13.207   2.042  1.00 20.00           C  \n"
        "ATOM     15  C   MET L   2      13.000  14.650   2.042  1.00 20.00           C  \n"
        "ATOM     16  O   MET L   2      12.560  15.500   2.042  1.00 20.00           O  \n"
        "TER\n"
        "ENDMDL\n"
    )
    file_path = tmp_path / "sample.pdb"
    file_path.write_text(pdb_content)
    return file_path

def test_biopdb_extractor_with_deduplication(sample_pdb_file: Path):
    """
    Test BioPDBExtractor with deduplication enabled.
    Expected:
      - Chain H: ["MET"] (duplicates removed)
      - Chain L: ["ALA", "MET"]
    """
    extractor = BioPDBExtractor(
        file_path=str(sample_pdb_file),
        accepted_chains=["H", "L"],
        deduplicate=True
    )
    result = extractor.extract()
    expected = {"H": ["MET"], "L": ["ALA", "MET"]}
    assert result == expected

def test_biopdb_extractor_without_deduplication(sample_pdb_file: Path):
    """
    Test BioPDBExtractor with deduplication disabled.
    Expected:
      - Chain H: ["MET", "MET"]
      - Chain L: ["ALA", "MET"]
    """
    extractor = BioPDBExtractor(
        file_path=str(sample_pdb_file),
        accepted_chains=["H", "L"],
        deduplicate=False
    )
    result = extractor.extract()
    expected = {"H": ["MET", "MET"], "L": ["ALA", "MET"]}
    assert result == expected

def test_deduplicate_adjacent():
    input_list = ["MET", "MET", "ALA", "ALA", "GLY", "GLY", "SER"]
    result = deduplicate_adjacent(input_list)
    assert result == ["MET", "ALA", "GLY", "SER"]
