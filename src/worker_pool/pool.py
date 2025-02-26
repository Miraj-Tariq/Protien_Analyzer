import concurrent.futures
from pathlib import Path
from typing import Callable, Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WorkerPool:
    """
    A generic worker pool for processing chunk files concurrently.

    Attributes:
        max_workers (int): Maximum number of parallel worker processes.
        max_retries (int): Maximum number of retries for a failed task.
        checkpoints (Dict[str, Any]): A dictionary to track processing status for each chunk.
    """
    def __init__(self, max_workers: int = 4, max_retries: int = 3) -> None:
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.checkpoints: Dict[str, Any] = {}
        logger.info("WorkerPool initialized with max_workers=%d, max_retries=%d",
                    self.max_workers, self.max_retries)

    def _build_file_name(self, base_address: str, chunk_number: int) -> str:
        """
        Constructs the file name for a given chunk number.

        Format: [base_address]_[chunk_number in 3-digit format].pdb
        """
        return f"{base_address}_{chunk_number:03d}.pdb"

    def process_chunks(
        self,
        base_address: str,
        total_files: int,
        processing_function: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """
        Processes multiple chunk files concurrently.

        Args:
            base_address (str): The base address (including path and file prefix) for chunk files.
            total_files (int): The total number of chunk files.
            processing_function (Callable[[str], Any]): Function to process a single chunk file.
                It should accept the file path (str) and return a result.

        Returns:
            Dict[str, Any]: A dictionary mapping file names to their processing result.
                            If a chunk fails, its value will contain an error message.
        """
        results: Dict[str, Any] = {}
        future_to_file: Dict[concurrent.futures.Future, str] = {}

        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks for each chunk file.
            for i in range(1, total_files + 1):
                file_name = self._build_file_name(base_address, i)
                future = executor.submit(self._process_with_retries, file_name, processing_function)
                future_to_file[future] = file_name

            # Collect results as tasks complete.
            for future in concurrent.futures.as_completed(future_to_file):
                file_name = future_to_file[future]
                try:
                    result = future.result()
                    results[file_name] = result
                    self.checkpoints[file_name] = "SUCCESS"
                    logger.info("Successfully processed %s", file_name)
                except Exception as exc:
                    error_msg = f"FAILED: {exc}"
                    results[file_name] = error_msg
                    self.checkpoints[file_name] = error_msg
                    logger.error("Failed to process %s: %s", file_name, exc)

        return results

    def _process_with_retries(
        self,
        file_name: str,
        processing_function: Callable[[str], Any]
    ) -> Any:
        """
        Processes a single chunk file with automatic retries.

        Args:
            file_name (str): The file name to process.
            processing_function (Callable[[str], Any]): The processing function.

        Returns:
            Any: The result of processing the file.

        Raises:
            Exception: If processing fails after the maximum number of retries.
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                if not Path(file_name).exists():
                    raise FileNotFoundError(f"File {file_name} not found.")
                result = processing_function(file_name)
                return result
            except Exception as e:
                retries += 1
                logger.warning("Error processing %s (attempt %d/%d): %s",
                               file_name, retries, self.max_retries, e)
                if retries > self.max_retries:
                    logger.error("Exceeded max retries for %s", file_name)
                    raise e
