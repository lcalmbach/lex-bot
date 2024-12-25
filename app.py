import streamlit as st
import lex

if st.button("Load"):
    lex = lex.Loader()
    with st.spinner("Writing data to parquet file"):
        lex.data.to_parquet("data.parquet")