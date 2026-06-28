"""
ChemX Extractor — веб-приложение для извлечения химических данных из PDF.
Запуск: streamlit run app.py
"""

import io
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st
import pandas as pd

#Настройки страницы

st.set_page_config(page_title="ChemX Extractor", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stDecoration"] { display: none; }

/* Root tokens */
:root {
    --bg: #0f1117;
    --surface: #161b27;
    --border: #1e2535;
    --border-light: #252d3d;
    --accent: #4f8ef7;
    --accent-dim: rgba(79,142,247,0.12);
    --text: #e2e8f0;
    --text-muted: #64748b;
    --text-dim: #94a3b8;
    --success: #10b981;
    --warn: #f59e0b;
    --font: 'Inter', sans-serif;
    --mono: 'IBM Plex Mono', monospace;
    --radius: 6px;
}

/* Global */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}

/* Main content area */
[data-testid="stMain"] {
    background-color: var(--bg) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: var(--font) !important;
    color: var(--text) !important;
}
[data-testid="stSidebarContent"] {
    padding: 1.5rem 1.25rem !important;
}

/* Sidebar header (custom) */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.5rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
}
.sidebar-logo-mark {
    width: 32px; height: 32px;
    background: var(--accent);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.sidebar-logo-text { font-size: 0.9rem; font-weight: 600; letter-spacing: 0.04em; }
.sidebar-logo-sub { font-size: 0.7rem; color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; }

/* Section labels */
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.25rem 0 0.5rem;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stRadio"] {
    background: var(--bg) !important;
    border-color: var(--border-light) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] span { color: var(--text-dim) !important; font-size: 0.85rem !important; }

/* Pills for fields */
.field-pill {
    display: inline-block;
    background: var(--bg);
    border: 1px solid var(--border-light);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.72rem;
    font-family: var(--mono);
    color: var(--accent);
    margin: 2px 2px;
}
.fields-wrap { margin-top: 0.5rem; line-height: 2; }

/* Page header */
.page-header {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.75rem;
}
.page-header h1 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 0.25rem;
    letter-spacing: -0.02em;
}
.page-header p {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin: 0;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    padding: 0.6rem 1.25rem !important;
    border-radius: 0 !important;
    margin-right: 0 !important;
    font-family: var(--font) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* Buttons */
[data-testid="stButton"] button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    color: #fff !important;
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    padding: 0.5rem 1.25rem !important;
    transition: opacity 0.15s !important;
}
[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

/* Download buttons */
[data-testid="stDownloadButton"] button {
    background: var(--surface) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius) !important;
    color: var(--text-dim) !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    padding: 0.45rem 1rem !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 1px dashed var(--border-light) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"] label { color: var(--text-muted) !important; font-size: 0.82rem !important; }

/* Alert/info/warning */
[data-testid="stAlert"] {
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    border-left-width: 3px !important;
    font-size: 0.82rem !important;
}

/* Progress bar */
[data-testid="stProgressBar"] > div { background: var(--accent) !important; }

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: var(--text-muted) !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 600 !important; color: var(--accent) !important; font-family: var(--mono) !important; }

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
}
[data-testid="stExpander"] summary { font-size: 0.82rem !important; color: var(--text-dim) !important; font-weight: 500 !important; }

/* Caption */
[data-testid="stCaptionContainer"] { color: var(--text-muted) !important; font-size: 0.75rem !important; }

/* Status / spinner text */
.stSpinner > div { color: var(--text-muted) !important; font-size: 0.82rem !important; }

/* Code blocks inside sidebar */
[data-testid="stSidebar"] code {
    background: var(--bg) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 4px !important;
    color: var(--accent) !important;
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    padding: 1px 6px !important;
}

/* Result status badges */
.badge-ok {
    display: inline-block;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3);
    color: #10b981;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-family: var(--mono);
}
.badge-warn {
    display: inline-block;
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    color: #f59e0b;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-family: var(--mono);
}
.result-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 0.4rem;
    background: var(--surface);
    font-size: 0.8rem;
}
.result-row-name { font-family: var(--mono); color: var(--text-dim); }
.result-row-meta { color: var(--text-muted); font-size: 0.72rem; }
.section-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.5rem 0 0.75rem;
}
.result-count {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
    font-family: var(--mono);
}
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown("""
<div class="page-header">
  <h1>🧪 ChemX Extractor</h1>
  <p>Automated chemical data extraction from scientific PDFs · DataCon 2026</p>
</div>
""", unsafe_allow_html=True)

# схемы датасетов

