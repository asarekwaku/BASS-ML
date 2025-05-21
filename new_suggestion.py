import pandas as pd
import streamlit as st
import difflib

# Page config
st.set_page_config(page_title="AI Model Explorer", layout="wide")

# --- Data Loading & Caching ---
@st.cache_data
def load_models():
    df = pd.read_csv('large_scale_ai_models_added_cols.csv')
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    # Numeric conversions
    num_cols = [
        'training_power_(watts)', 'training_energy_(kwh)', 'parameters',
        'training_compute_(flop)', 'training_dataset_size_(datapoints)',
        'training_time_(hours)', 'hardware_quantity', 'finetune_compute_(flop)'
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    # Date parsing
    if 'publication_date' in df.columns:
        df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    return df

@st.cache_data
def load_emissions():
    em = pd.read_csv('bloom_emissions.csv')
    em.columns = em.columns.str.strip().str.lower().str.replace(' ', '_')
    # Rename emissions column if needed
    if 'emissions' in em.columns:
        em = em.rename(columns={'emissions': 'carbon_emissions_(kg_co2)'})
    if 'carbon_emissions_(kg_co2)' in em.columns:
        em['carbon_emissions_(kg_co2)'] = pd.to_numeric(em['carbon_emissions_(kg_co2)'], errors='coerce')
    return em

def merge_emissions(models_df, em_df):
    # Merge on project_name to system
    if 'project_name' in em_df.columns and 'carbon_emissions_(kg_co2)' in em_df.columns:
        df = models_df.merge(
            em_df[['project_name', 'carbon_emissions_(kg_co2)']],
            left_on='system', right_on='project_name', how='left'
        )
        # Fuzzy fallback for unmatched entries
        mask = df['carbon_emissions_(kg_co2)'].isna()
        if mask.any():
            names = em_df['project_name'].dropna().astype(str).tolist()
            def match(name):
                if not isinstance(name, str) or not name.strip():
                    return None
                m = difflib.get_close_matches(name, names, n=1, cutoff=0.8)
                return m[0] if m else None
            df.loc[mask, 'matched_project'] = df.loc[mask, 'system'].apply(match)
            df = df.merge(
                em_df[['project_name', 'carbon_emissions_(kg_co2)']],
                left_on='matched_project', right_on='project_name',
                how='left', suffixes=('', '_fuzzy')
            )
            # Combine exact and fuzzy
            df['carbon_emissions_(kg_co2)'] = df['carbon_emissions_(kg_co2)'].fillna(
                df.get('carbon_emissions_(kg_co2)_fuzzy')
            )
        # Clean up
        to_drop = [col for col in ['project_name', 'matched_project', 'carbon_emissions_(kg_co2)_fuzzy'] if col in df.columns]
        df = df.drop(columns=to_drop)
        return df
    return models_df

# Load and merge data
df_models = load_models()
df_em = load_emissions()
df_models = merge_emissions(df_models, df_em)

# Load data dictionaries
df_ai_dict = pd.read_csv('ai_models_data_dictionary.csv')
df_bloom_dict = pd.read_csv('bloom_data_dictionary.csv')
df_ai_dict.columns = df_ai_dict.columns.str.strip().str.lower().str.replace(' ', '_')
df_bloom_dict.columns = df_bloom_dict.columns.str.strip().str.lower().str.replace(' ', '_')

# --- App UI Tabs ---
tab = st.sidebar.radio("Navigate to", ["🔍 Suggest", "🌱 Emissions Explorer", "ℹ️ Field Glossary"])

JS_MAX_INT = (1 << 53) - 1

if tab == "🔍 Suggest":
    st.header("Model Suggestion")
    # Task selector
    task_list = sorted(df_models['task'].dropna().unique())
    task = st.selectbox("Select a task:", task_list)
    # Power slider
    raw_max_power = int(df_models['training_power_(watts)'].max(skipna=True) or 0)
    max_power = min(raw_max_power, JS_MAX_INT)
    if raw_max_power > JS_MAX_INT:
        st.warning(f"Max training power {raw_max_power} exceeds JS limit; clamped to {JS_MAX_INT}.")
    help_power = df_ai_dict.loc[df_ai_dict['field']=='training_power_(watts)','description'].squeeze() if 'field' in df_ai_dict.columns else None
    power = st.slider("Max Training Power (Watts)", 0, max_power, max_power, help=help_power)
    # Parameters slider
    help_params = df_ai_dict.loc[df_ai_dict['field']=='parameters','description'].squeeze() if 'field' in df_ai_dict.columns else None
    params = st.slider("Max Parameters (billions)", 0, 1000, 1000, help=help_params)
    # CO2 slider
    co2 = None
    if 'carbon_emissions_(kg_co2)' in df_models.columns:
        raw_max_co2 = int(df_models['carbon_emissions_(kg_co2)'].max(skipna=True) or 0)
        max_co2 = min(raw_max_co2, JS_MAX_INT)
        if raw_max_co2 > JS_MAX_INT:
            st.warning(f"Max CO₂ {raw_max_co2} exceeds JS limit; clamped to {JS_MAX_INT}.")
        help_co2 = df_bloom_dict.loc[df_bloom_dict['field']=='carbon_emissions_(kg_co2)','description'].squeeze() if 'field' in df_bloom_dict.columns else None
        co2 = st.slider("Max Carbon Emissions (kg CO₂)", 0, max_co2, max_co2, help=help_co2)
    # Top K
    topk = st.slider("Number of suggestions", 1, 10, 5)
    # Filter and show
    sel = df_models[df_models['task'].str.contains(task, case=False, na=False)]
    sel = sel[(sel['training_power_(watts)']<=power) & (sel['parameters']<=params*1e9)]
    if co2 is not None:
        sel = sel[sel['carbon_emissions_(kg_co2)']<=co2]
    sug = sel.sort_values(['training_power_(watts)','parameters'], na_position='last').head(topk)
    if not sug.empty:
        cols = ['system','task','training_power_(watts)','training_energy_(kwh)','parameters','organization']
        if co2 is not None:
            cols.insert(4,'carbon_emissions_(kg_co2)')
        st.dataframe(sug[cols])
    else:
        st.warning("No models match your criteria.")

elif tab == "🌱 Emissions Explorer":
    st.header("Bloom Emissions Explorer")
    if 'project_name' in df_em.columns:
        names = sorted(df_em['project_name'].dropna().unique())
        sel_proj = st.multiselect("Select projects:", names, default=names[:3])
        df_e = df_em[df_em['project_name'].isin(sel_proj)]
        if 'carbon_emissions_(kg_co2)' in df_e.columns:
            st.bar_chart(df_e.set_index('project_name')['carbon_emissions_(kg_co2)'])
        else:
            st.info("No carbon emissions data available.")
    else:
        st.info("Emissions data lacks 'project_name' column.")

else:
    st.header("Data Field Glossary")
    dict_choice = st.selectbox("Choose dictionary:", ["AI Models","Bloom Emissions"])
    dd = df_ai_dict if dict_choice=="AI Models" else df_bloom_dict
    if 'field' in dd.columns and 'description' in dd.columns:
        st.dataframe(dd.rename(columns={'field':'Column','description':'Description'})[['Column','Description']])
    else:
        st.info("Selected dictionary missing expected fields.")
