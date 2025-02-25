import json
import time
from pathlib import Path
from typing import Dict, Any, List

import torch
from src.file_splitter.splitter import FileSplitter
from src.extractor.extractor import BioPDBExtractor
from src.mapper.mapper import Mapper
from src.output_generator.output import OutputFileGenerator
from src.ai_ml_integration.inference import ESMIntegration
from src.worker_pool.pool import WorkerPool
from src.utils.logger import logger

class PipelineOrchestrator:
    """
    Orchestrates the complete Protein Analyzer data pipeline.

    The pipeline proceeds in the following stages:
      1. File Splitting: Split the input PDB file into chunks.
      2. Extraction: Process each chunk using BioPDBExtractor to extract chain-specific residue codes.
         Parallel processing is applied via the WorkerPool.
      3. Merge Extractions: Combine extraction results from all chunks.
      4. Mapping: Convert 3-letter codes to 1-letter codes using Mapper.
      5. Output Generation: Generate a JSON file with metadata.
      6. ML Integration: Preprocess the JSON output and run model inference.
    """
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.input_file = Path(config["input_file"])
        self.temp_chunks_dir = Path(config["temp_chunks_dir"])
        self.output_dir = Path(config["output_dir"])
        self.mapping_file = Path(config["mapping_file"])
        self.checkpoints: Dict[str, Any] = {}
        # Ensure directories exist.
        self.temp_chunks_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("PipelineOrchestrator initialized with config: %s", self.config)

    def run_pipeline(self) -> Dict[str, Any]:
        # Stage 1: File Splitting.
        chunk_files = self.split_file()
        self.checkpoints["file_splitting"] = f"{len(chunk_files)} chunks generated."
        logger.info("File splitting completed: %s", self.checkpoints["file_splitting"])

        # Stage 2: Extraction via Worker Pool.
        extraction_results = self.extract_chunks(chunk_files)
        self.checkpoints["extraction"] = "Extraction completed for all chunks."
        logger.info("Extraction completed: %s", self.checkpoints["extraction"])

        # Stage 3: Merge Extraction Results.
        merged_extraction = self.merge_extraction_results(extraction_results)
        logger.info("Merged extraction results: %s", merged_extraction)

        # Stage 4: Mapping.
        mapper = Mapper(self.mapping_file)
        mapped_sequences = mapper.one_to_one_mapping(merged_extraction)
        self.checkpoints["mapping"] = "Mapping completed."
        logger.info("Mapping completed: %s", mapped_sequences)

        # Stage 5: Output File Generation.
        output_generator = OutputFileGenerator(output_dir=self.output_dir)
        output_json_path = output_generator.generate_output_file(
            input_filename=self.input_file.name,
            extracted_chains=mapped_sequences
        )
        self.checkpoints["output_generation"] = f"Output file generated at {output_json_path}"
        logger.info("Output file generation completed: %s", self.checkpoints["output_generation"])

        # Stage 6: ML Integration.
        esm_integration = ESMIntegration()
        tokenized_inputs = esm_integration.preprocess_input(output_json_path)
        output_tensors, pred_time = esm_integration.run_inference(tokenized_inputs)
        ml_metadata = esm_integration.post_process(output_tensors, tokenized_inputs, pred_time)
        self.checkpoints["ml_integration"] = "ML integration completed."
        logger.info("ML integration completed. Final metadata: %s", ml_metadata)

        logger.info("Pipeline completed. Checkpoints: %s", self.checkpoints)
        return ml_metadata

    def split_file(self) -> List[Path]:
        splitter = FileSplitter(
            input_file=str(self.input_file),
            output_dir=str(self.temp_chunks_dir)
        )
        chunk_files = splitter.split()
        return chunk_files

    def extract_chunks(self, chunk_files: List[Path]) -> List[Dict[str, List[str]]]:
        def extract_from_chunk(chunk_file_path: str) -> Dict[str, List[str]]:
            extractor = BioPDBExtractor(
                file_path=chunk_file_path,
                accepted_chains=self.config["accepted_chains"],
                deduplicate=self.config.get("deduplicate", True)
            )
            return extractor.extract()

        worker_pool = WorkerPool(
            max_workers=self.config.get("max_workers", 4),
            max_retries=self.config.get("max_retries", 3)
        )
        base_address = str(self.temp_chunks_dir / self.input_file.stem)
        total_files = len(chunk_files)
        extraction_results = worker_pool.process_chunks(
            base_address=base_address,
            total_files=total_files,
            processing_function=extract_from_chunk
        )
        successful_results = []
        for file_name, result in extraction_results.items():
            if isinstance(result, dict):
                successful_results.append(result)
            else:
                logger.error("Extraction failed for %s: %s", file_name, result)
        return successful_results

    def merge_extraction_results(self, results: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
        merged: Dict[str, List[str]] = {}
        for result in results:
            for chain, codes in result.items():
                if chain not in merged:
                    merged[chain] = []
                merged[chain].extend(codes)
        return merged
