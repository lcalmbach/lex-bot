__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import pandas as pd
import os
import re
import openai

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA
import csv
import json
from time import sleep
from streamlit_tree_select import tree_select
from pathlib import Path
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from langchain_core.documents import Document

from helper import clean_folder
import texts

# Feldgrößen-Limit deutlich heraufsetzen (z.B. auf sys.maxsize)
csv.field_size_limit(2**31 - 1)
openai.api_key  = os.environ['OPENAI_API_KEY']
parquet_file = Path("./100354.parquet")
# csv_file = Path("./100354.csv")
faiss_index_path = "faiss_index"
embeddings = OpenAIEmbeddings()
GRID_COLUMNS = ["title_de", "title", "systematic_number", "keywords_de", "version_active_since"]
col_names_dict = {
    "parent":"ID - übergeordnete Systematik",
    "children":"ID - untergeordnete Systematiken",
    "identifier":"systematische Kennung",
    "title":"Titel - Gesetzessystematik",
    "identifier_full":"Hierarchie nach Kennung",
    "title_full":"Hierarchie nach Titel",
    "systematic_number":"Kennung - Gesetzestext",
    "title_de":"Gesetzes-ID",
    "keywords_de":"Schlüsselwörter",
    "is_active":"Ist aktiv",
    "category_id":"Kategorie-ID",
    "version_active_since":"Gesetzestext aktiv seit",
    "family_active_since":"Gesetzestextfamilie aktiv seit",
    "version_found_at":"Version gefunden am",
    "url_de":"Gesetzestext auf lexfind.ch",
    "original_url_de":"Gesetzestext auf gesetzessammlung.bs.ch",
    "text_of_law":"Gesetzestext"
}

