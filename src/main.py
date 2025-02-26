import argparse
import shutil
import json
from pathlib import Path

from src.config.config import CONFIG
from src.pipeline.orchestrator import PipelineOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Protein Analyzer Pipeline")
    parser.add_argument("--input", type=str, help="Path to the input PDB file", default=None)
    args = parser.parse_args()

    # If the user provides an input file, copy it to the configured input directory.
    if args.input:
        user_input_path = Path(args.input)
        if not user_input_path.exists():
            logger.info(f"Input file {user_input_path} does not exist.")
            return

        # Define target directory based on the current configuration.
        input_dir = CONFIG["input_file"].parent if isinstance(CONFIG["input_file"], Path) else Path(
            CONFIG["input_file"]).parent
        input_dir.mkdir(parents=True, exist_ok=True)
        target_file = input_dir / user_input_path.name

        if user_input_path.resolve() != target_file.resolve():
            shutil.copy(user_input_path, target_file)
            print(f"Input file copied to: {target_file}")
        else:
            print(f"Input file already exists at: {target_file}")

        # Update the configuration's input_file.
        CONFIG["input_file"] = str(target_file)
        logger.info(f"Input file copied to: {target_file}")
    else:
        logger.info("No input file provided; using default from config.")

    orchestrator = PipelineOrchestrator(CONFIG)
    final_metadata = orchestrator.run_pipeline()
    logger.info(json.dumps(final_metadata, indent=4))


if __name__ == "__main__":
    main()
