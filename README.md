# ResumeIQ Pro

Streamlit app that ranks PDF/DOCX resumes by keyword match and generates an AI summary (Gemini or DeepSeek-R1 via OpenRouter).

## Setup

```bash
pip install -r requirements.txt
streamlit run main.py
```

Optional `.env` (pre-fills the API key field):

```
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash        # optional override
OPENROUTER_MODEL=deepseek/deepseek-r1 # optional override
```

## Tests

```bash
pip install pytest
python -m pytest
```

Note: resume text is sent to the selected third-party AI provider when you click "Generate Full Analysis".
