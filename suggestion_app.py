# import pandas as pd
# import streamlit as st

# # Load and clean data
# df = pd.read_csv('large_scale_ai_models_added_cols.csv')
# df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# # Convert numeric fields
# numeric_cols = [
#     'training_power_(watts)', 'parameters', 'training_compute_(flop)',
#     'training_dataset_size_(datapoints)', 'training_time_(hours)',
#     'hardware_quantity', 'finetune_compute_(flop)'
# ]
# for col in numeric_cols:
#     if col in df.columns:
#         df[col] = pd.to_numeric(df[col], errors='coerce')

# # UI setup
# st.title("AI Model Suggestion Tool")
# st.markdown("Enter the task you want to perform, and the model will recommend the most suitable AI systems based on efficiency and scale.")

# # Dropdown for tasks
# available_tasks = df['task'].dropna().unique()
# task_input = st.selectbox("Choose a task:", sorted(available_tasks))

# # Additional filters
# max_power = min(int(df['training_power_(watts)'].max(skipna=True)), 9_007_199_254_740_991)
# power_limit = st.slider("Max Training Power (Watts)", min_value=0, max_value=max_power, value=max_power)
# param_limit = st.slider("Max Parameters (in billions)", min_value=0, max_value=1000, value=1000)
# top_k = st.slider("Number of top suggestions", min_value=1, max_value=10, value=5)

# if task_input:
#     # Filter based on task and constraints
#     filtered = df[df['task'].str.contains(task_input, case=False, na=False)]
#     filtered = filtered[
#         (filtered['training_power_(watts)'] <= power_limit) &
#         (filtered['parameters'] <= param_limit * 1e9)
#     ]

#     if not filtered.empty:
#         # Sort by power efficiency and parameters
#         suggestion = filtered.sort_values(['training_power_(watts)', 'parameters']).head(top_k)

#         st.success("Top Suggestions:")
#         st.dataframe(suggestion[[
#             'system', 'task', 'training_power_(watts)', 'parameters', 'organization', 'training_compute_(flop)', 'training_time_(hours)'
#         ]])

#         st.download_button(
#             label="Download suggestions as CSV",
#             data=suggestion.to_csv(index=False),
#             file_name='suggested_models.csv',
#             mime='text/csv'
#         )
#     else:
#         st.warning("No matching models found for this task within your constraints.")




# Streamlit app for AI model suggestion
import pandas as pd
import streamlit as st

