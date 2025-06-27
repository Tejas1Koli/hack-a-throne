# Legal Document Analyzer

A FastAPI-based backend service for analyzing legal documents. The service extracts text from PDF or DOCX files, splits it into clauses, and analyzes each clause for risk assessment using AI.

## Features

- File upload support for PDF and DOCX documents
- Text extraction and preprocessing
- Clause segmentation using spaCy
- AI-powered risk analysis using OpenRouter API
- Detailed analysis including:
  - Risk score (0-5)
  - Risk explanation
  - Clause type identification
  - Safer rewritten versions
- RESTful API endpoints

## Prerequisites

- Python 3.10+
- pip (Python package manager)
- OpenRouter API key (sign up at [OpenRouter](https://openrouter.ai/))

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd legal-document-analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

3. Use the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### Health Check
- `GET /health` - Check if the API is running

### Document Analysis
- `POST /analyze` - Upload and analyze a legal document
  - **Request**: Form-data with a file (PDF or DOCX)
  - **Response**: JSON with analysis results

## Example Request

```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@document.pdf;type=application/pdf'
```

## Response Format

```json
{
  "clauses": [
    {
      "clause": "Party A shall not be liable for any indirect damages.",
      "risk_score": 2.5,
      "explanation": "This clause limits liability but may be too broad in some jurisdictions.",
      "clause_type": "Liability",
      "safer_version": "Party A's liability for any indirect damages shall be limited to the maximum extent permitted by applicable law."
    }
  ],
  "overall_risk": 2.5
}
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

### Code Style
This project uses `black` for code formatting and `flake8` for linting.

```bash
pip install black flake8
black .
flake8
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.