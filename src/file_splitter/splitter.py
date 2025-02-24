import logging
from pathlib import Path
from typing import List
from src.utils.logger import logger

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

class FileSplitter:
    """
    A class to split a PDB file into smaller chunks based on protein boundaries.
    The file is split each time a line starting with "TER" is encountered.

    Attributes:
        input_file (Path): Path to the input PDB file.
        output_dir (Path): Directory where chunk files will be stored.
    """

    def __init__(self, input_file: str, output_dir: str = project_root / "data" / "temp_chunks") -> None:
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)

        if not self.input_file.exists():
            logger.error("Input file %s does not exist.", self.input_file)
            raise FileNotFoundError(f"Input file {self.input_file} does not exist.")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Initialized FileSplitter with input file %s and output directory %s",
                    self.input_file, self.output_dir)

    def split(self) -> List[Path]:
        """
        Splits the input file into chunks using "TER" records as boundaries.

        Returns:
            List[Path]: A list of paths to the generated chunk files.
        """
        output_files: List[Path] = []
        chunk_lines: List[str] = []
        chunk_number = 1

        logger.info("Starting protein-based file splitting for %s", self.input_file)
        with self.input_file.open("r") as infile:
            for line in infile:
                chunk_lines.append(line)
                # When a "TER" record is found, complete the current chunk.
                if line.strip().startswith("TER"):
                    output_file = self._write_chunk(chunk_lines, chunk_number)
                    output_files.append(output_file)
                    logger.info("Wrote chunk %d with %d lines to %s",
                                chunk_number, len(chunk_lines), output_file)
                    chunk_number += 1
                    chunk_lines = []

            # If any lines remain (e.g., if no TER at the end), write them as a final chunk.
            if chunk_lines:
                output_file = self._write_chunk(chunk_lines, chunk_number)
                output_files.append(output_file)
                logger.info("Wrote final chunk %d with %d lines to %s",
                            chunk_number, len(chunk_lines), output_file)

        logger.info("Protein-based file splitting complete. Generated %d chunks.", len(output_files))
        return output_files

    def _write_chunk(self, lines: List[str], chunk_number: int) -> Path:
        """
        Writes the provided lines to a chunk file.

        Args:
            lines (List[str]): The lines to write.
            chunk_number (int): The sequential number of the chunk.

        Returns:
            Path: The path to the written chunk file.
        """
        base_name = self.input_file.stem  # Filename without extension.
        output_file_name = f"{base_name}_{chunk_number:03d}.pdb"
        output_file_path = self.output_dir / output_file_name

        with output_file_path.open("w") as outfile:
            outfile.writelines(lines)

        return output_file_path


# TESTING
# Construct the path to your input file
input_file = project_root / "data" / "input" / "1bey.pdb"

fs = FileSplitter(input_file)
fs.split()