DATASETS = {
    "EyeDrops": {
        "description": "Проницаемость роговицы и липофильность препаратов для глазных капель",
        "fields": ["smiles", "name", "perm (cm/s)", "logP"],
        "name_field": "name",
        "few_shot": """Пример таблицы в статье:
Drug        | logP  | Papp (cm/s)
acebutolol  | 1.63  | 1.1×10-6
timolol     | -1.9  | 2.3×10-6
pilocarpine | -1.6  | 1.7×10-7

Ожидаемый JSON:
[
  {"name": "acebutolol",  "smiles": null, "logP": "1.63",  "perm (cm/s)": "1.1E-6"},
  {"name": "timolol",     "smiles": null, "logP": "-1.9",  "perm (cm/s)": "2.3E-6"},
  {"name": "pilocarpine", "smiles": null, "logP": "-1.6",  "perm (cm/s)": "1.7E-7"}
]""",
    },
    "Nanozymes": {
        "description": "Нанозимы: кинетика ферментоподобной активности (Km, Vmax)",
        "fields": ["formula", "activity", "syngony", "length", "width", "depth",
                   "surface", "km_value", "km_unit", "vmax_value", "vmax_unit",
                   "target_source", "reaction_type", "c_min", "c_max", "c_const",
                   "c_const_unit", "ccat_value", "ccat_unit", "ph", "temperature"],
        "name_field": None,
        "few_shot": """Пример из текста:
Fe3O4 nanoparticles (3.5 nm, cubic, dopamine-coated) showed peroxidase-like activity.
Km = 2.75×10-3 mM, Vmax = 1.42×10-8 M/s, pH 4.6, 25°C, catalyst 20 μg/mL, H2O2 3.65 mM.

Ожидаемый JSON:
[{"formula":"Fe3O4","activity":"peroxidase","syngony":"cubic","length":"3.5",
  "surface":"dopamine","km_value":"2.75","km_unit":"10-3 mM",
  "vmax_value":"1.42","vmax_unit":"10-8 M/s","reaction_type":"H2O2+TMB",
  "c_const":"3.65","c_const_unit":"mM","ccat_value":"20","ccat_unit":"μg/mL",
  "ph":"4.6","temperature":"25"}]""",
    },
    "Synergy": {
        "description": "Синергизм наночастиц и антибиотиков/пептидов против бактерий",
        "fields": ["NP", "bacteria", "strain", "NP_synthesis", "drug",
                   "drug_dose_µg_disk", "NP_concentration_µg_ml",
                   "NP_size_min_nm", "NP_size_max_nm", "NP_size_avg_nm",
                   "shape", "method",
                   "ZOI_drug_mm_or_MIC _µg_ml", "error_ZOI_drug_mm_or_MIC_µg_ml",
                   "ZOI_NP_mm_or_MIC_np_µg_ml", "error_ZOI_NP_mm_or_MIC_np_µg_ml",
                   "ZOI_drug_NP_mm_or_MIC_drug_NP_µg_ml", "error_ZOI_drug_NP_mm_or_MIC_drug_NP_µg_ml",
                   "fold_increase_in_antibacterial_activity", "zeta_potential_mV",
                   "MDR", "FIC", "effect", "time_hr",
                   "coating_with_antimicrobial_peptide_polymers",
                   "combined_MIC", "peptide_MIC", "viability_%", "viability_error"],
        "name_field": None,
        "few_shot": "",
    },
    "Nanomag": {
        "description": "Магнитные свойства магнитных наночастиц",
        "fields": ["name", "np_shell_2", "np_hydro_size", "xrd_scherrer_size",
                   "zfc_h_meas", "htherm_sar", "mri_r1", "mri_r2", "emic_size",
                   "instrument", "core_shell_formula", "np_core", "np_shell",
                   "space_group_core", "space_group_shell", "squid_h_max",
                   "fc_field_T", "squid_temperature", "squid_sat_mag",
                   "coercivity", "squid_rem_mag", "exchange_bias_shift_Oe",
                   "vertical_loop_shift_M_vsl_emu_g", "hc_kOe"],
        "name_field": "name",
        "few_shot": "",
    },
    "Cytotox": {
        "description": "Цитотоксичность наночастиц (жизнеспособность клеток)",
        "fields": ["material", "shape", "coat_functional_group", "synthesis_method",
                   "surface_charge", "size_in_medium_nm", "zeta_in_medium_mv",
                   "no_of_cells_cells_well", "human_animal", "cell_source",
                   "cell_tissue", "cell_morphology", "cell_age", "time_hr",
                   "concentration", "test", "test_indicator", "viability_%",
                   "core_nm", "hydrodynamic_nm", "potential_mv", "cell_type"],
        "name_field": None,
        "few_shot": "",
    },
    "SelTox": {
        "description": "Антимикробная активность и токсичность наночастиц серебра",
        "fields": ["np", "coating", "bacteria", "mdr", "strain", "np_synthesis",
                   "method", "mic_np_µg_ml", "concentration", "zoi_np_mm",
                   "np_size_min_nm", "np_size_max_nm", "np_size_avg_nm",
                   "shape", "time_set_hours", "zeta_potential_mV",
                   "solvent_for_extract", "temperature_for_extract_C",
                   "duration_preparing_extract_min", "precursor_of_np",
                   "concentration_of_precursor_mM", "hydrodynamic_diameter_nm",
                   "ph_during_synthesis"],
        "name_field": None,
        "few_shot": "",
    },
    "Benzimidazoles": {
        "description": "Антибактериальная активность (MIC) производных бензимидазола",
        "fields": ["smiles", "compound_id", "target_type", "target_relation",
                   "target_value", "target_units", "bacteria"],
        "name_field": "compound_id",
        "few_shot": "",
    },
    "Oxazolidinones": {
        "description": "Антибактериальная активность оксазолидинонов",
        "fields": ["smiles", "compound_id", "target_type", "target_relation",
                   "target_value", "target_units", "bacteria"],
        "name_field": "compound_id",
        "few_shot": "",
    },
    "Co-crystals": {
        "description": "Свойства фармацевтических сокристаллов",
        "fields": ["name_cocrystal", "ratio_cocrystal", "name_drug", "SMILES_drug",
                   "name_coformer", "SMILES_coformer", "photostability_change"],
        "name_field": "name_drug",
        "few_shot": "",
    },
    "Complexes": {
        "description": "Металло-лигандные комплексы",
        "fields": ["compound_id", "compound_name", "SMILES", "metal", "target"],
        "name_field": "compound_name",
        "few_shot": "",
    },
}