# Cache data loading for performance
@st.cache_data
def load_data():
    df = pd.read_csv('large_scale_ai_models_added_cols.csv')
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    # Convert numeric fields
    numeric_cols = [
        'training_power_(watts)', 'parameters', 'training_compute_(flop)',
        'training_dataset_size_(datapoints)', 'training_time_(hours)',
        'hardware_quantity', 'finetune_compute_(flop)'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# Load data
df = load_data()

# UI setup
st.title("AI Model Suggestion Tool")
st.markdown(
    "Enter your task and adjust sliders — the suggestions will auto-update as you move the controls."
)

# Task dropdown
available_tasks = df['task'].dropna().unique()
task_input = st.selectbox("Choose a task:", sorted(available_tasks))

# Sliders
JS_MAX_INT = (1 << 53) - 1
max_power = min(int(df['training_power_(watts)'].max(skipna=True)), JS_MAX_INT)
power_limit = st.slider(
    "Max Training Power (Watts)", 0, max_power, max_power
)
param_limit = st.slider("Max Parameters (in billions)", 0, 1000, 1000)
top_k = st.slider("Number of top suggestions", 1, 10, 5)

# Filter & display suggestions
def get_suggestions(task, power_lim, param_lim, k):
    filtered = df[df['task'].str.contains(task, case=False, na=False)]
    filtered = filtered[
        (filtered['training_power_(watts)'] <= power_lim) &
        (filtered['parameters'] <= param_lim * 1e9)
    ]
    if filtered.empty:
        return None
    return filtered.sort_values(
        ['training_power_(watts)', 'parameters']
    ).head(k)

# Generate suggestions on any widget change
gsuggestion = get_suggestions(task_input, power_limit, param_limit, top_k)
if gsuggestion is not None:
    st.success("Top Suggestions:")
    st.dataframe(gsuggestion[[
        'system', 'task', 'training_power_(watts)', 'parameters',
        'organization', 'training_compute_(flop)', 'training_time_(hours)'
    ]])
    st.download_button(
        "Download suggestions as CSV", gsuggestion.to_csv(index=False),
        file_name='suggested_models.csv', mime='text/csv'
    )
else:
    st.warning("No matching models found.")



# # import pandas as pd
# # import streamlit as st

# # # Cache data loading for performance
# # @st.cache_data
# # def load_data():
# #     df = pd.read_csv('large_scale_ai_models_added_cols.csv')
# #     df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
# #     # Convert numeric fields
# #     numeric_cols = [
# #         'training_power_(watts)', 'parameters', 'training_compute_(flop)',
# #         'training_dataset_size_(datapoints)', 'training_time_(hours)',
# #         'hardware_quantity', 'finetune_compute_(flop)'
# #     ]
# #     for col in numeric_cols:
# #         if col in df.columns:
# #             df[col] = pd.to_numeric(df[col], errors='coerce')
# #     return df

# # # Load data
# # df = load_data()

# # # UI setup
# # st.title("AI Model Suggestion Tool")
# # st.markdown(
# #     "Enter your task and adjust sliders — the suggestions will auto-update as you move the controls."
# # )

# # # Task dropdown
# # available_tasks = df['task'].dropna().unique()
# # task_input = st.selectbox("Choose a task:", sorted(available_tasks))

# # # Sliders or Number input for power
# # actual_max_power = int(df['training_power_(watts)'].max(skipna=True))
# # JS_MAX_INT = (1 << 53) - 1

# # if actual_max_power <= JS_MAX_INT:
# #     power_limit = st.slider(
# #         "Max Training Power (Watts)",
# #         min_value=0,
# #         max_value=actual_max_power,
# #         value=actual_max_power
# #     )
# # else:
# #     st.warning(f"Max training power {actual_max_power} exceeds JavaScript safe integer. Using number input instead.")
# #     power_limit = st.number_input(
# #         "Max Training Power (Watts)",
# #         min_value=0,
# #         max_value=actual_max_power,
# #         value=actual_max_power
# #     )

# # # Other sliders
# # param_limit = st.slider("Max Parameters (in billions)", 0, 1000, 1000)
# # top_k = st.slider("Number of top suggestions", 1, 10, 5)

# # # Suggestion logic
# # def get_suggestions(task, power_lim, param_lim, k):
# #     filtered = df[df['task'].str.contains(task, case=False, na=False)]
# #     filtered = filtered[
# #         (filtered['training_power_(watts)'] <= power_lim) &
# #         (filtered['parameters'] <= param_lim * 1e9)
# #     ]
# #     if filtered.empty:
# #         return None
# #     return filtered.sort_values(
# #         ['training_power_(watts)', 'parameters']
# #     ).head(k)

# # # Display suggestions
# # gsuggestion = get_suggestions(task_input, power_limit, param_limit, top_k)
# # if gsuggestion is not None:
# #     st.success("Top Suggestions:")
# #     st.dataframe(gsuggestion[[
# #         'system', 'task', 'training_power_(watts)', 'parameters',
# #         'organization', 'training_compute_(flop)', 'training_time_(hours)'
# #     ]])
# #     st.download_button(
# #         "Download suggestions as CSV",
# #         gsuggestion.to_csv(index=False),
# #         file_name='suggested_models.csv',
# #         mime='text/csv'
# #     )
# # else:
# #     st.warning("No matching models found.")




# import pandas as pd
# import streamlit as st

# # Cache data loading for performance
# @st.cache_data
# def load_data():
#     df = pd.read_csv('large_scale_ai_models_added_cols.csv')
#     df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
#     # Convert numeric fields
#     numeric_cols = [
#         'training_power_(watts)', 'parameters', 'training_compute_(flop)',
#         'training_dataset_size_(datapoints)', 'training_time_(hours)',
#         'hardware_quantity', 'finetune_compute_(flop)', 'training_energy_(kwh)'
#     ]
#     for col in numeric_cols:
#         if col in df.columns:
#             df[col] = pd.to_numeric(df[col], errors='coerce')
#     # Parse publication date
#     if 'publication_date' in df.columns:
#         df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
#     return df

# # Load data
# df = load_data()

# # UI setup
# st.title("AI Model Suggestion & Comparison Tool")
# st.markdown("Enter your task, adjust constraints, and compare energy usage over time.")

# # Task dropdown
# available_tasks = df['task'].dropna().unique()
# task_input = st.selectbox("Choose a task:", sorted(available_tasks))

# # Sliders for constraints
# JS_MAX_INT = (1 << 53) - 1
# actual_max_power = int(df['training_power_(watts)'].max(skipna=True))
# max_power = min(actual_max_power, JS_MAX_INT)
# power_limit = st.slider("Max Training Power (Watts)", 0, max_power, max_power)
# param_limit = st.slider("Max Parameters (in billions)", 0, 1000, 1000)
# top_k = st.slider("Number of top suggestions", 1, 10, 5)

# # Suggestion function
# def get_suggestions(task, power_lim, param_lim, k):
#     filtered = df[df['task'].str.contains(task, case=False, na=False)]
#     filtered = filtered[
#         (filtered['training_power_(watts)'] <= power_lim) &
#         (filtered['parameters'] <= param_lim * 1e9)
#     ]
#     if filtered.empty:
#         return pd.DataFrame()
#     return filtered.sort_values(['training_power_(watts)', 'parameters']).head(k)

# # Generate suggestions
# gsuggestion = get_suggestions(task_input, power_limit, param_limit, top_k)
# if not gsuggestion.empty:
#     st.success("Top Suggestions:")
#     st.dataframe(gsuggestion[[
#         'system', 'task', 'training_power_(watts)', 'parameters',
#         'organization', 'training_compute_(flop)', 'training_time_(hours)'
#     ]])
#     st.download_button("Download suggestions as CSV", gsuggestion.to_csv(index=False),
#                        file_name='suggested_models.csv', mime='text/csv')
# else:
#     st.warning("No matching models found for this task within your constraints.")

# # Energy comparison over time
# st.subheader("Energy Consumption Over Time")
# # Current model selector
# current_model = st.selectbox("Select your current model:", sorted(df['system'].dropna().unique()))
# # Models to compare: current + recommended
# compare_list = [current_model] + gsuggestion['system'].tolist()

# df_plot = df[df['system'].isin(compare_list)]
# # Ensure dates and energy are present
# df_plot = df_plot.dropna(subset=['publication_date', 'training_energy_(kwh)'])
# if not df_plot.empty:
#     pivot = df_plot.pivot(index='publication_date', columns='system', values='training_energy_(kwh)')
#     st.line_chart(pivot)
# else:
#     st.info("No energy-over-time data available for selected models.")
