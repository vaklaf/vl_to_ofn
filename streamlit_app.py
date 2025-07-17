import streamlit as st
import json
import os

DOCS_DIR = "docs"
OUTPUT_DIR = "output"
GLOSSARIES_FILE = os.path.join(DOCS_DIR, "glossaries_files.json")
VALIDATION_REPORT_FILE = os.path.join(DOCS_DIR, "validation_report.json")

st.set_page_config(layout="wide")
st.markdown("# 🗂️ Prohlížeč slovníků")

# Načti seznam slovníků
with open(GLOSSARIES_FILE, encoding="utf-8") as f:
    glossaries = json.load(f)  # slovník: cesta_k_souboru

# Načti výsledky validace (předpokládáme textový soubor, každý slovník na novém řádku)
validation_results = {}
if os.path.exists(VALIDATION_REPORT_FILE):
    # with open(VALIDATION_REPORT_FILE, encoding="utf-8") as f:
    #     for line in f:
    #         if ":" in line:
    #             name, result = line.split(":", 1)
    #             validation_results[name.strip()] = result.strip()
    with open(VALIDATION_REPORT_FILE, encoding="utf-8") as f:
        validation_results = json.load(f)  # slovník: výsledek_validace
else:   
    st.warning("Výsledky validace nejsou k dispozici. Ujistěte se, že byly slovníky zvalidovány.")

# Rozdělení stránky na navigaci a hlavní obsah
nav, main = st.columns([1, 3])

with nav:
    st.subheader("Slovníky")
    selected = st.radio(
        "Vyber slovník:",
        options=list(glossaries.keys()),
        format_func=lambda x: x,
        label_visibility="collapsed"
    )

with main:
    st.subheader(f"Slovník: {selected}")
    # Výsledek validace
    val_result = validation_results.get(selected, "Není k dispozici")
    st.markdown(f"**Výsledek validace:** {val_result}")

    # Načti a zobraz obsah slovníku
    file_path = glossaries[selected]
    if not os.path.isabs(file_path):
        file_path = os.path.join(OUTPUT_DIR, file_path)
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        st.markdown("**Obsah slovníku:**")
        st.json(data)
        st.download_button("Stáhnout JSON-LD", json.dumps(data, ensure_ascii=False, indent=2), file_name=os.path.basename(file_path))
    else:
        st.error("Soubor slovníku nebyl nalezen.")