# Поля источника — не оцениваются
SOURCE_FIELDS = {
    "doi", "title", "journal", "year", "access", "page", "origin", "PMID",
    "publisher", "pdf", "supplementary", "authors", "reference", "article_list",
    "journal_name", "journal_is_oa", "is_oa", "oa_status", "doi_sourse", "supp",
    "verification required", "verified_by", "verification_date",
    "has_mistake_in_matadata", "comment", "article_name_folder", "supp_info_name_folder",
    "sn",
    # Co-crystals source cols
    "name_cocrystal_type_file", "name_cocrystal_page", "name_cocrystal_origin",
    "ratio_cocrystal_page", "ratio_cocrystal_page.1", "ratio_cocrystal_origin",
    "name_drug_type_file", "name_drug_origin", "name_drug_page",
    "SMILES_drug_type_file", "SMILES_drug_origin", "SMILES_drug_page",
    "name_coformer_type file", "name_coformer_origin", "name_coformer_page",
    "SMILES_coformer_type file", "SMILES_coformer_origin", "SMILES_coformer_page",
    "photostability_change_type_file", "photostability_change_origin", "photostability_change_page",
    # Benzimidazoles/Oxazolidinones source cols
    "page_bacteria", "origin_bacteria", "section_bacteria", "subsection_bacteria",
    "page_target", "origin_target", "section_target", "subsection_target",
    "page_scaffold", "origin_scaffold", "page_residue", "origin_residue",
    "column_prop", "line_prop", "section_scaffold", "subsection_scaffold", "section_residue",
    "bacteria_info", "bacteria_name_unified", "bacteria_unified",
    # Complexes source cols
    "SMILES_type", "page_smiles", "origin_smiles", "page_metal", "origin_metal",
    "page_target_value", "origin_target_value",
}

# SMILES LOOKUP — три источника

def _is_derivative_name(name: str) -> bool:
    """Нестандартные имена: производные, коды, серийные номера."""
    patterns = [r"der\.", r"SKF\s", r"MK-\d", r"\d[a-z]$", r"[a-z]{1,2}\d+$"]
    return any(re.search(p, name, re.IGNORECASE) for p in patterns)

def pubchem_lookup(name: str) -> Dict:
    """
    Получить SMILES по названию.
    Источник 1: CIR NIH
    Источник 2: PubChem через canonicalsmiles endpoint.
    """
    if not name or str(name).lower() in ("none", "null", "", "nan"):
        return {}
    name = str(name).strip()

    # Источник 1: CIR NIH — самый надёжный, простой текстовый ответ
    try:
        url = f"https://cactus.nci.nih.gov/chemical/structure/{requests.utils.quote(name)}/smiles"
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.text.strip() and "Page not found" not in r.text:
            smiles = r.text.strip().split()[0]  # берём только первый токен
            return {"smiles": smiles}
    except Exception:
        pass

    # Источник 2: PubChem — используем CanonicalSMILES (не Isomeric, он иногда отсутствует)
    try:
        url2 = (f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
                f"{requests.utils.quote(name)}/property/CanonicalSMILES,IsomericSMILES/JSON")
        r2 = requests.get(url2, timeout=10)
        if r2.status_code == 200:
            props = r2.json()["PropertyTable"]["Properties"][0]
            smiles = props.get("IsomericSMILES") or props.get("CanonicalSMILES")
            if smiles:
                return {"smiles": smiles}
    except Exception:
        pass

    return {}

