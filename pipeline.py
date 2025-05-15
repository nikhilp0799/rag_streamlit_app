import os
import requests
import pandas as pd
import logging
import json
from bs4 import BeautifulSoup

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
load_dotenv()


# Set API key
openai_api_key = os.getenv("OPENAI_API_KEY")


logging.basicConfig(level=logging.INFO)

# Get CIK from ticker
def get_cik_from_ticker(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "Nikhil Pandey (Northeastern University) pandey.nikh@northeastern.edu"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise ValueError("Failed to fetch ticker-to-CIK mapping.")
    data = res.json()
    for entry in data.values():
        if entry['ticker'].upper() == ticker.upper():
            return str(entry['cik_str']).zfill(10)
    raise ValueError(f"CIK not found for ticker '{ticker}'")

# Fetch 10-K and 8-K filings
def get_edgar_filings(cik, count=10):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": "Nikhil Pandey (Northeastern University) pandey.nikh@northeastern.edu"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch filings for CIK {cik}")
    filings = res.json().get("filings", {}).get("recent", {})
    df = pd.DataFrame(filings)
    df = df[df["form"].isin(["10-K", "8-K"])].head(count)
    return df[["accessionNumber", "reportDate", "primaryDocument", "form"]]

# Build filing URLs
def query_sec_filings(ticker):
    cik = get_cik_from_ticker(ticker)
    df = get_edgar_filings(cik)
    filings = []
    for _, row in df.iterrows():
        accession = row["accessionNumber"].replace("-", "")
        doc = row["primaryDocument"]
        form = row["form"]
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{doc}"
        filings.append({
            "type": form,
            "date": row["reportDate"],
            "url": url
        })
    return filings

# Download and extract plain text from filing URL
def extract_text_from_url(url):
    headers = {"User-Agent": "Nikhil Pandey (Northeastern University) pandey.nikh@northeastern.edu"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["script", "style"]): tag.decompose()
        return soup.get_text(separator=" ", strip=True)
    return ""

# Split into chunks for RAG
def preprocess_and_chunk(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_text(text)

# Create FAISS store
def create_vector_store(chunks):
    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(chunks, embeddings)

# RAG pipeline to extract drug/asset data
def extract_drug_information(vectorstore, query):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="map_reduce",
        return_source_documents=True
    )
    result = rag_chain.invoke({"query": query})
    return result["result"]

# Format final output
def format_output_to_table(data):
    df = pd.DataFrame(data)
    df.to_csv("drug_asset_summary.csv", index=False)
    try:
        import tabulate
        with open("drug_asset_summary.md", "w") as f:
            f.write(df.to_markdown())
    except ImportError:
        logging.warning("tabulate not installed")
    return df

# Final pipeline
def main_pipeline(ticker):
    filings = query_sec_filings(ticker)
    all_data = []

    for filing in filings:
        text = extract_text_from_url(filing["url"])
        if not text:
            continue

        chunks = preprocess_and_chunk(text)
        vs = create_vector_store(chunks)

        query = (
            f"You are reading a {filing['type']} SEC filing dated {filing['date']} "
            f"from the biotechnology company {ticker}. Extract all real drug or asset "
            "development programs. Return a JSON list of dicts with keys: "
            "'Name/Number', 'Mechanism of Action', 'Target', 'Indication', "
            "'Animal Models/Preclinical Data', 'Clinical Trials', 'Upcoming Milestones', 'References'. "
            f"Include the filing type, date, and section if known in the 'References' field. "
            "No commentary, just JSON."
        )

        try:
            raw_output = extract_drug_information(vs, query).strip()
            if raw_output.startswith("```json"):
                raw_output = raw_output.removeprefix("```json").strip()
            if raw_output.endswith("```"):
                raw_output = raw_output.removesuffix("```").strip()
            parsed = json.loads(raw_output)

            for entry in parsed:
                if "Name/Number" in entry:
                    entry["Name/Number"] = f"{ticker.upper()} / {entry['Name/Number']}"
                if "References" in entry:
                    entry["References"] += f" — {filing['type']} on {filing['date']}"
            all_data.extend(parsed)

        except Exception as e:
            logging.error(f"Failed to process filing {filing['url']} — {e}")

    if not all_data:
        logging.warning("No valid data extracted.")
        return

    # Optional: Deduplicate by Name/Number
    unique = {}
    for row in all_data:
        key = row["Name/Number"]
        if key in unique:
            for k in row:
                if k != "Name/Number" and row[k] not in unique[key][k]:
                    unique[key][k] += f" | {row[k]}"
        else:
            unique[key] = row

    return format_output_to_table(list(unique.values()))

# Run multiple tickers
if __name__ == "__main__":
    ticker = input("Enter a valid biotech stock ticker (e.g., ALNY, GILD, WVE): ").strip().upper()

    if not ticker:
        print("⚠️ No ticker entered. Exiting.")
        exit()

    try:
        logging.info(f"Processing ticker: {ticker}")
        df = main_pipeline(ticker)
        if df is not None:
            df.to_csv(f"{ticker}_drug_asset_summary.csv", index=False)
            print(f" Results saved for {ticker} in '{ticker}_drug_asset_summary.csv'")
        else:
            print(f"⚠️ No data returned for {ticker}.")
    except Exception as e:
        logging.error(f" Error while processing ticker {ticker}: {e}")


