import pytest
from pathlib import Path
from src.file_splitter.splitter import FileSplitter


@pytest.fixture
def sample_pdb_file_with_ter(tmp_path: Path) -> Path:
    """
    Create a temporary sample PDB file with dummy ATOM records and TER markers.
    The file will simulate three proteins:
      - Protein 1: 5 ATOM lines, followed by a TER line.
      - Protein 2: 3 ATOM lines, followed by a TER line.
      - Protein 3: 4 ATOM lines without a TER at the end.
    """
    lines = []
    # Protein 1
    for i in range(1, 6):
        lines.append(f"ATOM  {i:4d} TEST_PROT1\n")
    lines.append("TER   \n")
    # Protein 2
    for i in range(6, 9):
        lines.append(f"ATOM  {i:4d} TEST_PROT2\n")
    lines.append("TER   \n")
    # Protein 3 (no TER at end)
    for i in range(9, 13):
        lines.append(f"ATOM  {i:4d} TEST_PROT3\n")
    pdb_content = "".join(lines)

    file_path = tmp_path / "sample_with_ter.pdb"
    file_path.write_text(pdb_content)
    return file_path


@pytest.fixture
def sample_pdb_file_without_ter(tmp_path: Path) -> Path:
    """
    Create a temporary sample PDB file with dummy ATOM records and no TER markers.
    """
    pdb_content = "\n".join([f"ATOM  {i:4d} TEST" for i in range(1, 11)]) + "\n"
    file_path = tmp_path / "sample_without_ter.pdb"
    file_path.write_text(pdb_content)
    return file_path


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """
    Create a temporary directory for output chunks.
    """
    output_dir = tmp_path / "temp_chunks"
    output_dir.mkdir()
    return output_dir


def test_split_file_with_ter(sample_pdb_file_with_ter: Path, temp_output_dir: Path):
    """
    Test splitting when TER markers are present.
    Expected:
      - Chunk 1: 6 lines (5 ATOM lines + TER)
      - Chunk 2: 4 lines (3 ATOM lines + TER)
      - Chunk 3: 4 lines (4 ATOM lines, no TER)
    """
    splitter = FileSplitter(str(sample_pdb_file_with_ter), str(temp_output_dir))
    output_files = splitter.split()
    assert len(output_files) == 3

    # Verify chunk 1
    with output_files[0].open("r") as f:
        lines = f.readlines()
        assert len(lines) == 6
        assert lines[-1].strip().startswith("TER")

    # Verify chunk 2
    with output_files[1].open("r") as f:
        lines = f.readlines()
        assert len(lines) == 4
        assert lines[-1].strip().startswith("TER")

    # Verify chunk 3 (no TER expected)
    with output_files[2].open("r") as f:
        lines = f.readlines()
        assert len(lines) == 4
        assert not lines[-1].strip().startswith("TER")


def test_split_file_without_ter(sample_pdb_file_without_ter: Path, temp_output_dir: Path):
    """
    Test that if no TER marker is present, the entire file is returned as one chunk.
    """
    splitter = FileSplitter(str(sample_pdb_file_without_ter), str(temp_output_dir))
    output_files = splitter.split()
    assert len(output_files) == 1

    with output_files[0].open("r") as f:
        lines = f.readlines()
        # Expecting 10 lines in one chunk.
        assert len(lines) == 10


def test_input_file_not_found(tmp_path: Path):
    """
    Test that a FileNotFoundError is raised when the input file does not exist.
    """
    non_existent_file = tmp_path / "nonexistent.pdb"
    output_dir = tmp_path / "temp_chunks"
    output_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        FileSplitter(str(non_existent_file), str(output_dir))