def llm_smiles_for_derivatives(
    records: List[Dict],
    name_field: str,
    smiles_field: str,
    text: str,
    api_key: str,
    base_url: str,
    model: str,
) -> List[Dict]:
    """
    Для производных соединений (der.Xn, der.Xh и т.д.) которых нет в PubChem/CIR:
    просим GPT вывести SMILES на основе паттерна серии из текста/таблиц.
    Обрабатываем батчами по 20 штук чтобы не переполнить контекст.
    """
    need = [
        r for r in records
        if (not r.get(smiles_field) or str(r.get(smiles_field)) in ("None", "null", ""))
        and r.get(name_field)
        and _is_derivative_name(str(r.get(name_field, "")))
    ]
    if not need:
        return records

    # Батчи по 20
    BATCH = 20
    smiles_map = {}

    for i in range(0, len(need), BATCH):
        batch = need[i:i+BATCH]
        names_list = [str(r[name_field]) for r in batch]

        prompt = (
            "В научной статье есть серии производных соединений. "
            "Тебе нужно определить SMILES для каждого производного из списка.\n"
            "Производные обозначены как 'BaseName der.Xn' где X — номер, "
            "n — буква серии. Их структуры описаны в тексте или таблицах статьи — "
            "ищи таблицу с заместителями (R-группами) или схему синтеза.\n\n"
            f"Нужны SMILES для этих соединений:\n"
            + "\n".join(f"- {n}" for n in names_list)
            + f"\n\nТЕКСТ И ТАБЛИЦЫ СТАТЬИ:\n{text[:10000]}\n\n"
            "ВАЖНО: Производные отличаются заместителями на базовой структуре. "
            "Если видишь таблицу с R1, R2 заместителями — используй её.\n"
            "Верни JSON-объект {\"имя\": \"SMILES\"} для каждого соединения. "
            "Если SMILES определить невозможно — ставь null.\n"
            "Только JSON, без комментариев и markdown."
        )

        raw = call_llm(
            api_key, base_url, model,
            "Ты эксперт-химик. Определяй SMILES производных соединений по их структурным описаниям в тексте.",
            prompt,
            max_tokens=3000,
        )

        if raw:
            try:
                cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip()
                cleaned = re.sub(r"```\s*$", "", cleaned).strip()
                batch_map = json.loads(cleaned)
                if isinstance(batch_map, dict):
                    smiles_map.update(batch_map)
            except Exception:
                pass

    # Применяем найденные SMILES к записям
    for rec in records:
        name = str(rec.get(name_field, ""))
        found = smiles_map.get(name) or smiles_map.get(name.lower())
        if found and str(found) not in ("None", "null", ""):
            if not rec.get(smiles_field) or str(rec[smiles_field]) in ("None", "null", ""):
                rec[smiles_field] = found

    return records

# пдф парсинг

def parse_pdf(pdf_path: str) -> Dict:
    """Парсит PDF: текст + таблицы (JSON) + DOI + заголовок."""
    result = {"text": "", "tables": [], "title": "", "doi": ""}
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                # Текст
                t = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                pages_text.append(t)
                # Таблицы
                for tbl in page.extract_tables():
                    if not tbl or len(tbl) < 2:
                        continue
                    headers = [str(h).strip() if h else f"col{i}"
                               for i, h in enumerate(tbl[0])]
                    rows = []
                    for row in tbl[1:]:
                        if any(c for c in row if c):
                            rows.append({headers[i]: str(c).strip() if c else ""
                                         for i, c in enumerate(row)
                                         if i < len(headers)})
                    if rows:
                        result["tables"].append(rows)
            result["text"] = "\n".join(pages_text)
    except Exception as e:
        result["error"] = str(e)

    # Извлечь DOI из текста
    doi_match = re.search(
        r'\b(10\.\d{4,}/[^\s"\'<>]{4,})', result["text"])
    if doi_match:
        result["doi"] = doi_match.group(1).rstrip(".,;)")

    # Извлечь заголовок — первые непустые строки до "Abstract"
    lines = result["text"].split("\n")
    title_lines = []
    for line in lines[:30]:
        line = line.strip()
        if re.match(r"^abstract", line, re.IGNORECASE):
            break
        if len(line) > 20:
            title_lines.append(line)
        if len(title_lines) >= 3:
            break
    result["title"] = " ".join(title_lines)[:300]

    return result

# LLM вызов

def call_llm(api_key: str, base_url: str, model: str,
             system: str, user: str, max_tokens: int = 4096) -> Optional[str]:
    """Универсальный вызов LLM через OpenAI-совместимый API."""
    import openai
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=0.0,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            )
            return resp.choices[0].message.content
        except Exception as e:
            wait = 2 ** attempt
            st.warning(f"LLM ошибка (попытка {attempt+1}): {e}. Повтор через {wait}с...")
            time.sleep(wait)
    return None

