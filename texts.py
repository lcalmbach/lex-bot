info = """# Lex-Bot ⚖️
Diese App bietet die Möglichkeit, die Gesetzessammlung des Kantons Basel-Stadt zu durchsuchen und gezielt Fragen zu stellen. Alle Texte sind in einer Datenbank als Vektoren abgelegt. In diesem Format können Fragen sehr effizient mit den Gesetzestexten verglichen werden und nach Texten gefiltert werden, die am wahrscheinlichsten die Antwrten auf die Frage enthalten. Diese Dokumente werden anschliessend an ein Large Langauge Model geschickt und, welches die Antwort auf die Frage basierend auf diese mitgelieferten Dokumente zurückschickt. Die Antwort des LLMs kann inkorrekt sein, kontrolliere im Zweifelsfalle immer die mitgelieferten Dokumente, welche unter der Antwort angezeigt werden. 

- Der Menüpunkt **Gesetze** erlaubt eine hierarchische Darstellung und detaillierte Suche nach Gesetzestexten.  
- Mit **Lex-Chat** kannst du Fragen zu den Gesetzen stellen und passende Antworten erhalten.  

Die zugrunde liegenden Daten basieren auf der [Systematischen Gesetzessammlung](https://www.gesetzessammlung.bs.ch/app/de/systematic/texts_of_law) sowie den Erlasstexten des Kantons Basel-Stadt. Sie ermöglichen eine systematische Kategorisierung und Beschreibung der geltenden Rechtsnormen. Änderungen von Erlassen (Chronologische Gesetzessammlung) sind ebenfalls verfügbar, entweder unter [gesetzessammlung.bs.ch](https://www.gesetzessammlung.bs.ch/app/de/chronology/change_documents) oder direkt im Datensatz: [Chronologische Gesetzessammlung](https://data.bs.ch/explore/dataset/100355/).  

Alle Daten werden von der [Open Data Plattform](https://data.bs.ch/) des Kantons Basel-Stadt bereitgestellt. Der Datensatz enthält {} Dokumente. 
"""

default_question = "Wer darf zu Statistik Zwecken Daten verknüpfen?"
llm_context = "Du bist ein Rechtsexperte und beantwortest rechtliche Fragen basierend auf die Gesetzessammlung des Kantons Basel-Stadt. Antworte immer auf deutsch. Erwähne immer das Gesetz, auf welche du deine Antwort stützt.\nFrage:\n{}"  
question_label = "**Gib eine Frage ein zum Thema Recht im Kanton Basel-Stadt**"