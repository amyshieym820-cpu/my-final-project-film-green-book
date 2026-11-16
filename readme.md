# Film Green Book · Art Department Carbon Calculator

A Streamlit web application for film and theatre art departments to estimate and reduce the carbon and water footprint of props and set materials.

## Project Structure

```text
├── App.py                 # Main Streamlit application
├── factors.py             # Carbon & water emission factors and thresholds
├── requirements.txt       # Python dependencies
├── readme.md              # Documentation and deployment guide
└── .streamlit/
    └── config.toml        # UI theme configuration (#0E3B2C)
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run App.py
```

## Deploy on GitHub + Streamlit Community Cloud

1. Push all files (`App.py`, `factors.py`, `requirements.txt`, `readme.md`, and `.streamlit/config.toml`) to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Click **New app**, select your repository, set **Main file path** to `App.py`, and click **Deploy**.
