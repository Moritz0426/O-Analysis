
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import textwrap
import re
import tempfile

def parse_schulnote(value):
    if isinstance(value, str):
        match = re.match(r"^\s*(\d)", value)
        if match:
            return int(match.group(1))
    try:
        return float(value)
    except:
        return None

def remove_emojis(text):
    return re.sub(r'[^-]+', '', text)

def spalten_mit_code(df, code_liste):
    return [col for col in df.columns for code in code_liste if col.startswith(code)]

def generiere_auswertung_pdf(json_path):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data["responses"])
    df = df[df["submitdate. Datum Abgeschickt"].notnull()]

    altersklassen_code_WK1 = "G07Q01"
    altersklassen_code_WK2 = "G09Q01"

    numerische_codes = [
        "G06Q01", "G06Q02", "G06Q03", "G06Q04",
        "G08Q01", "G08Q02", "G08Q03", "G08Q04"
    ]

    gruppierte_fragen_WK1 = ["G07Q02", "G07Q03", "G07Q04", "G07Q05"]
    gruppierte_fragen_WK2 = ["G09Q02", "G09Q03", "G09Q04", "G09Q05"]

    kategorische_codes = ["G04Q01", "G04Q02", "G04Q03", "G04Q04", "G04Q05", "G01Q01", "G05Q01", "G05Q02"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        pdf = PdfPages(temp_pdf.name)

        def add_titelseite(title):
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=20)
            pdf.savefig()
            plt.close()

        add_titelseite("Gesamtauswertung numerischer Fragen")
        numerische_fragen = spalten_mit_code(df, numerische_codes)
        for col in numerische_fragen:
            df[col] = df[col].apply(parse_schulnote)
        mittelwerte = df[numerische_fragen].mean().sort_values()
        bewertung_df = pd.DataFrame({
            "Frage": [col.split('. ', 1)[1] if '. ' in col else col for col in mittelwerte.index],
            "Durchschnitt": mittelwerte.values
        })
        plt.figure(figsize=(10, 0.6 * len(bewertung_df)))
        sns.barplot(data=bewertung_df, x="Durchschnitt", y="Frage")
        plt.xlabel("Durchschnitt")
        plt.title("Durchschnittliche Bewertungen")
        plt.gca().invert_xaxis()
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        def auswertung_pro_wk(altersklassen_code, gruppierte_fragen):
            altersklasse_spalte = next((col for col in df.columns if col.startswith(altersklassen_code)), None)
            if altersklasse_spalte:
                for code in gruppierte_fragen:
                    frage_spalte = next((col for col in df.columns if col.startswith(code)), None)
                    if not frage_spalte:
                        continue
                    df[frage_spalte] = df[frage_spalte].apply(parse_schulnote)
                    gruppiert = df.groupby(altersklasse_spalte)[frage_spalte].mean().dropna()
                    if gruppiert.empty:
                        continue
                    plt.figure(figsize=(8, 4))
                    sns.barplot(x=gruppiert.index, y=gruppiert.values)
                    plt.title(frage_spalte.split('. ', 1)[1] if '. ' in frage_spalte else frage_spalte)
                    plt.xlabel("Altersklasse")
                    plt.ylabel("Note")
                    ax = plt.gca()
                    ax.set_ylim(0, 5.5)
                    ax.set_yticks([5, 4, 3, 2, 1, 0])
                    ax.set_yticklabels(["5", "4", "3", "2", "1", "0"])
                    plt.tight_layout()
                    pdf.savefig()
                    plt.close()

        add_titelseite("Auswertung nach Altersklassen – WK1")
        auswertung_pro_wk(altersklassen_code_WK1, gruppierte_fragen_WK1)
        add_titelseite("Auswertung nach Altersklassen – WK2")
        auswertung_pro_wk(altersklassen_code_WK2, gruppierte_fragen_WK2)

        add_titelseite("Auswertung kategorischer Fragen")
        kategorische_fragen = spalten_mit_code(df, kategorische_codes)
        for frage in kategorische_fragen:
            werte = df[frage].fillna("Keine Antwort")
            kategorien = ["Ja", "Nein", "Keine Antwort"] if set(werte.unique()).issubset({"Ja", "Nein", "Keine Antwort"})                 else werte.value_counts().index.tolist()
            plt.figure(figsize=(8, 4))
            farben = ["#1f77b4" if k != "Keine Antwort" else "#aaaaaa" for k in kategorien]
            plot = sns.countplot(y=werte, order=kategorien, palette=farben)
            for p in plot.patches:
                wert = int(p.get_width())
                y = p.get_y() + p.get_height() / 2
                plot.text(p.get_width() + 0.1, y, str(wert), va='center')
            plt.title(frage.split('. ', 1)[1] if '. ' in frage else frage)
            plt.xlabel("Anzahl")
            plt.ylabel("Antwort")
            plt.tight_layout()
            pdf.savefig()
            plt.close()

        add_titelseite("Freitextantworten")
        textfragen = [col for col in df.columns if "Anmerkungen" in col]
        for frage in textfragen:
            antworten = df[frage].dropna().astype(str).str.strip()
            antworten = [remove_emojis(a) for a in antworten if a]
            if len(antworten) == 0:
                continue
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            titel = frage.split('. ', 1)[1] if '. ' in frage else frage
            text = f"{titel}\n" + "-" * 80 + "\n\n"
            for antw in antworten:
                text += textwrap.fill(f"- {antw}", width=100) + "\n\n"
            ax.text(0, 1, text, ha="left", va="top", wrap=True, family="monospace")
            pdf.savefig()
            plt.close()

        pdf.close()
        with open(temp_pdf.name, "rb") as f:
            return f.read()