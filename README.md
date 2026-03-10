# Loan Agreement Analyzer

An LLM-powered tool that extracts and validates financial terms from loan agreements.

## Features

- 📋 Extract 13+ financial entities (loan amount, interest rate, fees, etc.)
- ✅ Hallucination detection using Levenshtein similarity and TF-IDF
- 🧮 Mathematical validation (EMI × duration ≈ total cost)
- ⚠️ Risk scoring for borrowers (0-10 scale)
- 📝 Plain-language summaries for non-experts
- 💬 WhatsApp/SMS-ready summaries

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: Streamlit
- **LLM**: Llama-3.1-8B-Instruct via HuggingFace Router
- **Validation**: scikit-learn, python-Levenshtein, NLTK

## Local Development

### Prerequisites

- Python 3.11+
- HuggingFace API token

### Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file:
   ```
   HF_TOKEN=your_huggingface_token_here
   ```

4. Run the backend:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

5. Run the frontend:
   ```bash
   streamlit run frontend/app.py
   ```

## Deployment

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `HF_TOKEN=your_token`

### Frontend (Streamlit Cloud)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your repository
4. Set main file path: `frontend/app.py`
5. Add secrets in Streamlit dashboard:
   ```
   API_URL = "https://your-render-backend-url.onrender.com"
   ```

## License

MIT License - GSoC 2026 Prototype