def parse_json_from_llm(raw: Optional[str]) -> List[Dict]:
    """Парсит JSON из ответа LLM, обрабатывает разные форматы."""
    if not raw:
        return []
    # Убрать markdown-фенсы
    raw = re.sub(r"```(?:json)?\s*", "", raw).strip()
    raw = re.sub(r"```\s*$", "", raw).strip()
    try:
        parsed = json.loads(raw)
    except Exception:
        # Найти массив или объект
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group())
            except Exception:
                return []
        else:
            return []
    if isinstance(parsed, dict):
        for key in ["data", "results", "entries", "records"]:
            if key in parsed and isinstance(parsed[key], list):
                return parsed[key]
        return [parsed]
    if isinstance(parsed, list):
        return [r for r in parsed if isinstance(r, dict)]
    return []

# экстракция

SYSTEM_PROMPT = """Ты эксперт по извлечению химических данных из научных статей.

ПРАВИЛА:
1. Извлекай ТОЛЬКО значения которые явно есть в тексте или таблицах.
2. Числа сохраняй точно как написано — не конвертируй единицы.
3. Если поле не найдено — ставь null.
4. КРИТИЧЕСКИ ВАЖНО: если в таблице N строк с соединениями — верни ровно N объектов.
5. НЕ пропускай строки из таблиц. Каждая строка = один JSON-объект.
6. Верни ТОЛЬКО JSON-массив, без комментариев и markdown-блоков."""

def build_prompt(dataset_name: str, text: str, tables: List, doi: str, title: str) -> str:
    schema = DATASETS[dataset_name]
    fields = schema["fields"]
    few_shot = schema["few_shot"]

    parts = [
        f"## ЗАДАЧА: экстракция данных для датасета {dataset_name}",
        f"Описание: {schema['description']}",
        "",
        "## ПОЛЯ ДЛЯ ИЗВЛЕЧЕНИЯ:",
        ", ".join(fields),
        "",
    ]

    if few_shot:
        parts += ["## ПРИМЕР:", few_shot, ""]

    if doi:
        parts.append(f"DOI статьи: {doi}")
    if title:
        parts.append(f"Заголовок: {title}")
    parts.append("")

    # Таблицы как JSON — самое важное
    if tables:
        parts.append("## ТАБЛИЦЫ ИЗ СТАТЬИ (JSON):")
        for i, tbl in enumerate(tables):
            parts.append(f"\nТаблица {i+1} ({len(tbl)} строк):")
            parts.append(json.dumps(tbl[:150], ensure_ascii=False))
        parts.append("")

    parts += [
        "## ТЕКСТ СТАТЬИ:",
        text[:10000],
        "",
        "## ИНСТРУКЦИЯ:",
        "Шаг 1: Найди все соединения/наночастицы в тексте и таблицах.",
        "Шаг 2: Для каждого извлеки все перечисленные поля.",
        "Шаг 3: Таблицы важнее текста — извлеки ВСЕ строки.",
        f"Шаг 4: Верни JSON-массив объектов с полями: {', '.join(fields)}",
        "Верни ТОЛЬКО JSON-массив.",
    ]
    return "\n".join(parts)

def verify_prompt(dataset_name: str, extracted: str, text: str, tables: List) -> str:
    fields = DATASETS[dataset_name]["fields"]
    return (
        f"## ПРОВЕРКА ЭКСТРАКЦИИ: {dataset_name}\n\n"
        f"Поля: {', '.join(fields)}\n\n"
        f"## УЖЕ ИЗВЛЕЧЕНО:\n{extracted}\n\n"
        f"## ИСХОДНЫЙ ТЕКСТ:\n{text[:5000]}\n\n"
        f"## ТАБЛИЦЫ:\n{json.dumps(tables[:3], ensure_ascii=False)[:3000]}\n\n"
        "ЗАДАЧА:\n"
        "1. Проверь что каждое значение реально есть в источнике.\n"
        "2. Исправь ошибки в единицах или числах.\n"
        "3. Добавь пропущенные записи если они есть в таблицах.\n"
        "4. Верни ТОЛЬКО исправленный JSON-массив."
    )

