# Legal Document Analyzer - Frontend

A Streamlit-based web interface for the Legal Document Analyzer. This frontend allows users to upload legal documents (PDF/DOCX) and view detailed risk analysis reports.

## Features

- Modern, responsive web interface
- Drag-and-drop file upload
- Real-time analysis progress tracking
- Interactive visualizations of risk scores
- Detailed clause-by-clause analysis
- Suggested improvements for problematic clauses
- Summary statistics and risk distribution

## Prerequisites

- Python 3.10+
- Backend API running (see main README for setup)

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your configuration:
   ```env
   # API configuration
   API_BASE_URL=http://localhost:8000/api/v1
   ```

## Running the Application

1. Ensure the backend API is running (default: http://localhost:8000)

2. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Usage

1. **Upload a Document**:
   - Click "Browse files" in the sidebar or drag and drop a PDF or DOCX file
   - Supported file types: .pdf, .docx

2. **Analyze the Document**:
   - Click the "Analyze Document" button
   - View the progress bar as the document is processed

3. **Review Results**:
   - See the overall risk score and interpretation
   - Switch between "Detailed View" and "Summary" tabs
   - Expand individual clauses to see suggestions and explanations

4. **View Visualizations**:
   - Check the risk distribution pie chart
   - See risk scores by clause type (if applicable)

## Project Structure

```
frontend/
├── app.py              # Main Streamlit application
├── utils.py            # Utility functions and API client
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Troubleshooting

- **API Connection Issues**: Ensure the backend API is running and accessible at the URL specified in `.env`
- **File Upload Problems**: Verify the file is not corrupted and is one of the supported formats
- **Missing Dependencies**: Run `pip install -r requirements.txt` to ensure all dependencies are installed

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
