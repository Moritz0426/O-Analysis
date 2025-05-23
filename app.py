import base64
import csv
import io
import requests
import streamlit as st
import os
import re

# Hilfsfunktion, um Fragetext auf LimeSurvey-Titel zu mappen
def finde_frage_title(spaltenname, code_to_title):
    for title, frage in code_to_title.items():
        # Exakter Vergleich oder Teilstring-Suche
        if frage == spaltenname or frage in spaltenname or spaltenname in frage:
            return title
    return None
st.set_page_config(page_title="LimeSurvey Short-Format Mapper", layout="centered")
st.title("LimeSurvey Short-Format Antwort-Mapping")

survey_id = st.text_input("Survey-ID", placeholder="z. B. 123456")

if st.button("Antworten mappen") and survey_id:
    LS_URL = os.environ.get("LS_URL")
    LS_USER = os.environ.get("LS_USER")
    LS_PASSWORD = os.environ.get("LS_PASSWORD")

    # Session holen
    session_payload = {
        "method": "get_session_key",
        "params": [LS_USER, LS_PASSWORD],
        "id": 1
    }
    r = requests.post(LS_URL, json=session_payload)
    session_key = r.json().get("result")
    if not session_key:
        st.error("Session-Key konnte nicht abgerufen werden.")
        st.stop()

    # Antworten im Short-Format exportieren
    export_payload = {
        "method": "export_responses",
        "params": [session_key, survey_id, "csv", "de-informal", "short"],
        "id": 2
    }
    export_response = requests.post(LS_URL, json=export_payload)
    export_data = export_response.json().get("result")
    if not export_data:
        st.error("Keine Daten gefunden.")
        st.stop()
    decoded_bytes = base64.b64decode(export_data)
    decoded_str = decoded_bytes.decode("utf-8-sig")
    csv_reader = csv.DictReader(io.StringIO(decoded_str), delimiter=';')
    data = list(csv_reader)

    # Fragen holen
    questions_payload = {
        "method": "list_questions",
        "params": [session_key, survey_id],
        "id": 3
    }
    questions_response = requests.post(LS_URL, json=questions_payload)
    questions = questions_response.json().get("result", [])
    code_to_title = {q["title"]: q["question"] for q in questions}
    title_to_qid = {q["question"]: q["qid"] for q in questions}
    title_to_type = {q["question"]: q["type"] for q in questions}

    # Antwortoptionen holen und mappen
    answer_map = {}
    for q in questions:
        if q["type"] in ("L", "M", "O", "P", "5", "A", "B"):
            answers_payload = {
                "method": "list_answers",
                "params": [session_key, survey_id, int(q["qid"])],
                "id": 4
            }
            answers_response = requests.post(LS_URL, json=answers_payload)
            if answers_response.status_code == 200:
                answers = answers_response.json().get("result", [])
                code_ans_map = {a["code"]: a["answer"] for a in answers}
                if code_ans_map:
                    answer_map[q["question"]] = code_ans_map

    # Antwortcodes ersetzen
    new_data = []
    for row in data:
        new_row = {}
        for col, value in row.items():
            # Finde zugehörigen Fragetitel
            title = finde_frage_title(col, code_to_title)
            if title and title in answer_map and value in answer_map[title]:
                new_row[col] = answer_map[title][value]
            else:
                new_row[col] = value
        new_data.append(new_row)

    st.write("Gemappte Daten (erste 10 Zeilen):")
    st.dataframe(new_data[:10])