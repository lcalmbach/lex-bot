import streamlit as st
import pandas as pd
import os
import re
import openai

from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA
import csv
import json
from time import sleep
from streamlit_tree_select import tree_select
import chromadb.api
from pathlib import Path
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from langchain_core.documents import Document

from helper import clean_folder
import texts

import pysqlite3
import sys
sys.modules["sqlite3"] = pysqlite3

# Feldgrößen-Limit deutlich heraufsetzen (z.B. auf sys.maxsize)
csv.field_size_limit(2**31 - 1)
openai.api_key  = os.environ['OPENAI_API_KEY']
persist_directory = './docs/chroma/'
parquet_file = Path("./100354.parquet")
csv_file = Path("./100354.csv")


class Lex():
    def __init__(self):
        self.url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/100354/exports/csv?lang=de&timezone=Europe%2FBerlin&use_labels=false&delimiter=%7C"
        #if Path(parquet_file).is_file():
        #    self.data = pd.read_parquet(parquet_file)
        #else:
        self.data = self.load_data(force=False)
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=OpenAIEmbeddings(),
        )
        self.hierarchy = self.get_hierarchy_tree()
        

    def get_hierarchy_tree(self):
        if Path("rechtsgebiet.json").is_file():
            with open("rechtsgebiet.json", "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            level1_lst = ['1','2','3','4','5','6','7','8','9'] # ,'BaB', 'BeE', 'BeE', 'RiB', 'RiE'
            tree = []
            for level1 in level1_lst:
                level1_row = self.data.reset_index()[self.data['identifier']==level1].iloc[0]
                node = {"label": level1_row["title"], "value": str(level1_row["index"]), "children": []}
                tree.append(node)
                level2_rows = self.data.reset_index()[
                    (self.data['identifier'].str.startswith(level1_row['identifier'])) & (self.data['identifier'].str.len() == 2)
                ].sort_values(by='identifier', ascending=True)
                if len(level2_rows)>0:
                    for index, level2_row in level2_rows.iterrows():
                        level2_node = {"label": level2_row["title"], "value": str(index), "children": []}
                        node["children"].append(level2_node)
                        level3_rows = self.data.reset_index()[
                            (self.data['identifier'].str.startswith(level2_row['identifier'])) & (self.data['identifier'].str.len() == 3)
                        ].sort_values(by='identifier', ascending=True)
                        if len(level3_rows)>0:
                            for index, level3_row in level3_rows.iterrows():
                                level3_node = {"label": level3_row["title"], "value": str(index), "children": []}
                                level2_node["children"].append(level3_node)
                
            with open("rechtsgebiet.json", "w", encoding="utf-8") as file:
                json.dump(tree, file, ensure_ascii=False, indent=4) 
            return tree


    def load_data(self, force:bool=False)->bool:
        def rename_columns():
            df.rename(columns={'index': 'lex_index'}, inplace=True)
            df['identifier'] = df['identifier'].astype(str)
        if parquet_file.is_file() and not force:
            df = pd.read_parquet(parquet_file)
            rename_columns
            return df
        else:
            df = pd.read_csv(self.url, delimiter='|', engine='python')
            df = self.clean_all_texts(df)
            rename_columns()
            self.embed_text(df)
            df.to_parquet(parquet_file, index=False)
            df.to_csv(csv_file, index=False)
            return df
        

    def clean_all_texts(self, data):
        def clean_text(text):
            text = re.sub(r'(?m)^\s*\n', '', text)
            # 1) Leere (oder nur mit Whitespace gefüllte) Zeilen entfernen
            text = re.sub(r'(?m)^[ \t]*\n', '', text)
            
            # whitespaces am Beginn der Zeile entfernen
            text = re.sub(r'(?m)^[ \t]+', '', text)
            # 2) Zeilen zusammenführen, wenn sie z.B. mit "1." oder "1)" oder "a)" aufhören
            text = re.sub(r'(?m)^(\d+|§ \d+|\d+\.|\d+\)|[a-z]\))\s*\n', r'\1 ', text)
            return text

        for index, row in data.iterrows():
            text = row['text_of_law']
            if pd.notnull(text) and str(text).strip():
                text = str(text)
                cleaned_text = clean_text(text)
                data.loc[index,'text_of_law'] = cleaned_text
        return data
    
    def embed_text(self, data):
        # Clean persist directory (optional)
        clean_folder(Path(persist_directory))
        embedding_model = OpenAIEmbeddings()
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        documents = []
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
        cnt=1
        for index, row in data.reset_index().iterrows():
            if pd.notnull(row['txt_filename']) and str(row['txt_filename']).strip():
                print(f"Adding documents {row['title_de'][:50]} {cnt}/{len(data)} to vectorstore")
                chunks = row['text_of_law'].split("\n§")
                ids = []
                documents = []
                id = 1
                for chunk in chunks:
                    document = Document(page_content='§' + chunk.strip(), metadata={"id": f"{str(index)}-{id}", "doc": str(index)})
                    documents.append(document)
                    ids.append(f"{str(index)}-{id}")
                    id+=1
                vectorstore.add_documents(documents=documents, ids=ids)
                sleep(1)
            cnt+=1

    def get_vectorstore_content(self):
        return self.vectorstore.get()

    def get_embeddings(self):
        result = self.vectorstore.get(include=["documents", "embeddings", "metadatas"])
        st.write(result["embeddings"][0])
        
    def show_info(self):
        st.markdown(texts.info.format(len(self.data)))

    def show_stats(self):
        st.write("## Gesetzessammlung")
        filtered_data = self.data
        with st.sidebar:
            filter_title = st.text_input("Filtern nach Titel", "")
            filter_hierarchy = tree_select(self.hierarchy)
        if filter_title:
            filtered_data["title_de"] = filtered_data["title_de"].fillna("")
            filtered_data = filtered_data[filtered_data["title_de"].str.contains(filter_title, case=False)]
        if len(filter_hierarchy["checked"])>0:
            numeric_indices = list(map(int, filter_hierarchy["checked"]))  # Or: [int(idx) for idx in indices]
            filtered_data = filtered_data.loc[numeric_indices]
        
        filtered_data = filtered_data[["title_de", "title", "version_active_since"]]
        gb = GridOptionsBuilder.from_dataframe(filtered_data)
        gb.configure_selection("single")  # Single row selection
        grid_options = gb.build()

        st.markdown(f"{len(filtered_data)}/{len(self.data)} Einträge")
        # Display the interactive table
        response = AgGrid(
            filtered_data.reset_index(),
            gridOptions=grid_options,
            enable_enterprise_modules=False,
            theme="streamlit",  # Use Streamlit theme
        )
        selected_row = response["selected_rows"]
        # Check if a row is selected
        if selected_row is not None and not selected_row.empty:
            index = selected_row.iloc[0]['index']
            # Convert selected row (dictionary) to DataFrame
            text_of_law = self.data.loc[index]['text_of_law']
            selected_row_dict = selected_row.iloc[0]  # First (and only) selected row
            row_df = pd.DataFrame(selected_row_dict)
            st.markdown(row_df.to_html(), unsafe_allow_html=True)
            st.write(text_of_law.replace('\n', '<br>'), unsafe_allow_html=True)
        else:
            st.info("Selektiere ein Zeile um die Details anzuzeigen")
        

    def show_chat(self):
        question = st.text_input(texts.question_label, texts.default_question)
        if st.button("Frage stellen"):
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
            llm = OpenAI(temperature=0.0)

            # Build QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever
            )
            question = texts.llm_context.format(question)
            docs_ss = self.vectorstore.similarity_search(question,k=3)
            
            st.write(qa_chain.invoke(question))
            with st.expander("Dokumente"):
                for doc in docs_ss:
                    link = self.data.loc[int(doc.metadata['doc'])]['original_url_de']
                    title = self.data.loc[int(doc.metadata['doc'])]['title_de']
                    st.markdown(f"[{title}]({link})")
                    st.write(doc.page_content)
            
