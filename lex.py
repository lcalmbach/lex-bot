import pandas as pd
import os
import re
import openai
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA
import csv
from pathlib import Path
from helper import clean_folder

# Feldgrößen-Limit deutlich heraufsetzen (z.B. auf sys.maxsize)
csv.field_size_limit(2**31 - 1)
openai.api_key  = os.environ['OPENAI_API_KEY']
persist_directory = './docs/chroma/'
TEXT_FILES_PATH = Path("./docs/text")
parquet_file = Path("./100354.parquet")
csv_file = Path("./100354.csv")


class Loader():
    def __init__(self):
        self.url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/100354/exports/csv?lang=de&timezone=Europe%2FBerlin&use_labels=false&delimiter=%7C"
        if Path(parquet_file).is_file():
            self.data = pd.read_parquet(parquet_file)
        else:
            self.data = self.load_data()
            self.embed_text()
            self.data.to_parquet(parquet_file, index=False)
            self.data.to_csv(csv_file, index=False)

    def load_data(self):
        data = pd.read_csv(self.url, delimiter='|', engine='python')
        data = self.clean_all_texts(data)
        return data

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

        clean_folder(TEXT_FILES_PATH)
        data['txt_filename'] = None
        for index, row in data.iterrows():
            text = row['text_of_law']
            if pd.notnull(text) and str(text).strip():
                text = str(text)
                file = TEXT_FILES_PATH / f"{int(row['index'])}.txt"
                cleaned_text = clean_text(text)
                with open(file, "w", encoding='utf-8') as f:
                    f.write(cleaned_text)
                data.loc[index, 'txt_filename'] = file.name
        return data
    
    def embed_text(self):
        clean_folder(Path(persist_directory))
        docs = []
        text_splitter = CharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=0,
            separator=' '
        )
        for index, row in self.data[:10].iterrows():
            if pd.notnull(row['txt_filename']) and str(row['txt_filename']).strip():
                file = TEXT_FILES_PATH / row['txt_filename']
                loader = TextLoader(file, encoding="utf-8")
                doc = loader.load()
                print(doc)
                doc[0].metadata['index'] = row['index']
                docs.extend(doc)
                print(doc[0]['metadata'])
            split_docs = text_splitter.split_documents(docs)
        
        for doc in split_docs:
            vectorstore = Chroma.from_documents(
                documents=[doc],
                embedding=OpenAIEmbeddings(),
                persist_directory=persist_directory
            )

    def run_qa(self, question):
        # Same embeddings to ensure consistent vector representation
        embedding_function = OpenAIEmbeddings(
            # openai_api_key="YOUR_OPENAI_API_KEY",
            model="text-embedding-ada-002"
        )

        # Load your existing Chroma DB
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_function
        )

        # Create a retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        llm = OpenAI(temperature=0.0)

        # Build QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever
        )

        # Simple interactive loop
        while True:
            query = input("Ask a legal question (or 'quit'): ")
            if query.lower() in ["quit", "exit"]:
                break
            answer = qa_chain.run(query)
            print(f"\nAnswer: {answer}\n")