def extract_from_pdf(
    pdf_path: str,
    dataset_name: str,
    api_key: str,
    base_url: str,
    model: str,
    use_pubchem: bool = True,
    use_verify: bool = True,
) -> Tuple[List[Dict], Dict]:
    """Полный пайплайн извлечения из одного PDF."""
    meta = {"doi": "", "title": "", "n_tables": 0, "n_records": 0}

    # 1. Парсинг PDF
    parsed = parse_pdf(pdf_path)
    meta["doi"] = parsed.get("doi", "")
    meta["title"] = parsed.get("title", "")
    meta["n_tables"] = len(parsed.get("tables", []))

    text = parsed.get("text", "")
    tables = parsed.get("tables", [])

    if not text and not tables:
        return [], meta

    # 2. Основная экстракция
    prompt = build_prompt(
        dataset_name, text, tables,
        meta["doi"], meta["title"]
    )
    raw = call_llm(api_key, base_url, model, SYSTEM_PROMPT, prompt)
    records = parse_json_from_llm(raw)

    if not records:
        return [], meta

    # 3. Верификация (второй проход)
    if use_verify and records:
        v_prompt = verify_prompt(
            dataset_name,
            json.dumps(records, ensure_ascii=False),
            text,
            tables,
        )
        v_raw = call_llm(api_key, base_url, model, SYSTEM_PROMPT, v_prompt)
        v_records = parse_json_from_llm(v_raw)
        if v_records:
            records = v_records

    # 4. PubChem обогащение
    name_field = DATASETS[dataset_name].get("name_field")
    needs_smiles = dataset_name in {
        "EyeDrops", "Benzimidazoles", "Oxazolidinones",
        "Co-crystals", "Complexes"
    }

    if use_pubchem and name_field and needs_smiles:
        smiles_key = "SMILES_drug" if dataset_name == "Co-crystals" else (
            "SMILES" if dataset_name == "Complexes" else "smiles"
        )

        # Шаг 4а: PubChem для стандартных имён
        for rec in records:
            name = rec.get(name_field) or rec.get("name")
            if not name:
                continue
            if rec.get(smiles_key) and str(rec.get(smiles_key)) not in ("None", "null", ""):
                continue  # уже есть
            if _is_derivative_name(str(name)):
                continue  # производные — обработаем через LLM

            props = pubchem_lookup(str(name))
            if props:
                if not rec.get(smiles_key):
                    rec[smiles_key] = props.get("smiles")
                if dataset_name == "EyeDrops" and not rec.get("logP"):
                    rec["logP"] = props.get("logP_pubchem")
            time.sleep(0.2)

        # Шаг 4б: LLM для производных и нестандартных имён
        records = llm_smiles_for_derivatives(
            records, name_field, smiles_key,
            text, api_key, base_url, model,
        )

    # 5. Добавить метаданные
    for rec in records:
        if meta["doi"] and not rec.get("doi"):
            rec["doi"] = meta["doi"]
        if meta["title"] and not rec.get("title"):
            rec["title"] = meta["title"]
        rec["_pdf"] = Path(pdf_path).stem

    meta["n_records"] = len(records)
    return records, meta

# ─── ОЦЕНКА (F1) ─────────────────────────────────────────────────────────────

def normalize(val) -> str:
    if val is None:
        return ""
    s = str(val).strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("−", "-").replace("–", "-").replace(",", ".")
    s = s.replace("×", "x").replace("·", ".")
    return s

def values_match(p, g) -> bool:
    pn, gn = normalize(p), normalize(g)
    if pn == gn:
        return True
    if not pn or not gn:
        return False
    try:
        pf = float(re.sub(r"[^\d.\-eE+]", "", pn))
        gf = float(re.sub(r"[^\d.\-eE+]", "", gn))
        if gf != 0:
            return abs(pf - gf) / abs(gf) < 0.02
        return abs(pf - gf) < 1e-9
    except Exception:
        pass
    return pn in gn or gn in pn

