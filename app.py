import base64
import csv
import io
import requests
import streamlit as st
import os

def finde_frage_keys(spaltenname, questions):
    # Gibt alle möglichen Keys (title, question) für eine Spalte zurück
    for q in questions:
        if q["question"] == spaltenname or q["title"] == spaltenname or q["question"] in spaltenname:
            return [q["title"], q["question"]]
    return []


# CSV-Daten analysieren
def analysiere_csv(data):
    # Zeige die Spaltennamen
    st.write("Spaltennamen im CSV:", list(data[0].keys()) if data else "Keine Daten gefunden.")

    # Zeige die ersten Zeilen der Daten
    st.write("Erste Zeilen der CSV-Daten:")
    for i, row in enumerate(data[:5]):  # Zeige die ersten 5 Zeilen
        st.write(f"Zeile {i + 1}: {row}")


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
    analysiere_csv(data)

    # Fragen holen
    questions_payload = {
        "method": "list_questions",
        "params": [session_key, survey_id],
        "id": 3
    }
    questions_response = requests.post(LS_URL, json=questions_payload)
    questions = questions_response.json().get("result", [])

    # Antwortoptionen holen und mappen
    answer_map = {}
    st.write(questions)
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
                    # Mappe auf Fragetitel UND Fragetext
                    answer_map[q["title"]] = code_ans_map
                    answer_map[q["question"]] = code_ans_map
    # Beispiel: Antwortoptionen für G04Q01 anzeigen
    qid_g04q01 = next(q["qid"] for q in questions if q["title"] == "G04Q01")
    answers_payload = {
        "method": "list_answers",
        "params": [session_key, survey_id, int(qid_g04q01)],
        "id": 99
    }
    answers_response = requests.post(LS_URL, json=answers_payload)
    st.write(answers_response.json().get("result", []))
    if answers_response.status_code == 200:
        answers = answers_response.json().get("result", [])
        st.write("Antwortoptionen für G04Q01:", answers)
    # Antwortcodes ersetzen
    st.write(answer_map)
    new_data = []
    for row in data:
        new_row = {}
        for col, value in row.items():
            frage_keys = finde_frage_keys(col, questions)
            mapped = False
            for key in frage_keys:
                if key in answer_map and value in answer_map[key]:
                    new_row[col] = answer_map[key][value]
                    mapped = True
                    break
            if not mapped:
                new_row[col] = value
        new_data.append(new_row)

    st.write("Gemappte Daten (erste 10 Zeilen):")
    st.dataframe(new_data[:10])