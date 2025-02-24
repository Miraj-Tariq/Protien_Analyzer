from pathlib import Path
from typing import List, Union, Callable, Optional
from Bio.PDB import PDBParser
from src.utils.logger import logger


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
    deduped = [entries[0]]
    for entry in entries[1:]:
        if entry != deduped[-1]:
            deduped.append(entry)
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
            logger.error("File %s does not exist.", self.file_path)
            raise FileNotFoundError(f"File {self.file_path} does not exist.")
        self.accepted_chains = accepted_chains
        self.deduplicate = deduplicate
        # Default extraction function: extract the 3-letter residue name.
        self.extraction_fn = extraction_fn if extraction_fn is not None else lambda \
            residue: residue.get_resname().strip()
        logger.info("BioPDBExtractor initialized for file: %s", self.file_path)

    def extract(self) -> List[str]:
        """
        Parses the PDB file using Bio.PDB, filters chains based on accepted_chains,
        extracts residue data using extraction_fn, and optionally deduplicates adjacent duplicates.

        Returns:
            List[str]: The list of extracted values.
        """
        parser = PDBParser(QUIET=True)
        try:
            structure = parser.get_structure(self.file_path.stem, str(self.file_path))
        except Exception as e:
            logger.error("Error parsing PDB file: %s", e)
            raise e

        results: List[str] = []
        # Iterate over all models, chains, and residues.
        for model in structure:
            for chain in model:
                if chain.get_id() in self.accepted_chains:
                    for residue in chain:
                        data = self.extraction_fn(residue)
                        if data:
                            results.append(data)
        if self.deduplicate:
            results = deduplicate_adjacent(results)
        logger.info("Extracted %d items from file %s using BioPDBExtractor.", len(results), self.file_path)
        return results


# TESTING
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

# Construct the path to your input file
input_file = project_root / "data" / "temp_chunks" / "1bey_002.pdb"

print(BioPDBExtractor(input_file, accepted_chains=["H", "L"]).extract())