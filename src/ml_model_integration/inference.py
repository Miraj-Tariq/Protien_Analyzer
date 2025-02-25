import json
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Union

import torch
import esm
from src.utils.logger import logger


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
        logger.info("ESMIntegration initialized on device: %s", self.device)

    def load_model(self) -> Tuple[torch.nn.Module, esm.Alphabet]:
        """
        Loads the pre-trained ESM model.

        Returns:
            Tuple[torch.nn.Module, esm.Alphabet]: The loaded model and its alphabet.
        """
        try:
            # Using the ESM-1b model.
            model, alphabet = esm.pretrained.esm1b_t33_650M_UR50S()
            # Optionally, you could trace the model for faster inference:
            # example_input = torch.zeros((1, 10), dtype=torch.long).to(self.device)
            # model = torch.jit.trace(model, example_input)
            logger.info("Loaded ESM-1b model successfully.")
            return model, alphabet
        except Exception as e:
            logger.error("Failed to load ESM model: %s", e)
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
            logger.error("Input JSON file %s does not exist.", json_file)
            raise FileNotFoundError(f"Input JSON file {json_file} does not exist.")

        try:
            with json_file.open("r") as f:
                data = json.load(f)
            extracted = data.get("extracted_chains", {})
            # Prepare batch for tokenization as list of tuples: (chain_id, sequence)
            batch = []
            for chain, info in extracted.items():
                # Convert sequence to uppercase to avoid tokenization issues.
                sequence = info.get("sequence", "").upper()
                batch.append((chain, sequence))
            batch_converter = self.alphabet.get_batch_converter()
            batch_labels, batch_strs, batch_tokens = batch_converter(batch)
            batch_tokens = batch_tokens.to(self.device)
            token_dict = {label: tokens for label, tokens in zip(batch_labels, batch_tokens)}
            logger.info("Preprocessed input from %s into tokenized sequences.", json_file)
            return token_dict
        except Exception as e:
            logger.error("Error during input preprocessing: %s", e)
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
            logger.info("Model inference completed in %.3f seconds.", prediction_time)
            return outputs, prediction_time
        except Exception as e:
            logger.error("Error during model inference: %s", e)
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
        logger.info("Post-processing completed. Metadata: %s", metadata)
        return metadata


# For direct module testing (optional)
if __name__ == "__main__":
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[2]
    output_file = project_root / "data" / "output" / "1bey_output.json"

    esm_ml = ESMIntegration()
    tokenized_output = esm_ml.preprocess_input(output_file)
    output_tensors_dict, prediction_time = esm_ml.run_inference(tokenized_output)
    metadata = esm_ml.post_process(output_tensors_dict, tokenized_output, prediction_time)
    print(metadata)
