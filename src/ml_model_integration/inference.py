import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Union

import torch
import esm

from src.utils.file_storage import store_data
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ESMIntegration:
    """
    A class that integrates the ESM model for protein sequence embedding extraction.

    Tasks:
      - Load a pre-trained ESM model and its alphabet.
      - Preprocess input from a JSON output file into tokenized sequences.
      - Run model inference to extract embeddings and measure prediction time.
      - Post-process the outputs to generate predictions and collate metadata.
    """

    def __init__(self) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model, self.alphabet = self.load_model()
        self.model.to(self.device)
        self.model.eval()
        logger.info(f"ESMIntegration initialized on device: {self.device}")

    def load_model(self) -> Tuple[torch.nn.Module, esm.Alphabet]:
        """
        Loads the pre-trained ESM model.

        Returns:
            Tuple[torch.nn.Module, esm.Alphabet]: The loaded model and its alphabet.
        """
        try:
            # Using the ESM-1b model.
            model, alphabet = esm.pretrained.esm1b_t33_650M_UR50S()

            logger.info("Loaded ESM-1b model successfully.")
            return model, alphabet
        except Exception as e:
            logger.error(f"Failed to load ESM model: {e}")
            raise e

    def preprocess_input(self, json_file: Union[str, Path]) -> Dict[str, torch.Tensor]:
        """
        Reads the JSON output file to extract sequences for chains and tokenizes them.

        Args:
            json_file (Union[str, Path]): Path to the JSON file from Output File Generation.

        Returns:
            Dict[str, torch.Tensor]: A dictionary mapping chain identifiers to tokenized input tensors.
        """
        json_file = Path(json_file)
        if not json_file.exists():
            logger.error(f"Input JSON file {json_file} does not exist.")
            raise FileNotFoundError(f"Input JSON file {json_file} does not exist.")

        try:
            with json_file.open("r") as f:
                data = json.load(f)
            extracted = data.get("extracted_chains", {})

            # Prepare batch for tokenization as list of tuples: (chain_id, sequence)
            batch = []
            for chain, info in extracted.items():
                if isinstance(info, dict):
                    # If info is a dict (with a "sequence" key)
                    sequence = info.get("sequence", "").upper()
                elif isinstance(info, list):
                    # If info is a list, join the list items to form a single sequence string.
                    sequence = "".join(info).upper()
                else:
                    sequence = ""
                batch.append((chain, sequence))

            # Get the batch converter from the alphabet.
            batch_converter = self.alphabet.get_batch_converter()
            batch_labels, batch_strs, batch_tokens = batch_converter(batch)

            # Move tokens to the correct device.
            batch_tokens = batch_tokens.to(self.device)

            # Create a dict mapping chain IDs to their tokens.
            token_dict = {label: tokens for label, tokens in zip(batch_labels, batch_tokens)}

            logger.info(f"Preprocessed input from {json_file} into tokenized sequences.")
            return token_dict
        except Exception as e:
            logger.error(f"Error during input preprocessing: {e}")
            raise e

    def run_inference(self, tokenized_inputs: Dict[str, torch.Tensor]) -> Tuple[Dict[str, torch.Tensor], float]:
        """
        Runs model inference on the tokenized inputs and measures prediction time.

        Args:
            tokenized_inputs (Dict[str, torch.Tensor]): Dictionary of tokenized inputs per chain.

        Returns:
            Tuple[Dict[str, torch.Tensor], float]: A dictionary mapping chain IDs to output tensors and
                                                   the total prediction time in seconds.
        """
        outputs = {}
        start_time = time.time()
        try:
            with torch.no_grad(), torch.amp.autocast(device_type=self.device.type):
                for chain, tokens in tokenized_inputs.items():
                    # Ensure tokens are 2D; if 1D, add a batch dimension.
                    if tokens.ndim == 1:
                        tokens = tokens.unsqueeze(0)
                    output = self.model(tokens, repr_layers=[33], return_contacts=False)
                    outputs[chain] = output["representations"][33]

            prediction_time = time.time() - start_time

            logger.info(f"Model inference completed in {prediction_time} seconds.")
            return outputs, prediction_time
        except Exception as e:
            logger.error(f"Error during model inference: {e}")
            raise e

    def post_process(
        self,
        output_tensors: Dict[str, torch.Tensor],
        tokenized_inputs: Dict[str, torch.Tensor],
        prediction_time: float
    ) -> Dict[str, Any]:
        """
        Post-processes model outputs to generate final predictions and collate metadata.

        For demonstration, this function derives a dummy predicted sequence by taking the argmax
        along the feature dimension of the first token as a placeholder.

        Args:
            output_tensors (Dict[str, torch.Tensor]): Dictionary of output tensors from the model.
            tokenized_inputs (Dict[str, torch.Tensor]): Original tokenized inputs.
            prediction_time (float): Time taken for model inference.

        Returns:
            Dict[str, Any]: A structured metadata dictionary containing:
                - prediction_time (float)
                - original_tokens (dict): Mapping chain -> token tensor shape info
                - model_output (dict): Mapping chain -> output tensor shape info
                - predicted_sequence (dict): Mapping chain -> dummy predicted result (as string)
        """
        predictions = {}
        for chain, tensor in output_tensors.items():
            pred_indices = tensor[0].argmax(dim=-1).tolist()
            predicted_seq = "".join([str(idx % 26 + 65) for idx in pred_indices])
            predictions[chain] = predicted_seq

        original_tokens = {chain: tokens.shape for chain, tokens in tokenized_inputs.items()}
        model_output_info = {chain: tensor.shape for chain, tensor in output_tensors.items()}

        metadata = {
            "prediction_time": prediction_time,
            "original_tokens": original_tokens,
            "model_output": model_output_info,
            "predicted_sequence": predictions
        }

        logger.info(f"Post-processing completed. Metadata: {metadata}")
        return metadata

    def store_metadata(self, metadata: Dict[str, Any], output_dir: Union[str, Path]) -> Path:
        """
        Stores the metadata as a JSON file in the 'src/data/output/inferenced/' directory.

        Args:
            metadata (Dict[str, Any]): The metadata to store.
            filename (str): Optional filename; if not provided, a timestamped name is used.

        Returns:
            Path: The path to the stored metadata file.
        """
        output_file_name = f"{os.environ.get('file_base_name')}_inferenced_output.json"
        output_path = output_dir / output_file_name

        return store_data(metadata, output_path, format="json")
