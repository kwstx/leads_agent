# Engram Lead Discovery & Enrichment System

A fully automated, global lead discovery and enrichment system specifically designed for **Engram**.

## Architecture
The system is built as a modular pipeline:
1.  **Collection**: Fetches raw data from GitHub and Reddit based on configurable queries.
2.  **Processing**: Deduplicates and cleans raw leads.
3.  **Categorization**: Tags leads based on content (e.g., AI/ML, DevOps).
4.  **Enrichment**: Adds contact information and profile metadata.
5.  **Scoring**: Ranks leads by intent score using weighted keywords.
6.  **Output**: Exports the final lead list to CSV.

## Project Structure
- `src/collectors/`: Modules for data acquisition.
- `src/processors/`: Data cleaning and tagging.
- `src/enrichers/`: Contact discovery and profiling.
- `src/scorers/`: Intent analysis and scoring.
- `src/schema/`: Unified Pydantic data models.
- `src/utils/`: Shared utilities (config, logging).

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

## Usage
Run the main pipeline:
```bash
python main.py --query "agentic ai issues" --limit 10
```

Intermediate and final data can be found in the `data/` directory.

## License
MIT
