# Protein Analyzer

Protein Analyzer is a Python-based data pipeline for processing protein structure files (PDB files). It performs validation, extraction, amino acid mapping, and integrates machine learning models for advanced analysis. This project is designed for bioinformatics researchers and developers working with protein or antibody structural data.

## Features

- **PDB Parsing & Validation:** Reads and validates PDB files, ensuring data integrity.
- **Chain Extraction:** Identifies heavy (H) and light (L) chains (configurable) from PDB files.
- **Amino Acid Mapping:** Converts three-letter amino acid codes to one-letter codes using a mapping file.
- **JSON Output Generation:** Produces structured JSON outputs containing the extracted data.
- **ML Model Integration:**  Executes a machine learning model on the extracted sequences for additional insights.
- **Parallel Processing:** Uses multi-processing for efficient handling of large files.
- **Dockerized Environment:** Fully dockerized for reproducible builds and easy deployment.

## Prerequisites

- **Python 3.7+** (for local installation)
- **Docker & Docker Compose** (for containerized setup)

## Installation

### Local Installation

1. **Clone the Repository:**
```bash
  git clone https://github.com/Miraj-Tariq/Protien_Analyzer.git
  cd Protien_Analyzer
```

2. **Create a Virtual Environment (Recommended):**
```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**
```bash
  pip install -r requirements.txt
```
This installs all required packages, including Biopython and any ML-related dependencies.

4. **Configure Environment Variables:**
Copy the example environment file and update it as needed:
```bash
  cp .env.example .env
```
Update settings such as:
- `INPUT_FILE`: Path to your input PDB file (default: `data/input/1bey.pdb`)
- `OUTPUT_DIR`: Directory for extracted data (default: `data/output/extracted`)
- `INFERENCE_OUTPUT_DIR`: Directory for ML inference results (default: `data/output/inferenced`)
- Other parameters like `ACCEPTED_CHAINS`, `MAX_WORKERS`, etc.

5. **Run Tests (Optional):**
If tests are provided, execute:
```bash
  pytest -v
```

### Docker Installation

The project also includes a Dockerized setup.

1. **Clone the Repository:**
```bash
  git clone https://github.com/Miraj-Tariq/Protien_Analyzer.git
  cd Protien_Analyzer
```

2. **Configure Environment Variables:**

Copy and update the `.env` file:
```bash
  cp .env.example .env
```

3. **Build and Run the Docker Container for Custom Input:**

To run the pipeline in a Docker container for a custom input file, execute:
```bash
  docker build -t protein_analyzer .
  docker run --rm -v "$(pwd):/app" protein_analyzer python src/main.py --input /app/data/input/your_input_file.pdb
```

4. **Accessing Outputs:**

If you want to check the output files, the extracted files are available at `/app/data/output/extracted` and the inferenced files at `/app/data/output/inferenced`.


## Usage

### Running Locally

After installation, run the pipeline with:
```bash
  python src/main.py
```
This processes the PDB file specified in your `.env`, extracts the relevant sequences, and—if configured—executes the ML inference step.

### Running with Docker

With Docker Compose, the pipeline runs automatically on container startup. To view logs:
```bash
  docker-compose logs -f
```
To restart the container:
```bash
  docker-compose down
  docker-compose up --build
```

## Input and Output Details

- **Input:** A single PDB file specified by `INPUT_FILE` in the `.env` (default: `data/input/1bey.pdb`). Ensure your PDB file contains the protein chains you wish to analyze.
- **Output:** JSON files containing the extracted protein chain sequences and metadata stored in location `data/output/extracted/`. ML inference JSON file with prediction results is generated in location `data/output/inferenced/`.

## ML Model Integration

The pipeline includes an ML integration module:
- **Location:** `src/ml_model_integration/inference.py`
- **Purpose:** Run a machine learning model on the extracted sequences for predictions (e.g., protein property analysis).

## Customization Options

The pipeline is configurable via the `.env` file:
- **`INPUT_FILE`** – Path to the input PDB file.
- **`TEMP_CHUNKS_DIR`** – Directory for temporary file chunks.
- **`OUTPUT_DIR`** – Directory for extracted JSON outputs.
- **`INFERENCE_OUTPUT_DIR`** – Directory for ML inference outputs.
- **`MAPPING_FILE`** – Path to the amino acid mapping JSON.
- **`ACCEPTED_CHAINS`** – Comma-separated chain IDs to process (default: `H,L`).
- **`MAX_WORKERS`** – Maximum number of parallel worker processes.
- **`MAX_RETRIES`** – Number of retries for failed tasks.
- **`DEDUPLICATE`** – Boolean flag to remove adjacent duplicate residues (default: `True`).


## Project Structure
```
Protien_Analyzer/
├── docs/                           # Documentation (diagrams, architecture docs, etc.)
├── data/
│   ├── input/                      # Directory for original PDB files
│   ├── output/                     # Generated output files (JSON, etc.)
│   └── temp_chunks/                # Temporarily stored file chunks
├── src/                            # Source code
│   ├── __init__.py
│   ├── config/                     # Configuration management (e.g., config.py, settings.yml)
│   │   ├── __init__.py
│   │   └── config.py
│   ├── file_splitter/              # Module for file splitting & uploading (renamed from file_chunking)
│   │   ├── __init__.py
│   │   └── splitter.py
│   ├── validator/                  # Validation logic (e.g., checking for required atoms)
│   │   ├── __init__.py
│   │   └── validator.py
│   ├── worker_pool/                # Worker management (using ProcessPoolExecutor)
│   │   ├── __init__.py
│   │   └── pool.py
│   ├── extractor/                  # H and L extraction module
│   │   ├── __init__.py
│   │   └── extractor.py
│   ├── mapper/                     # Mapping module for amino acid conversion
│   │   ├── __init__.py
│   │   └── mapper.py
│   ├── output_generator/           # Output file generation (JSON output)
│   │   ├── __init__.py
│   │   └── output.py
│   ├── ml_model_integration/       # AI/ML model integration module
│   │   ├── __init__.py
│   │   └── inference.py
│   ├── pipeline/                   # Orchestrator module to connect all data pipeline modules
│   │   ├── __init__.py
│   │   └── orchestrator.py
│   ├── utils/                      # Utility functions (e.g., file_storage, logger)
│   │   ├── __init__.py
│   │   ├── file_storage.py
│   │   └── logger.py
│   └── main.py                     # The entry point that orchestrates the workflow
├── tests/                          # Test suite mirroring the src structure
│   ├── config/
│   │   └── test_config.py
│   ├── file_splitter/
│   │   └── test_splitter.py
│   ├── validator/
│   │   └── test_validator.py
│   ├── worker_pool/
│   │   └── test_pool.py
│   ├── extractor/
│   │   └── test_extractor.py
│   ├── mapper/
│   │   └── test_mapper.py
│   ├── output_generator/
│   │   └── test_output.py
│   ├── ml_model_integration/
│   │   └── test_inference.py
│   ├── pipeline/
│   │   └── test_orchestrator.py
│   ├── utils/
│   │   ├── test_file_storage.py
│   │   └── test_logger.py
│   └── test_main_pipeline.py
├── .env.example                    # Environment variables for configuration
├── Dockerfile                      # Container build file
├── docker-compose.yml              # Container orchestration file
├── README.md                       # Project overview, setup instructions, etc.
└── requirements.txt                # Python dependencies
```