import emoji
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import textwrap
import tempfile

# ----------------------------
# Hilfsfunktionen
# ----------------------------

def normalize_string(s):
    """
    Wandelt alle Kleinbuchstaben in Großbuchstaben um
    und entfernt Leerzeichen sowie Bindestriche.
    """
    return s.replace(" ", "").replace("-", "").replace("\"","").upper()

def remove_emojis(text):
    # Entfernt nur Emojis, nicht aber Umlaute oder andere Unicode-Zeichen
    return emoji.replace_emoji(text, replace='')

def spalten_mit_code(df, code_liste):
    return [col for col in df.columns for code in code_liste if col.startswith(code)]

def add_titelseite(title, pdf):
    fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4
    ax.axis("off")
    ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=20)
    pdf.savefig()
    plt.close()

def auswertung_pro_wettkampf(df, altersklassen_code, gruppierte_fragen, pdf):
    altersklasse_spalte = next((col for col in df.columns if col.startswith(altersklassen_code)), None)
    if altersklasse_spalte:
        df[altersklasse_spalte] = df[altersklasse_spalte].astype(str).apply(normalize_string)
        for code in gruppierte_fragen:
            frage_spalte = next((col for col in df.columns if col.startswith(code)), None)
            if not frage_spalte:
                continue

            gruppiert = df.groupby(altersklasse_spalte)[frage_spalte].mean().dropna()
            if gruppiert.empty:
                continue

            # Nach Präfix H und D splitten
            gruppiert_H = gruppiert[gruppiert.index.str.startswith("H")]
            gruppiert_D = gruppiert[gruppiert.index.str.startswith("D")]

            if not gruppiert_H.empty:
                plt.figure(figsize=(8, 4))
                sns.barplot(x=gruppiert_H.index, y=gruppiert_H.values)
                plt.title(f"{frage_spalte.split('. ', 1)[1] if '. ' in frage_spalte else frage_spalte} (H*)")
                plt.xlabel("Altersklasse (H*)")
                plt.ylabel("Note")
                ax = plt.gca()
                ax.set_ylim(0, 5.5)
                ax.set_yticks([5, 4, 3, 2, 1, 0])
                ax.set_yticklabels(["5", "4", "3", "2", "1", "0"])
                plt.tight_layout()
                pdf.savefig()
                plt.close()

            if not gruppiert_D.empty:
                plt.figure(figsize=(8, 4))
                sns.barplot(x=gruppiert_D.index, y=gruppiert_D.values)
                plt.title(f"{frage_spalte.split('. ', 1)[1] if '. ' in frage_spalte else frage_spalte} (D*)")
                plt.xlabel("Altersklasse (D*)")
                plt.ylabel("Note")
                ax = plt.gca()
                ax.set_ylim(0, 5.5)
                ax.set_yticks([5, 4, 3, 2, 1, 0])
                ax.set_yticklabels(["5", "4", "3", "2", "1", "0"])
                plt.tight_layout()
                pdf.savefig()
                plt.close()

# ----------------------------
# Hauptfunktion
# ----------------------------

