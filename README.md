project_root/
├── docs/                           # Documentation (diagrams, architecture docs, etc.)
├── input/                          # Directory for original PDB files
├── ml_data/                        # ML pre-training or preprocessed data files
├── output/                         # Generated output files (JSON, etc.)
├── temp_chunks/                    # Temporarily stored file chunks
├── src/                            # Source code
│   ├── __init__.py
│   ├── config/                     # Configuration management (e.g., config.py, settings.yml)
│   │   ├── __init__.py
│   │   └── config.py
│   ├── file_splitter/              # Module for file splitting & uploading (renamed from file_chunking)
│   │   ├── __init__.py
│   │   └── splitter.py
│   ├── parser/                     # Parsing logic using BioPython
│   │   ├── __init__.py
│   │   └── parser.py
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
│   ├── ai_ml_integration/          # AI/ML model integration module
│   │   ├── __init__.py
│   │   └── inference.py
│   └── main_pipeline.py            # The entry point that orchestrates the workflow
├── tests/                          # Test suite mirroring the src structure
│   ├── config/
│   │   └── test_config.py
│   ├── file_splitter/
│   │   └── test_splitter.py
│   ├── parser/
│   │   └── test_parser.py
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
│   ├── ai_ml_integration/
│   │   └── test_inference.py
│   └── test_main_pipeline.py
├── .env                            # Environment variables for configuration
├── Dockerfile                      # Container build file
├── docker-compose.yml              # Container orchestration file
├── README.md                       # Project overview, setup instructions, etc.
└── requirements.txt                # Python dependencies
