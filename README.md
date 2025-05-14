# 🔍 rag_streamlit_app

> **SEC Drug Asset Extraction Pipeline using LangChain + OpenAI + Streamlit**

This application extracts structured drug development information directly from SEC 10-K and 8-K filings using a Retrieval-Augmented Generation (RAG) pipeline. It provides a clean Streamlit front-end to run the pipeline, view the data, and download results in CSV and Markdown formats.

---

## 📌 Features

- 🔎 Retrieves and processes recent **10-K and 8-K SEC filings** for any biotechnology stock ticker.
- ✂️ Chunks text using `RecursiveCharacterTextSplitter`.
- 🧠 Uses **LangChain + OpenAI** (via FAISS and ChatOpenAI) to extract structured drug program data.
- 📊 Interactive **Streamlit UI** to input tickers, view results, and download CSV/Markdown.
- ☁️ (Optional) **S3 integration** to store outputs persistently in AWS.

---

## 🧪 Sample Use Case

> Extract all drug development programs from recent SEC filings for `VRTX`.

```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://<EC2_PUBLIC_IP>:8501`, enter a ticker (e.g., `VRTX`), and view structured results like:

| Name/Number     | Mechanism of Action | Target        | Clinical Trials | References            |
|----------------|---------------------|---------------|-----------------|------------------------|
| VRTX / Program X | CFTR potentiator    | CFTR protein  | Phase 3 ongoing | 10-K filing on 2024-12 |
| VRTX / VX-864    | FXR agonist         | Farnesoid X   | Preclinical     | 10-K filing on 2024-12 |

---

## 🚀 Tech Stack

| Layer        | Tool / Framework         |
|--------------|---------------------------|
| 🧠 LLM        | OpenAI GPT (via LangChain) |
| 📚 RAG Engine | FAISS + LangChain         |
| 🔎 Retrieval  | EDGAR SEC Filings API     |
| 🖥 Frontend   | Streamlit                 |
| ☁️ Hosting    | AWS EC2                   |

---

## 🛠 Installation

### 1. Clone the repo

```bash
git clone https://github.com/nikhilp0799/rag_streamlit_app.git
cd rag_streamlit_app
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your OpenAI key

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
```

> ✅ `.env` is already gitignored.

---

## 🧠 How It Works

- Fetches 10-K/8-K filing URLs from EDGAR using ticker → CIK mapping.
- Downloads HTML filings, removes noise using BeautifulSoup.
- Splits filings into semantic chunks.
- Embeds into FAISS vector store.
- Queries with a JSON-format prompt to extract asset-level program info.
- Outputs results as a clean CSV and Markdown file.

---

## 🖼 Streamlit UI

- Input box for stock ticker
- Displays:
  - ✅ Extraction summary
  - 📊 Table of programs
  - 📎 Download buttons (CSV, Markdown)
  - 📝 Markdown preview (expandable)

---

## ☁️ (Optional) AWS S3 Integration

You can upload CSV/Markdown results to S3 by adding this snippet in `pipeline.py`:

```python
import boto3
s3 = boto3.client("s3")
s3.upload_file("drug_asset_summary.csv", "your-bucket", "file.csv")
```

> Add IAM credentials via `aws configure` or use EC2 IAM role.

---

## 📁 Project Structure

```
├── pipeline.py           # Core RAG + SEC pipeline
├── streamlit_app.py      # Frontend (Streamlit)
├── requirements.txt      # All dependencies
├── .env                  # API key (not pushed to GitHub)
├── .gitignore            # Ignores sensitive files
└── README.md             # Project description
```

---

## 📣 Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain)
- [OpenAI API](https://platform.openai.com/)
- [EDGAR SEC Filings](https://www.sec.gov/edgar.shtml)
- [Streamlit](https://streamlit.io)

---
