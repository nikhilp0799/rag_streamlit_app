import streamlit as st
import pandas as pd
from pipeline import main_pipeline  # Import your main_pipeline function

# Stylish header
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🔍 SEC Drug Program Extractor</h1>",
    unsafe_allow_html=True
)

# Sidebar input
with st.sidebar:
    st.header(" Input Settings")
    if "ticker" not in st.session_state:
        st.session_state.ticker = ""
    ticker = st.text_input("Enter a biotech stock ticker (e.g., WVE, ALNY)", value=st.session_state.ticker)
    st.session_state.ticker = ticker

# Main logic
if ticker and st.button("Run Pipeline"):
    with st.spinner("⏳ Running pipeline, extracting data..."):
        df = main_pipeline(ticker.upper())
        st.session_state.df = df
        st.session_state.md_text = None

        if df is not None and not df.empty:
            try:
                st.session_state.md_text = df.to_markdown(index=False)
            except Exception:
                st.session_state.md_text = "⚠️ Markdown generation failed."

# Load from session
df = st.session_state.get("df")
md_text = st.session_state.get("md_text")

if df is not None and not df.empty:
    st.success("Extraction complete!")

    # Show summary metrics
    col1, col2 = st.columns(2)
    col1.metric("Programs Found", len(df))
    col2.metric("Ticker", st.session_state.ticker.upper())

    # Show data
    st.subheader("📊 Drug Development Summary")
    st.dataframe(df, use_container_width=True)

    # Download buttons
    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False),
        file_name=f"drug_summary_{st.session_state.ticker.upper()}.csv",
        mime="text/csv"
    )

    if md_text:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "📘 Download Markdown",
            md_text,
            file_name=f"drug_summary_{st.session_state.ticker.upper()}.md",
            mime="text/markdown"
        )

        # Keep original Markdown preview untouched
        with st.expander("📝 Markdown Preview"):
            st.code(md_text, language='markdown')

else:
    if ticker:
        st.warning("⚠️ No data found. Please try another ticker.")
