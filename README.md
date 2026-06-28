# Datacon26
# ChemX Extractor

Автоматическое извлечение химических данных из научных PDF-файлов

-------------------------------------------------------------------------------
ОГЛАВЛЕНИЕ
-------------------------------------------------------------------------------

1. О программе
2. Возможности
3. Установка
4. Запуск
5. Использование
6. Наборы данных
7. Архитектура
8. Требования
9. Конфигурация


-------------------------------------------------------------------------------
1. О ПРОГРАММЕ
-------------------------------------------------------------------------------

ChemX Extractor - веб-приложение для автоматического извлечения структурированных 
химических данных из научных PDF-статей. Использует большие языковые модели 
(LLM) для парсинга текста и таблиц, поддерживает 10+ предметных областей, 
обогащение через PubChem и оценку качества извлечения.

Интерфейс реализован на Streamlit, поддерживает работу с OpenRouter, OpenAI, 
Gemini и Claude.


-------------------------------------------------------------------------------
2. ВОЗМОЖНОСТИ
-------------------------------------------------------------------------------

- Извлечение данных для 10+ предопределённых химических наборов данных
- Парсинг PDF: текст + таблицы (pdfplumber)
- LLM-извлечение через OpenAI-совместимые API
- Автоматическое обогащение SMILES через PubChem и CIR NIH
- Определение SMILES для производных соединений (отсутствуют в PubChem)
- Верификация извлечённых данных вторым проходом LLM
- Оценка качества: Macro-F1, Precision, Recall
- Удобный веб-интерфейс с тёмной темой
- Экспорт результатов в CSV и JSON


-------------------------------------------------------------------------------
3. УСТАНОВКА
-------------------------------------------------------------------------------

Клонирование репозитория:

git clone https://github.com/yourusername/chemx-extractor.git
cd chemx-extractor

Создание виртуального окружения:

python -m venv venv

Активация:

- Linux/Mac:   source venv/bin/activate
- Windows:     venv\Scripts\activate

Установка зависимостей:

pip install -r requirements.txt


-------------------------------------------------------------------------------
4. ЗАПУСК
-------------------------------------------------------------------------------

streamlit run app.py

После запуска откройте браузер по адресу: http://localhost:8501


-------------------------------------------------------------------------------
5. ИСПОЛЬЗОВАНИЕ
-------------------------------------------------------------------------------

5.1. Настройка API

В боковой панели укажите API ключ:
- OpenRouter: sk-or-v1-...
- OpenAI:     sk-proj-...

Выберите провайдера и модель.

5.2. Вкладка "Extraction" (Извлечение)

Шаги:
1. Выберите набор данных в боковой панели
2. Загрузите один или несколько PDF-файлов
3. Настройте опции:
   - PubChem enrichment - автоматическое определение SMILES
   - Verification pass - второй проход LLM для проверки
4. Нажмите "Run extraction"
5. Просмотрите результаты в таблице
6. Скачайте результат в CSV или JSON

5.3. Вкладка "Evaluation" (Оценка)

Шаги:
1. Загрузите файл с предсказаниями (CSV)
2. Загрузите gold-стандарт (CSV или Parquet)
3. Выберите набор данных
4. Нажмите "Compute F1"
5. Получите метрики: Macro-F1, Precision, Recall


-------------------------------------------------------------------------------
6. НАБОРЫ ДАННЫХ
-------------------------------------------------------------------------------

6.1. EyeDrops
Проницаемость роговицы и липофильность препаратов для глазных капель
Поля: smiles, name, perm (cm/s), logP

6.2. Nanozymes
Нанозимы: кинетика ферментоподобной активности
Поля: formula, activity, syngony, length, width, depth, surface, km_value, 
      km_unit, vmax_value, vmax_unit, target_source, reaction_type, c_min, 
      c_max, c_const, c_const_unit, ccat_value, ccat_unit, ph, temperature

6.3. Synergy
Синергизм наночастиц и антибиотиков/пептидов против бактерий
Поля: NP, bacteria, strain, NP_synthesis, drug, drug_dose_µg_disk, 
      NP_concentration_µg_ml, NP_size_min_nm, NP_size_max_nm, NP_size_avg_nm,
      shape, method, ZOI_drug_mm_or_MIC_µg_ml, error_ZOI_drug_mm_or_MIC_µg_ml,
      ZOI_NP_mm_or_MIC_np_µg_ml, error_ZOI_NP_mm_or_MIC_np_µg_ml,
      ZOI_drug_NP_mm_or_MIC_drug_NP_µg_ml, error_ZOI_drug_NP_mm_or_MIC_drug_NP_µg_ml,
      fold_increase_in_antibacterial_activity, zeta_potential_mV, MDR, FIC,
      effect, time_hr, coating_with_antimicrobial_peptide_polymers,
      combined_MIC, peptide_MIC, viability_%, viability_error