class Lex():
    def __init__(self):
        self.url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/100354/exports/csv?lang=de&timezone=Europe%2FBerlin&use_labels=false&delimiter=%7C"
        #if Path(parquet_file).is_file():
        #    self.data = pd.read_parquet(parquet_file)
        #else:
        self.data = self.load_data(force=False)
        self.vectorstore = FAISS.load_local(
            "faiss_index", embeddings, allow_dangerous_deserialization=True
        )
        
        self.hierarchy = self.get_hierarchy_tree()
        


    def get_hierarchy_tree(self):
        """
        Constructs a hierarchical tree structure from self.data or loads it from a JSON file if available.

        Returns:
            list: A hierarchical tree structure.
        """
        def build_level(identifier, length):
            """
            Constructs nodes for a specific level of the hierarchy.

            Args:
                identifier (str): The parent identifier to filter child nodes.
                length (int): The length of identifiers to match for this level.

            Returns:
                list: A list of child nodes.
            """
            rows = self.data.reset_index()[
                (self.data['identifier'].str.startswith(identifier)) & (self.data['identifier'].str.len() == length)
            ].sort_values(by='identifier', ascending=True)
            children = []
            previous_node = {"label": None}

            for index, row in rows.iterrows():
                node = {"label": row["title"], "value": [str(index)], "children": [], "identifier": row["identifier"]}
                if node['label'] == previous_node['label']:
                    previous_node["value"].append(str(index))
                else:
                    children.append(node)
                    previous_node = node
            return children

        # Check for cached JSON file
        json_file = Path("rechtsgebiet.json")
        if json_file.is_file():
            try:
                with open(json_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                pass  # Handle invalid JSON file gracefully
        
        # Build tree structure
        level1_lst = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        tree = []

        for level1 in level1_lst:
            level1_row = self.data.reset_index()[self.data['identifier'] == level1].iloc[0]
            level1_node = {
                "label": level1_row["title"],
                "value": [str(level1_row["index"])],
                "children": [],
                "identifier": level1
            }

            # Add Level 2 Nodes
            level1_node["children"] = build_level(level1_row['identifier'], 2)

            # Add Level 3 Nodes for each Level 2 Node
            for level2_node in level1_node["children"]:
                level2_node["children"] = build_level(level2_node["identifier"], 3)


            tree.append(level1_node)

        # Save to JSON file
        with open(json_file, "w", encoding="utf-8") as file:
            json.dump(tree, file, ensure_ascii=False, indent=4)

        return tree


    def load_data(self, force:bool=False)->bool:
        """
        Loads data from a parquet file if it exists, otherwise reads from a CSV file, processes it, and saves it as a parquet file.

        Args:
            force (bool): If True, forces reloading data from the CSV file even if the parquet file exists. Default is False.

        Returns:
            bool: Returns the processed DataFrame.

        The function performs the following steps:
        1. Checks if the parquet file exists and if `force` is False.
        2. If the parquet file exists and `force` is False, reads the data from the parquet file.
        3. If the parquet file does not exist or `force` is True, reads the data from the CSV file.
        4. Cleans the text data in the DataFrame.
        5. Renames columns and changes data types as necessary.
        6. Embeds text data.
        7. Saves the processed DataFrame to a parquet file.
        """
        def rename_columns():
            df.rename(columns={'index': 'lex_index'}, inplace=True)
            df['identifier'] = df['identifier'].astype(str)
            df["title_de"] = df["title_de"].fillna("")
            df["text_of_law"] = df["text_of_law"].fillna("")

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
            # df.to_csv(csv_file, index=False)
            return df
        
    def clean_all_texts(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans all texts in the provided DataFrame by removing empty lines, leading whitespaces,
        and merging lines that end with specific patterns.
        Args:
            data (pd.DataFrame): A DataFrame containing a column 'text_of_law' with text data to be cleaned.
        Returns:
            pd.DataFrame: The DataFrame with cleaned text data in the 'text_of_law' column.
        """
        def clean_text(text: str)->str:
            """
            Cleans the input text by performing the following operations:
            1. Removes empty lines or lines filled only with whitespace.
            2. Removes leading whitespaces at the beginning of each line.
            3. Joins lines that end with specific patterns such as numbers followed by a period or parenthesis, 
               or lowercase letters followed by a period or parenthesis.
            Args:
                text (str): The input text to be cleaned.
            Returns:
                str: The cleaned text.
            """
            text = re.sub(r'(?m)^\s*\n', '', text)
            # 1) Leere (oder nur mit Whitespace gefüllte) Zeilen entfernen
            text = re.sub(r'(?m)^[ \t]*\n', '', text)
            
            # whitespaces am Beginn der Zeile entfernen
            text = re.sub(r'(?m)^[ \t]+', '', text)
            # 2) Zeilen zusammenführen, wenn sie z.B. mit "1." oder "1)" oder "a)" aufhören
            text = re.sub(r'(?m)^(\d+|§ \d+|\d+\.|\d+\)|[a-z]\)|[a-z]\.)\s*\n', r'\1 ', text)
            return text

        for index, row in data.iterrows():
            text = row['text_of_law']
            if pd.notnull(text) and str(text).strip():
                text = str(text)
                cleaned_text = clean_text(text)
                data.loc[index,'text_of_law'] = cleaned_text
        return data
    
    def embed_text(self, data: pd.DataFrame):
        """
        Embeds text data from a pandas DataFrame into a FAISS vector store.
        Args:
            data (pd.DataFrame): A DataFrame containing the text data to be embedded. 
                                 The DataFrame should have columns 'text_of_law' and 'title_de'.
        Returns:
            None
        This function processes each row in the DataFrame, splits the 'text_of_law' column into chunks,
        and embeds these chunks into a FAISS vector store. The vector store is then saved locally.
        """
        with st.spinner("Embedding Texte..."):
            # Prepare FAISS vectorstore
            vectorstore = FAISS.from_texts(['x'], embeddings)
            
            cnt = 1
            for index, row in data.reset_index().iterrows():
                if pd.notnull(row['text_of_law']) and str(row['text_of_law']).strip():
                    print(f"Processing document {row['title_de'][:50]}: {cnt}/{len(data)}")
                    chunks = row['text_of_law'].split("\n§")
                    ids = []
                    documents = []
                    id = 1
                    for chunk in chunks:
                        document = Document(page_content='§' + chunk.strip(), metadata={"id": f"{str(index)}-{id}", "doc": str(index)})
                        documents.append(document)
                        ids.append(f"{str(index)}-{id}")
                        id += 1
                    vectorstore.add_documents(documents)
                    sleep(1)
                cnt += 1
        with st.spinner("Bilde FAISS Index..."):    
            # Save the FAISS index
            vectorstore.save_local("faiss_index")

        
    def show_info(self):
        """
        Displays information in a Streamlit app.

        This method creates a layout with three columns and displays an image
        and formatted text in the middle column. The image is loaded from a 
        file named "splash_screen.webp" and the text is formatted using the 
        length of the data attribute.

        Returns:
            None
        """
        cols = st.columns([1, 3, 1])
        with cols[1]:
            st.image("./splash_screen.webp", width=800)
            st.markdown(texts.info.format(len(self.data)))

    def show_stats(self):
        """
        Displays the statistics and details of the legal collection.
        This method filters and displays the legal data based on user input from the sidebar.
        Users can filter the data by title and hierarchy, and view the filtered results in an interactive table.
        When a row is selected, detailed information about the selected law is displayed, including a link to the original document and the text of the law if available.
        Sidebar Inputs:
        - Text input to filter by title.
        - Hierarchy selection using a tree structure.
        Table Columns:
        - title_de: Title in German.
        - title: Title.
        - systematic_number: Systematic number.
        - keywords_de: Keywords in German.
        - version_active_since: Version active since.
        Interactive Table:
        - Displays the filtered data.
        - Allows single row selection.
        Selected Row Details:
        - Displays detailed information about the selected law.
        - Provides a link to the original document.
        - Shows the text of the law if available.
        Notes:
        - If no row is selected, an informational message is displayed.
        - If the selected law has no text, an informational message is displayed.
        Returns:
        None
        """
        st.write("## Gesetzessammlung")
        filtered_data = self.data[self.data['id'].notnull()].copy()
        filtered_data["title_de"] = filtered_data["title_de"].fillna("")
        filtered_data["text_of_law"] = filtered_data["text_of_law"].fillna("")

        with st.sidebar:
            filter_title = st.text_input("Titel enthält", "")
            filter_text = st.text_input("Gesetzestext enthält", "")
            st.markdown("Einschränkung nach Rechtsgebiet")
            filter_hierarchy = tree_select(self.hierarchy)
        if len(filter_title)>0:
            filtered_data = filtered_data[filtered_data["title_de"].str.contains(filter_title, case=False)]
        if len(filter_text)>0:
            filtered_data = filtered_data[filtered_data["text_of_law"].str.contains(filter_text, case=False)]
        if len(filter_hierarchy["checked"])>0:
            # ["2","3,4,5"] > ["2","3","4","5"]
            checked_list = []
            for item in filter_hierarchy["checked"]:
                checked_list.extend(item.split(","))
            numeric_indices = list(map(int, checked_list))  # Or: [int(idx) for idx in indices]
            numeric_indices = [idx for idx in numeric_indices if idx in filtered_data.index]
            filtered_data = filtered_data.loc[numeric_indices]
        filtered_data = filtered_data[GRID_COLUMNS]
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
            html = self.data.loc[index]['gesetzestext_html']
            url = self.data.loc[index]['original_url_de']
            selected_row.rename(columns=col_names_dict, inplace=True)
            selected_row_dict = selected_row.iloc[0]  # First (and only) selected row

            selected_row_dict['url'] = f'<a href="{url}" target="_blank">Link Gesetzessammlung</a>'
            row_df = pd.DataFrame(selected_row_dict)
            st.markdown(row_df.to_html(escape=False), unsafe_allow_html=True)
            if text_of_law:
                st.write(html, unsafe_allow_html=True)
                #st.write(text_of_law.replace('\n', '<br>'), unsafe_allow_html=True)
            else:
                st.info("Kein Gesetzestext verfügbar")
        else:
            st.info("Selektiere ein Zeile um die Details anzuzeigen")
        

    def show_chat(self):
        """
        Displays a chat interface using Streamlit.

        This method creates a chat interface where users can input a question and specify the number of results to retrieve.
        It uses a vector store retriever and an OpenAI language model to generate responses to the user's questions.
        The results are displayed along with relevant documents.

        The interface includes:
        - A text input for the question.
        - A sidebar number input to specify the number of results.
        - A button to submit the question and retrieve the response.
        - An expander to show the retrieved documents with links and content.

        Additionally, there is a commented-out section that, when enabled, allows the user to output the database content.

        Args:
            None

        Returns:
            None
        """
        cols = st.columns([1, 3, 1])
        with cols[1]:
            question = st.text_input(texts.question_label, texts.default_question)
            num_of_results = st.sidebar.number_input("Anzahl Resultate", 3, 50, 3)
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
                docs_ss = self.vectorstore.similarity_search(question,k=num_of_results)
                response = qa_chain.invoke(question)
                st.write(response["result"])
                with st.expander("Dokumente"):
                    for doc in docs_ss:
                        link = self.data.loc[int(doc.metadata['doc'])]['original_url_de']
                        title = self.data.loc[int(doc.metadata['doc'])]['title_de']
                        st.markdown(f"[{title}]({link})")
                        st.write(doc.page_content)
        