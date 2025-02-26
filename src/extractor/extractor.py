from pathlib import Path
from typing import List, Union, Callable, Optional
from Bio.PDB import PDBParser
from src.utils.logger import get_logger

logger = get_logger(__name__)


def deduplicate_adjacent(entries: List[str]) -> List[str]:
    """
    Removes adjacent duplicate entries from a list.

    Args:
        entries (List[str]): Input list of strings.

    Returns:
        List[str]: List with adjacent duplicates removed.
    """
    if not entries:
        return []

    deduped = []
    prev = None
    for entry in entries:
        if entry != prev:
            deduped.append(entry)
        prev = entry

    return deduped


class BioPDBExtractor:
    """
    A generic extractor that uses Bio.PDB to filter and extract residue data from a PDB file.

    By default, it extracts the 3-letter residue name for each residue from chains whose
    chain identifier is in the accepted list. A custom extraction function can be provided
    for other use cases.

    Attributes:
        file_path (Path): Path to the input PDB file.
        accepted_chains (List[str]): List of chain identifiers to process (e.g., ["H", "L"]).
        deduplicate (bool): Whether to remove adjacent duplicate residue names.
        extraction_fn (Callable): Function to extract desired attribute from a residue.
                                  Defaults to extracting the residue name.
    """

    def __init__(
            self,
            file_path: Union[str, Path],
            accepted_chains: List[str],
            deduplicate: bool = True,
            extraction_fn: Optional[Callable] = None
    ) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            logger.error(f"File {file_path} does not exist.")
            raise FileNotFoundError(f"File {self.file_path} does not exist.")

        self.accepted_chains = accepted_chains
        self.deduplicate = deduplicate
        # Default extraction function: extract the 3-letter residue name.
        self.extraction_fn = extraction_fn if extraction_fn is not None else lambda \
            residue: residue.get_resname().strip()
        logger.info(f"BioPDBExtractor initialized for file: {self.file_path}")

    def extract(self) -> dict:
        """
        Parses the PDB file using Bio.PDB, filters chains based on accepted_chains,
        extracts residue data using extraction_fn, and optionally deduplicates adjacent duplicates
        for each chain.

        Returns:
            dict: A dictionary where keys are chain identifiers (e.g., "H", "L") and values are lists
                  of extracted 3-letter amino acid codes.
        """
        parser = PDBParser(QUIET=True)
        try:
            structure = parser.get_structure(self.file_path.stem, str(self.file_path))
        except Exception as e:
            logger.error(f"Error parsing PDB file: {e}")
            raise e

        results = {}

        # Iterate over all models, chains, and residues.
        for model in structure:
            for chain in model:
                chain_id = chain.get_id()
                if chain_id in self.accepted_chains:
                    if chain_id not in results:
                        results[chain_id] = []
                    for residue in chain:
                        data = self.extraction_fn(residue)
                        if data:
                            results[chain_id].append(data)

        # OPTIONAL: deduplicate each chain's list.
        if self.deduplicate:
            for chain_id in results:
                results[chain_id] = deduplicate_adjacent(results[chain_id])

        logger.info(f"Extracted data for {len(results)} chains from file {self.file_path} using BioPDBExtractor.")
        return results