6.4. Nanomag
Магнитные свойства магнитных наночастиц
Поля: name, np_shell_2, np_hydro_size, xrd_scherrer_size, zfc_h_meas, 
      htherm_sar, mri_r1, mri_r2, emic_size, instrument, core_shell_formula,
      np_core, np_shell, space_group_core, space_group_shell, squid_h_max,
      fc_field_T, squid_temperature, squid_sat_mag, coercivity, squid_rem_mag,
      exchange_bias_shift_Oe, vertical_loop_shift_M_vsl_emu_g, hc_kOe

6.5. Cytotox
Цитотоксичность наночастиц (жизнеспособность клеток)
Поля: material, shape, coat_functional_group, synthesis_method, surface_charge,
      size_in_medium_nm, zeta_in_medium_mv, no_of_cells_cells_well,
      human_animal, cell_source, cell_tissue, cell_morphology, cell_age,
      time_hr, concentration, test, test_indicator, viability_%, core_nm,
      hydrodynamic_nm, potential_mv, cell_type

6.6. SelTox
Антимикробная активность и токсичность наночастиц серебра
Поля: np, coating, bacteria, mdr, strain, np_synthesis, method, 
      mic_np_µg_ml, concentration, zoi_np_mm, np_size_min_nm, np_size_max_nm,
      np_size_avg_nm, shape, time_set_hours, zeta_potential_mV,
      solvent_for_extract, temperature_for_extract_C, duration_preparing_extract_min,
      precursor_of_np, concentration_of_precursor_mM, hydrodynamic_diameter_nm,
      ph_during_synthesis

6.7. Benzimidazoles
Антибактериальная активность (MIC) производных бензимидазола
Поля: smiles, compound_id, target_type, target_relation, target_value, 
      target_units, bacteria

6.8. Oxazolidinones
Антибактериальная активность оксазолидинонов
Поля: smiles, compound_id, target_type, target_relation, target_value, 
      target_units, bacteria

6.9. Co-crystals
Свойства фармацевтических сокристаллов
Поля: name_cocrystal, ratio_cocrystal, name_drug, SMILES_drug, name_coformer,
      SMILES_coformer, photostability_change

6.10. Complexes
Металло-лигандные комплексы
Поля: compound_id, compound_name, SMILES, metal, target


-------------------------------------------------------------------------------
7. АРХИТЕКТУРА
-------------------------------------------------------------------------------

7.1. Пайплайн обработки

PDF -> pdfplumber -> Текст + Таблицы
                          |
                          v
                     LLM (извлечение)
                          |
                          v
                 Верификация (опционально)
                          |
                          v
                 PubChem обогащение
                          |
                          v
                 Экспорт (CSV/JSON)

7.2. Основные функции

parse_pdf()
  Извлечение текста, таблиц, DOI и заголовка из PDF

extract_from_pdf()
  Основной пайплайн извлечения

call_llm()
  Универсальный вызов LLM с повторными попытками

pubchem_lookup()
  Получение SMILES из PubChem и CIR NIH

llm_smiles_for_derivatives()
  Определение SMILES для производных соединений через LLM

compute_macro_f1()
  Вычисление Macro-F1, Precision, Recall


-------------------------------------------------------------------------------
8. ТРЕБОВАНИЯ
-------------------------------------------------------------------------------

- Python 3.9 или выше

Зависимости (requirements.txt):

pdfplumber >= 0.10.3    - парсинг PDF
PyMuPDF   >= 1.23.0     - работа с PDF
openai    >= 1.30.0     - LLM API
pandas    >= 2.0.0      - обработка данных
requests  >= 2.31.0     - HTTP-запросы
streamlit >= 1.35.0     - веб-интерфейс
pyarrow   >= 14.0.0     - поддержка Parquet


-------------------------------------------------------------------------------
9. КОНФИГУРАЦИЯ
-------------------------------------------------------------------------------

9.1. API ключи

Переменные окружения:
OPENAI_API_KEY = "sk-..."   # или укажите в интерфейсе

9.2. Провайдеры

OpenRouter: https://openrouter.ai/api/v1
OpenAI:     https://api.openai.com/v1

9.3. Поддерживаемые модели

- openai/gpt-4o
- openai/gpt-4o-mini
- anthropic/claude-sonnet-4-5
- google/gemini-2.0-flash
- gpt-4o
- gpt-4o-mini
