info = """# Lex-Bot ⚖️
Diese App bietet die Möglichkeit, die Gesetzessammlung des Kantons Basel-Stadt zu durchsuchen und gezielt Fragen zu stellen. Alle Texte sind in einer Datenbank als Vektoren abgelegt. In diesem Format können Fragen sehr effizient mit den Gesetzestexten verglichen und nach Texten gefiltert werden, die am wahrscheinlichsten die Antworten auf die Frage enthalten. Diese Dokumente werden anschliessend an ein Large Language Model (LLM) übermittelt, das auf Basis dieser Dokumente eine Antwort generiert. Die Antwort des LLMs kann jedoch inkorrekt sein. Kontrolliere im Zweifelsfall immer die mitgelieferten Dokumente, welche unter der Antwort angezeigt werden.

Der Menüpunkt Gesetze erlaubt eine hierarchische Darstellung und detaillierte Suche nach Gesetzestexten.

Mit Lex-Chat kannst du Fragen zu den Gesetzen stellen und passende Antworten erhalten.

Die zugrunde liegenden Daten basieren auf der Systematischen Gesetzessammlung sowie den Erlasstexten des Kantons Basel-Stadt. Sie ermöglichen eine systematische Kategorisierung und Beschreibung der geltenden Rechtsnormen. Änderungen von Erlassen (Chronologische Gesetzessammlung) sind ebenfalls verfügbar, entweder unter gesetzessammlung.bs.ch oder direkt im Datensatz: Chronologische Gesetzessammlung.

Alle Daten werden von der Open Data Plattform des Kantons Basel-Stadt bereitgestellt. Der Datensatz enthält {} Dokumente.
"""

default_question = "Wer darf zu Statistik Zwecken Daten verknüpfen?"
llm_context = "Du bist ein Rechtsexperte und beantwortest rechtliche Fragen basierend auf die Gesetzessammlung des Kantons Basel-Stadt. Antworte immer auf deutsch. Erwähne immer das Gesetz, auf welche du deine Antwort stützt.\nFrage:\n{}"  
question_label = "**Gib eine Frage ein zum Thema Recht im Kanton Basel-Stadt**"