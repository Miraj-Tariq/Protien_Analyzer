import json
from src.config.config import CONFIG
from src.pipeline.orchestrator import PipelineOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    orchestrator = PipelineOrchestrator(CONFIG)
    final_metadata = orchestrator.run_pipeline()
    logger.info(f"Final ML Metadata: \n{json.dumps(final_metadata, indent=4)}")

if __name__ == "__main__":
    main()