def compute_macro_f1(pred_df: pd.DataFrame, gold_df: pd.DataFrame,
                     fields: List[str]) -> Dict:
    """Вычислить Macro-F1 по схеме ChemX."""
    pred = pred_df.to_dict("records")
    gold = gold_df.to_dict("records")

    if not gold:
        return {"macro_f1": 0, "precision": 0, "recall": 0}

    total_f1 = 0.0
    used = set()

    for g in gold:
        best_f1 = 0.0
        best_i = -1
        for i, p in enumerate(pred):
            if i in used:
                continue
            tp = fp = fn = 0
            for f in fields:
                gv = g.get(f)
                pv = p.get(f)
                g_has = gv is not None and str(gv).strip() not in ("", "null", "None", "nan")
                p_has = pv is not None and str(pv).strip() not in ("", "null", "None", "nan")
                if g_has and p_has:
                    if values_match(pv, gv):
                        tp += 1
                    else:
                        fp += 1; fn += 1
                elif p_has and not g_has:
                    fp += 1
                elif g_has and not p_has:
                    fn += 1
            pr = tp / (tp + fp) if (tp + fp) > 0 else 0
            rc = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * pr * rc / (pr + rc) if (pr + rc) > 0 else 0
            if f1 > best_f1:
                best_f1 = f1
                best_i = i
        total_f1 += best_f1
        if best_i >= 0:
            used.add(best_i)

    macro_f1 = total_f1 / len(gold)

    # Общий precision/recall
    all_p = all_r = 0.0
    for g in gold:
        bp = br = 0.0
        for p in pred:
            tp = sum(1 for f in fields
                     if values_match(p.get(f), g.get(f))
                     and g.get(f) is not None
                     and str(g.get(f)).strip() not in ("", "null", "None", "nan"))
            fp_ = sum(1 for f in fields
                      if p.get(f) and str(p.get(f)).strip() not in ("", "null")
                      and not values_match(p.get(f), g.get(f)))
            fn_ = sum(1 for f in fields
                      if g.get(f) and str(g.get(f)).strip() not in ("", "null", "None", "nan")
                      and not values_match(p.get(f), g.get(f)))
            pr = tp / (tp + fp_) if (tp + fp_) > 0 else 0
            rc = tp / (tp + fn_) if (tp + fn_) > 0 else 0
            if pr + rc > bp + br:
                bp, br = pr, rc
        all_p += bp; all_r += br
    n = len(gold)
    return {
        "macro_f1": round(macro_f1, 4),
        "precision": round(all_p / n, 4),
        "recall": round(all_r / n, 4),
        "n_pred": len(pred),
        "n_gold": len(gold),
    }

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-mark">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="3" fill="white"/>
                <circle cx="8" cy="2" r="1.5" fill="white" opacity="0.5"/>
                <circle cx="8" cy="14" r="1.5" fill="white" opacity="0.5"/>
                <circle cx="2" cy="8" r="1.5" fill="white" opacity="0.5"/>
                <circle cx="14" cy="8" r="1.5" fill="white" opacity="0.5"/>
            </svg>
        </div>
        <div>
            <div class="sidebar-logo-text">ChemX</div>
            <div class="sidebar-logo-sub">Extractor v2</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">API</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Key",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        help="OpenRouter: sk-or-v1-... | OpenAI: sk-proj-...",
        label_visibility="collapsed",
        placeholder="API key...",
    )

    provider = st.radio(
        "Provider",
        ["OpenRouter", "OpenAI"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )
    if provider == "OpenRouter":
        base_url = "https://openrouter.ai/api/v1"
    else:
        base_url = "https://api.openai.com/v1"

    st.markdown('<div class="sidebar-section">Model</div>', unsafe_allow_html=True)
    model = st.selectbox(
        "Model",
        ["openai/gpt-4o", "openai/gpt-4o-mini",
         "anthropic/claude-sonnet-4-5",
         "google/gemini-2.0-flash",
         "gpt-4o", "gpt-4o-mini"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section">Dataset</div>', unsafe_allow_html=True)
    dataset_name = st.selectbox(
        "Dataset",
        list(DATASETS.keys()),
        label_visibility="collapsed",
    )
    st.caption(DATASETS[dataset_name]["description"])

    st.markdown('<div class="sidebar-section">Options</div>', unsafe_allow_html=True)
    use_pubchem = st.checkbox("PubChem enrichment", value=True)
    use_verify = st.checkbox("Verification pass", value=True)

    st.markdown('<div class="sidebar-section">Fields</div>', unsafe_allow_html=True)
    pills_html = '<div class="fields-wrap">' + "".join(
        f'<span class="field-pill">{f}</span>' for f in DATASETS[dataset_name]["fields"]
    ) + "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────

tab_extract, tab_evaluate = st.tabs(["Extraction", "Evaluation"])

# ── TAB 1: Extraction ─────────────────────────────────────────────────────────

with tab_extract:
    uploaded = st.file_uploader(
        "Drop PDF files here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if not api_key:
        st.info("Enter your API key in the sidebar to begin.")
    elif not uploaded:
        st.markdown('<div class="section-label">Upload</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:var(--text-muted);font-size:0.82rem;">Upload one or more PDF files to extract chemical data.</p>', unsafe_allow_html=True)
    else:
        if st.button("Run extraction"):
            all_records = []
            prog = st.progress(0)
            status = st.empty()

            with tempfile.TemporaryDirectory() as tmpdir:
                for i, f in enumerate(uploaded):
                    status.markdown(f'<p style="font-size:0.8rem;color:var(--text-muted);font-family:var(--mono);">Processing {f.name} ({i+1}/{len(uploaded)})</p>', unsafe_allow_html=True)
                    prog.progress(i / len(uploaded))

                    tmp = os.path.join(tmpdir, f.name)
                    with open(tmp, "wb") as out:
                        out.write(f.read())

                    with st.spinner(f"Extracting from {f.name}..."):
                        records, meta = extract_from_pdf(
                            tmp, dataset_name,
                            api_key, base_url, model,
                            use_pubchem=use_pubchem,
                            use_verify=use_verify,
                        )

                    if records:
                        all_records.extend(records)
                        st.markdown(
                            f'<div class="result-row">'
                            f'<span class="result-row-name">{f.name}</span>'
                            f'<span class="result-row-meta">'
                            f'{meta["n_records"]} records &nbsp;·&nbsp; '
                            f'DOI: {meta["doi"] or "—"} &nbsp;·&nbsp; '
                            f'{meta["n_tables"]} tables'
                            f'</span>'
                            f'<span class="badge-ok">done</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="result-row">'
                            f'<span class="result-row-name">{f.name}</span>'
                            f'<span class="badge-warn">no results</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            prog.progress(1.0)
            status.empty()

            if all_records:
                st.session_state["records"] = all_records
                st.session_state["dataset"] = dataset_name

    # Results
    if "records" in st.session_state:
        records = st.session_state["records"]
        ds = st.session_state.get("dataset", dataset_name)
        fields = DATASETS[ds]["fields"]

        st.markdown(f'<div class="section-label">Results</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-count">{len(records)} records extracted · dataset: {ds}</div>', unsafe_allow_html=True)

        df = pd.DataFrame(records)
        ordered = [c for c in fields if c in df.columns]
        meta_cols = [c for c in df.columns if c not in ordered and not c.startswith("_")]
        df = df[[*ordered, *meta_cols]]

        st.dataframe(df, use_container_width=True, height=380)

        with st.expander("Field coverage"):
            cov = {}
            for field in fields:
                if field in df.columns:
                    n = df[field].notna() & ~df[field].astype(str).isin(["None", "null", "", "nan"])
                    cov[field] = f"{n.sum()}/{len(df)} ({100*n.mean():.0f}%)"
                else:
                    cov[field] = "0/0 (0%)"
            st.dataframe(
                pd.DataFrame({"Field": list(cov.keys()), "Filled": list(cov.values())}),
                hide_index=True,
            )

        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, f"{ds}_extracted.csv", "text/csv")
        with col2:
            js = json.dumps(records, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button("Download JSON", js, f"{ds}_extracted.json", "application/json")

# ── TAB 2: Evaluation ─────────────────────────────────────────────────────────

with tab_evaluate:
    st.markdown('<div class="section-label">Files</div>', unsafe_allow_html=True)
    col_p, col_g = st.columns(2)
    with col_p:
        pred_file = st.file_uploader("Predictions (CSV)", type=["csv"], key="pred")
    with col_g:
        gold_file = st.file_uploader("Gold standard (CSV or Parquet)", type=["csv", "parquet"], key="gold")

    st.markdown('<div class="sidebar-section">Dataset</div>', unsafe_allow_html=True)
    eval_dataset = st.selectbox(
        "Dataset",
        list(DATASETS.keys()),
        key="eval_ds",
        label_visibility="collapsed",
    )

    if pred_file and gold_file:
        # Загружаем данные для проверки
        pred_df = pd.read_csv(pred_file)
        if gold_file.name.endswith(".parquet"):
            gold_df = pd.read_parquet(gold_file)
        else:
            gold_df = pd.read_csv(gold_file)
        
        # Показываем информацию о загруженных файлах
        st.markdown("### 📋 Информация о файлах")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Predictions:** {len(pred_df)} строк")
            st.write(f"Колонки: {list(pred_df.columns)[:5]}...")
        with col2:
            st.write(f"**Gold:** {len(gold_df)} строк")
            st.write(f"Колонки: {list(gold_df.columns)[:5]}...")
        
        # Проверяем общие поля
        fields = DATASETS[eval_dataset]["fields"]
        common = [f for f in fields if f in pred_df.columns and f in gold_df.columns]
        if common:
            st.success(f"✅ Общие поля для сравнения: {common}")
        else:
            st.error(f"❌ Нет общих полей! Поля датасета: {fields}")
            st.write("Поля в Predictions:", list(pred_df.columns))
            st.write("Поля в Gold:", list(gold_df.columns))
        
        if st.button("📊 Compute F1", type="primary"):
            with st.spinner("Вычисление метрик..."):
                try:
                    metrics = compute_macro_f1(pred_df, gold_df, fields)
                    
                    if "error" in metrics:
                        st.error(metrics["error"])
                    else:
                        st.markdown('<div class="section-label">📈 Results</div>', unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("Macro-F1", f"{metrics['macro_f1']:.4f}")
                        with c2:
                            st.metric("Precision", f"{metrics.get('precision', 0):.4f}")
                        with c3:
                            st.metric("Recall", f"{metrics.get('recall', 0):.4f}")
                        
                        st.caption(f"Predicted: {metrics['n_pred']}  ·  Gold: {metrics['n_gold']}")
                        
                        # Сравнение с бейзлайном
                        baselines = {
                            "Benzimidazoles": 0.217,
                            "Oxazolidinones": 0.491,
                            "Co-crystals": 0.296,
                            "Complexes": 0.290,
                            "Nanozymes": 0.164,
                            "Synergy": 0.080,
                            "Nanomag": 0.034,
                            "Cytotox": 0.182,
                            "SelTox": 0.045,
                        }
                        bl = baselines.get(eval_dataset)
                        if bl:
                            diff = metrics["macro_f1"] - bl
                            sign = "+" if diff >= 0 else ""
                            color = "#10b981" if diff >= 0 else "#ef4444"
                            st.markdown(
                                f'<p style="font-size:0.8rem;color:var(--text-muted);margin-top:0.75rem;">'
                                f'Single-agent baseline: <span style="color:var(--text);font-family:var(--mono)">{bl}</span>'
                                f' &nbsp;·&nbsp; Delta: <span style="color:{color};font-family:var(--mono);font-weight:600">{sign}{diff:.4f}</span>'
                                f'</p>',
                                unsafe_allow_html=True,
                            )
                except Exception as e:
                    st.error(f"❌ Ошибка при вычислении: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    else:
        st.info("📥 Загрузите файлы Predictions и Gold standard для оценки")
