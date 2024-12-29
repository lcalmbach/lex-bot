info = """# Lex-Bot ⚖️
Der Datensatz beschreibt die Struktur und Inhalte der [Systematischen Gesetzessammlung](https://www.gesetzessammlung.bs.ch/app/de/systematic/texts_of_law) sowie der Erlasstexte des Kantons Basel-Stadt. Er ermöglicht eine systematische Kategorisierung und Beschreibung der geltenden Rechtsnormen. 

Erlassänderungen (Chronologische Gesetzessammlung) können unter [gesetzessammlung.bs.ch](https://www.gesetzessammlung.bs.ch/app/de/chronology/change_documents) oder auch in diesem Datensatz gefunden werden: https://data.bs.ch/explore/dataset/100355/. Alle Daten stammen von der [Open Data Plattform des Kantons Basel-Stadt](https://data.bs.ch/).

Der Datensatz enthält {} Einträge. 
"""
default_question = "Wer ist für die Sicherheit der Strassen zuständig?"
llm_context = "Du bist ein Rechtsexperte und beantwortest rechtliche Fragen basierend auf die Gesetzessammlung des Kantons Basel-Stadt. Antworte immer auf deutsch. Erwähne immer das Gesetz, auf welche du deine Antwort stützt.\nFrage:\n{}"  
question_label = "**Gib eine Frage ein zum thema Recht im Kanton Basel-Stadt**"