def generiere_auswertung_pdf(data, pdf_path="antwortenV2"):
    altersklassen_code_wk1 = "G07Q01"
    altersklassen_code_wk2 = "G09Q01"
    # Fragen die auf einer Skala von 1-5 bewertet werden
    numerische_codes = [
        "G06Q01", "G06Q02", "G06Q03", "G06Q04",
        "G08Q01", "G08Q02", "G08Q03", "G08Q04"
    ]
    # Fragen die Wettkampfspezifisch sind
    gruppierte_fragen_wk1 = ["G07Q02", "G07Q03", "G07Q04", "G07Q05"]
    gruppierte_fragen_wk2 = ["G09Q02", "G09Q03", "G09Q04", "G09Q05"]
    # Beispielsweoise JaNein-Fragen
    kategorische_codes = ["G04Q01", "G04Q02", "G04Q03", "G04Q04", "G04Q05", "G01Q01", "G05Q01", "G05Q02"]

    df = pd.DataFrame(data["responses"])

    # Nur abgeschickte Antworten
    # Suche nach einer Spalte, die "submitdate" ODER "Datum Abgeschickt" enthält
    submit_col = next(
        (c for c in df.columns if "submitdate" in c.lower() or "datum abgeschickt" in c.lower()),
        None
    )
    if submit_col:
        df = df[df[submit_col].notna()]

    if pdf_path is None:
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_path = tmpfile.name

    pdf = PdfPages(pdf_path)

    # Teil 1: Numerische Gesamtauswertung
    #add_titelseite("Gesamtauswertung numerischer Fragen", pdf)
    numerische_fragen = spalten_mit_code(df, numerische_codes)

    mittelwerte = df[numerische_fragen].mean().sort_values()
    if not mittelwerte.empty:
        bewertung_df = pd.DataFrame({
            "Frage": [col.split('. ', 1)[1] if '. ' in col else col for col in mittelwerte.index],
            "Durchschnitt": mittelwerte.values
        })
        plt.figure(figsize=(10, 0.6 * len(bewertung_df)))
        sns.barplot(data=bewertung_df, x="Durchschnitt", y="Frage")
        plt.xlabel("Durchschnitt")
        plt.title("Durchschnittliche Bewertungen")
        ax = plt.gca()
        ax.set_xlim(0, 5.5)
        ax.set_xticks([5, 4, 3, 2, 1, 0])
        ax.set_xticklabels(["5", "4", "3", "2", "1", "0"])
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    # Teil 2: Gruppierte Auswertungen (wie gehabt)
    auswertung_pro_wettkampf(df, altersklassen_code_wk1, gruppierte_fragen_wk1, pdf)
    auswertung_pro_wettkampf(df, altersklassen_code_wk2, gruppierte_fragen_wk2, pdf)

    # Teil 3: Kategorische Fragen (mit "Keine Antwort")
    #add_titelseite("Auswertung kategorischer Fragen", pdf)
    kategorische_fragen = spalten_mit_code(df, kategorische_codes)
    for frage in kategorische_fragen:
        if frage not in df.columns:
            continue
        werte = df[frage].astype(str).replace("", "Keine Antwort").fillna("Keine Antwort")
        kategorien = werte.value_counts().index.tolist()

        plt.figure(figsize=(8, 4))
        sns.countplot(y=werte, order=kategorien)
        plt.title(frage.split('. ', 1)[1] if '. ' in frage else frage)
        plt.xlabel("Anzahl")
        plt.ylabel("Antwort")
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    # Teil 4: Freitextantworten
    #add_titelseite("Freitextantworten", pdf)
    textfragen = [col for col in df.columns if "Anmerkungen" in col]
    for frage in textfragen:
        antworten = df[frage].dropna().astype(str).str.strip()
        antworten = [remove_emojis(a) for a in antworten if a]
        if len(antworten) == 0:
            continue

        seite = []
        zeilenzahl = 0
        for antw in antworten:
            wrapped = textwrap.wrap(f"- {antw}", width=80)
            if zeilenzahl + len(wrapped) + 2 > 60:  # 40 Zeilen pro Seite
                # Seite voll, neue Seite beginnen
                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                ax.axis("off")
                titel = frage.split('. ', 1)[1] if '. ' in frage else frage
                text = f"{titel}\n" + "-" * 80 + "\n\n" + "\n".join(seite)
                ax.text(0, 1, text, ha="left", va="top", wrap=True, family="monospace")
                pdf.savefig()
                plt.close()
                seite = []
                zeilenzahl = 0
            seite.extend(wrapped + [""])
            zeilenzahl += len(wrapped) + 1
        if seite:
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            text = f"{titel}\n" + "-" * 80 + "\n\n" + "\n".join(seite)
            ax.text(0, 1, text, ha="left", va="top", wrap=True, family="monospace")
            pdf.savefig()
            plt.close()
    pdf.close()

    with open(pdf_path, "rb") as f:
        return f.read()

def get_frage_code(frage):
    return frage.split('. ', 1)[1]