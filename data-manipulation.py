import streamlit as st
import pandas as pd
import altair as alt

# --- Page config ---
st.set_page_config(page_title="AI Model Explorer", layout="wide")

# --- Data loading & cleaning ---
@st.cache_data
def load_data(path='notable_ai_models.csv'):
    df = pd.read_csv(path)
    # normalize column names
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r"[ \(\)]", "_", regex=True)
    )
    # parse dates
    if 'publication_date' in df.columns:
        df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    # numeric conversions
    for col in [
        'parameters', 'training_compute_flop',
        'training_dataset_size_datapoints', 'training_power_draw_w',
        'citations', 'training_time_hours'
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    # split domain into list
    if 'domain' in df.columns:
        df['domain_list'] = df['domain'].str.split(r'\s*,\s*')
    return df

# load dataframe
df = load_data()

# auto-detected metric columns
domain_col = 'domain_list'
power_col = 'training_power_draw_w'
cite_col = 'citations'

# --- Sidebar navigation ---
tab = st.sidebar.radio("Navigate to", ["🔍 Suggest", "📊 Plot"])

# --- Suggest Tab ---
if tab == "🔍 Suggest":
    st.header("Model Suggestion by Domain")
    # domain selector
    domains = sorted({d for lst in df[domain_col].dropna() for d in lst})
    domain = st.selectbox("Select a domain", domains)
    top_k = st.slider("How many suggestions?", 1, 20, 5)
    # filter by domain
    mask = df[domain_col].apply(lambda lst: domain in lst if isinstance(lst, list) else False)
    df_dom = df[mask]
    # require both citations and power
    if power_col in df_dom.columns and cite_col in df_dom.columns:
        df_dom = df_dom.dropna(subset=[power_col, cite_col])
        df_dom = df_dom.sort_values(by=[cite_col, power_col], ascending=[False, True])
    suggestions = df_dom.head(top_k)
    if not suggestions.empty:
        display = ['model', 'organization', 'publication_date', cite_col]
        if power_col in suggestions.columns:
            display.append(power_col)
        st.table(suggestions[display])
    else:
        st.warning("No models match your criteria.")

# --- Plot Tab ---
else:
    st.header("Custom Plot Explorer")
    # domain filter
    domains = sorted({d for lst in df[domain_col].dropna() for d in lst})
    selected = st.multiselect("Filter by domain (optional)", domains, default=domains)
    mask = df[domain_col].apply(lambda lst: any(d in lst for d in selected) if isinstance(lst, list) else False)
    df_plot = df[mask]
    # choose axes
    numeric_date = [
        c for c in df_plot.columns
        if pd.api.types.is_numeric_dtype(df_plot[c])
        or pd.api.types.is_datetime64_any_dtype(df_plot[c])
    ]
    x_col = st.selectbox("X axis", numeric_date,
                         index=numeric_date.index('publication_date')
                               if 'publication_date' in numeric_date else 0)
    y_choices = [c for c in numeric_date if c != x_col]
    y_col = st.selectbox("Y axis", y_choices)
    df_xy = df_plot[[x_col, y_col]].dropna()
    x_type = 'temporal' if pd.api.types.is_datetime64_any_dtype(df_xy[x_col]) else 'quantitative'
    y_type = 'temporal' if pd.api.types.is_datetime64_any_dtype(df_xy[y_col]) else 'quantitative'
    chart = (
        alt.Chart(df_xy)
           .mark_circle(size=60)
           .encode(
               x=alt.X(x_col, type=x_type, title=x_col.replace('_', ' ').title()),
               y=alt.Y(y_col, type=y_type, title=y_col.replace('_', ' ').title()),
               tooltip=[x_col, y_col]
           )
           .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
 