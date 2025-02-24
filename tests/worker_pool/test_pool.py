import os
import pytest
from pathlib import Path
from src.worker_pool.pool import WorkerPool


# Dummy processing functions for testing.
def dummy_processing_success(file_name: str) -> str:
    """Simulates successful processing of a file."""
    return f"Processed {file_name}"


# Global dictionary to simulate stateful retries.
retry_counter = {}


def dummy_processing_retry(file_name: str) -> str:
    """
    Simulates processing that fails twice before succeeding.
    Uses a global counter keyed by file_name.
    """
    global retry_counter
    if file_name not in retry_counter:
        retry_counter[file_name] = 0
    retry_counter[file_name] += 1
    if retry_counter[file_name] < 3:
        raise Exception("Temporary failure")
    return f"Processed after retries: {file_name}"


def dummy_processing_fail(file_name: str) -> str:
    """Simulates a processing function that always fails."""
    raise Exception("Processing failed")


@pytest.fixture
def create_temp_chunk_files(tmp_path: Path) -> str:
    """
    Creates a set of temporary chunk files for testing.

    The files are named as follows (with dummy content):
      - [base_address]_001.pdb, [base_address]_002.pdb, ...
    Returns the base address as a string.
    """
    base_prefix = tmp_path / "chunk"
    for i in range(1, 4):
        file_path = tmp_path / f"chunk_{i:03d}.pdb"
        file_path.write_text(f"Dummy content for chunk {i}")
    return str(base_prefix)


def test_process_chunks_success(create_temp_chunk_files: str, tmp_path: Path):
    """
    Test processing of chunk files where all processing functions succeed.
    """
    base_address = str(tmp_path / "chunk")
    pool = WorkerPool(max_workers=2, max_retries=2)
    results = pool.process_chunks(base_address, total_files=3, processing_function=dummy_processing_success)
    assert len(results) == 3
    for file_name, result in results.items():
        assert result.startswith("Processed")
        assert pool.checkpoints[file_name] == "SUCCESS"


def test_process_chunks_retry(create_temp_chunk_files: str, tmp_path: Path):
    """
    Test processing with automatic retries.
    The dummy_processing_retry function fails twice then succeeds.
    """
    # Reset global counter for consistency.
    global retry_counter
    retry_counter = {}

    base_address = str(tmp_path / "chunk")
    pool = WorkerPool(max_workers=2, max_retries=3)
    results = pool.process_chunks(base_address, total_files=3, processing_function=dummy_processing_retry)
    assert len(results) == 3
    for file_name, result in results.items():
        assert result.startswith("Processed after retries")
        assert pool.checkpoints[file_name] == "SUCCESS"


def test_process_chunks_failure(create_temp_chunk_files: str, tmp_path: Path):
    """
    Test processing where the processing function fails even after retries.
    """
    base_address = str(tmp_path / "chunk")
    pool = WorkerPool(max_workers=2, max_retries=1)  # Lower max_retries to force failure.
    results = pool.process_chunks(base_address, total_files=3, processing_function=dummy_processing_fail)
    for file_name, result in results.items():
        assert "FAILED" in result
        assert "Processing failed" in result
