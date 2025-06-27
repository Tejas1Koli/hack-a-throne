# Legal Document Analyzer

A full-stack application for analyzing legal documents, built with a FastAPI backend and Streamlit frontend. The service extracts text from PDF or DOCX files, splits it into clauses, and provides AI-powered risk assessment and suggestions.

## Features

### Backend (FastAPI)
- File upload support for PDF and DOCX documents
- Text extraction and preprocessing
- Clause segmentation using spaCy
- AI-powered risk analysis using OpenRouter API
- Detailed analysis including:
  - Risk score (0-5)
  - Risk explanation
  - Clause type identification
  - Safer rewritten versions
- Comprehensive error handling and logging (logs in `app.log` with rotation)
- API documentation with Swagger UI

### Frontend (Streamlit)
- Modern, responsive user interface
- Document upload and analysis
- Interactive visualization of risk scores
- Detailed clause-by-clause analysis
- Suggested safer versions for risky clauses
- Improved error handling and user feedback

## Recent Improvements (2025-06)
- **Frontend and backend integration fixed**: Frontend now connects to backend on the correct port (8001), with `.env` configuration (`API_BASE_URL`).
- **Frontend UI/UX improved**: Risk scores, clause details, and suggestions are shown in a modern, organized layout with tabs and progress bars.
- **Backend error handling enhanced**: More descriptive errors and logs, better propagation of issues to the frontend.
- **Logging**: All backend logs are saved to `app.log` (rotated up to 5 files), for easier debugging.
- **API health check**: Frontend checks backend health before allowing uploads.
- **File type validation**: Only PDF and DOCX are accepted; others are rejected with clear errors.

## Prerequisites

- Python 3.10+
- pip (Python package manager)
- OpenRouter API key (sign up at [OpenRouter](https://openrouter.ai/))

## Backend Installation & Usage

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hack-a-throne
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

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

6. The API will be available at `http://localhost:8001/api/v1`
   - Swagger docs: `http://localhost:8001/docs`

## Frontend Installation & Usage

1. Go to the frontend directory:
   ```bash
   cd frontend
   ```
2. (Optional) Create a virtual environment for the frontend as well.
3. Install frontend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the example environment file:
   ```bash
   cp .env.example .env
   # Ensure API_BASE_URL is set to http://localhost:8001/api/v1
   ```
5. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
6. Access the UI at `http://localhost:8501`

## API Endpoints

### Health Check
- `GET /api/v1/health` - Check if the API is running

### Document Analysis
- `POST /api/v1/analyze` - Upload and analyze a legal document
  - **Request**: Form-data with a file (PDF or DOCX)
  - **Response**: JSON with analysis results

## Example Request

```bash
curl -X 'POST' \
  'http://localhost:8001/api/v1/analyze' \
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

## Troubleshooting

- **"Failed to analyze the document"**: Check backend logs in `app.log` for errors. Ensure backend is running and accessible at the correct port.
- **Timeouts or 500 errors**: Make sure you are uploading valid PDF or DOCX files. Large or malformed files may cause errors.
- **Frontend not connecting**: Verify `API_BASE_URL` in `frontend/.env` is set to `http://localhost:8001/api/v1`.
- **OpenRouter API errors**: Ensure your API key is set and valid in the backend `.env` file.

## Logging
- All backend logs are written to `app.log` (rotated up to 5 files, 10MB each).
- Check these logs for debugging backend issues.

## Development & Testing
- Backend and frontend can be run independently for development.
- Use the provided API docs (`/docs`) for backend testing.
- Frontend provides a user-friendly interface for uploading and analyzing documents.

---

If you encounter any issues, please check the logs and configuration files first. For further help, open an issue or contact the maintainers.


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