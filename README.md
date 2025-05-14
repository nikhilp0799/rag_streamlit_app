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
