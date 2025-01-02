# Lex-Bot.BS

[Lex-Bot.BS](https://lex-bot-bs.streamlit.app/) ist eine Anwendung, die Nutzern die Möglichkeit bietet, die Gesetzessammlung des Kantons Basel-Stadt effizient zu durchsuchen und gezielte Fragen zu stellen. Die App kombiniert modernste Technologien aus den Bereichen der Datenbankverwaltung und künstlichen Intelligenz, um benutzerfreundliche Antworten auf rechtliche Fragen zu liefern.

## Funktionen

### Gesetze

Der Menüpunkt **Gesetze** erlaubt:

- Eine hierarchische Darstellung der Gesetzessammlung.
- Detaillierte Suchmöglichkeiten, um spezifische Gesetzestexte schnell zu finden.

### Lex-Chat

Mit **Lex-Chat** kannst du:

- Fragen zu den Gesetzen des Kantons Basel-Stadt stellen.
- Antworten erhalten, die auf den relevantesten Gesetzestexten basieren.
- Verweise auf die zugrunde liegenden Gesetzestexte einsehen, um die Antwort zu verifizieren.

## Wie es funktioniert

1. **Vektorisierung der Daten:** Alle Texte der Gesetzessammlung sind in einer Datenbank als Vektoren gespeichert. Dies ermöglicht eine effiziente Suche nach relevanten Texten basierend auf den eingegebenen Fragen.
2. **Abfrageprozess:** Fragen werden mit den vektorisierten Daten verglichen, und die am wahrscheinlichsten relevanten Texte werden ausgewählt.
3. **Antwortgenerierung:** Die ausgewählten Texte werden an ein Large Language Model (LLM) weitergeleitet, das auf Basis dieser Dokumente Antworten generiert.
4. **Transparenz:** Unter jeder Antwort zeigt die App die zugrunde liegenden Dokumente an, um eine Verifizierung der Informationen zu ermöglichen.

**Wichtig:** Die Antworten des LLMs sind nicht immer korrekt. Bitte kontrolliere im Zweifelsfall die angegebenen Dokumente.

## Datenquellen

Die App basiert auf offiziellen Datenquellen des Kantons Basel-Stadt:
- [Open Data Plattform Basel-Stadt](https://data.bs.ch/)

Der Datensatz umfasst insgesamt **{Anzahl Dokumente}** Dokumente, die regelmäßig aktualisiert werden, um sicherzustellen, dass alle Informationen aktuell und präzise sind.

## Lokale Installation

```
> git clone [https://github.com/lcalmbach/lex-bot-bs.git](https://github.com/lcalmbach/lex-bot-bs.git)
> cd lex-bot-bs
> py -m venv .venv
> .venv\scripts\activate
> pip install -r requirements.txt
> streamlit run app.py
```

## Technologie

- **Programmiersprache:** Python
- **Frameworks:** Streamlit, 
- **Vektorstore:** FAISS,
- **KI-Modell:** GPT-4o

## Einschränkungen

- Die Antworten des LLMs können ungenau oder unvollständig sein. Nutzer sollten die zugrunde liegenden Dokumente stets überprüfen.
- Der Datensatz wird regelmäßig aktualisiert, doch können kurzfristige Änderungen in den Gesetzen nicht sofort berücksichtigt werden.

## Lizenz

Die Anwendung steht unter der MIT-Lizenz. Sie kann für kommerzielle Zwecke genutzt werden, solange der Autor der Anwendung zitiert wird. Weitere Details zur Lizenz finden sich in der beigefügten LICENSE-Datei.

## Beitragen

Beiträge zur Entwicklung der App sind willkommen. Bitte kontaktiere uns per E-Mail unter lcalmbach@gmail.com oder erstelle ein GitHub-Issue, um deine Ideen oder Verbesserungsvorschläge einzureichen.

## Kontakt

Für Rückfragen und Feedback: lcalmbach@gmail.com
