# src/main.py

import json
from src.config.config import CONFIG
from src.pipeline.orchestrator import PipelineOrchestrator

def main():
    # Initialize the pipeline orchestrator with the plug-and-play configuration.
    orchestrator = PipelineOrchestrator(CONFIG)
    final_metadata = orchestrator.run_pipeline()
    print("Final ML Metadata:")
    print(json.dumps(final_metadata, indent=4))

if __name__ == "__main__":
    main()
