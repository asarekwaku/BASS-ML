import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv('large_scale_ai_models_added_cols.csv')

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Convert relevant numeric columns to numeric type
df['training_power_(watts)'] = pd.to_numeric(df['training_power_(watts)'], errors='coerce')
df['training_compute_(flop)'] = pd.to_numeric(df['training_compute_(flop)'], errors='coerce')

# Filter top 30 by power
df_top30 = df.dropna(subset=['training_power_(watts)', 'training_compute_(flop)']) \
             .nlargest(30, 'training_power_(watts)')

# -------------------------
# Plot 1: Power vs System
# -------------------------
plt.figure(figsize=(14, 6))
plt.bar(df_top30.sort_values('training_power_(watts)', ascending=False)['system'],
        df_top30.sort_values('training_power_(watts)', ascending=False)['training_power_(watts)'])
plt.xticks(rotation=75, ha='right')
plt.ylabel('Training Power (Watts)')
plt.title('Training Power vs System (Top 30)')
plt.tight_layout()
plt.show()

# -------------------------
# Plot 2: Power vs Task
# -------------------------
plt.figure(figsize=(14, 6))
plt.bar(df_top30.sort_values('training_power_(watts)', ascending=False)['task'],
        df_top30.sort_values('training_power_(watts)', ascending=False)['training_power_(watts)'])
plt.xticks(rotation=75, ha='right')
plt.ylabel('Training Power (Watts)')
plt.title('Training Power vs Task (Top 30)')
plt.tight_layout()
plt.show()

# system and task are the same for each model, so we can use either one
plt.figure(figsize=(14, 6))

# Sort and prepare data
df_sorted = df_top30.sort_values('training_power_(watts)', ascending=False)
labels = df_sorted['task'] + ' - ' + df_sorted['system']

# Plot
plt.bar(labels, df_sorted['training_power_(watts)'])
plt.xticks(rotation=75, ha='right')
plt.ylabel('Training Power (Watts)')
plt.title('Training Power vs Task-System (Top 30)')
plt.tight_layout()
plt.show()

# -------------------------
# Plot 3: FLOP vs System
# -------------------------
plt.figure(figsize=(14, 6))
plt.bar(df_top30.sort_values('training_compute_(flop)', ascending=False)['system'],
        df_top30.sort_values('training_compute_(flop)', ascending=False)['training_compute_(flop)'])
plt.xticks(rotation=75, ha='right')
plt.ylabel('Training Compute (FLOP)')
plt.title('Training Compute (FLOP) vs System (Top 30 by Power)')
plt.tight_layout()
plt.show()

'''
Make a bar plot of power as a function of system with nulls taken out 
Make a bar plot of power as a function of task with nulls taken out 
Make a bar plot of FLOP as a function of system with nulls taken out 
'''

# # -------------------------
# # Plot 4: Power vs System (All Data)
# # -------------------------
# plt.figure(figsize=(12, 6))
# plt.barh(df.sort_values('training_power_(watts)', ascending=False)['system'],
#          df.sort_values('training_power_(watts)', ascending=False)['training_power_(watts)'])
# plt.xlabel('Training Power (Watts)')
# plt.title('Training Power vs System (All Data)')
# plt.gca().invert_yaxis()


# plt.tight_layout()

# plt.show()


# # -------------------------
# # Plot 5: Power vs Task (All Data)
# # -------------------------
# plt.figure(figsize=(12, 6))             
# plt.barh(df.sort_values('training_power_(watts)', ascending=False)['task'],
#          df.sort_values('training_power_(watts)', ascending=False)['training_power_(watts)'])
# plt.xlabel('Training Power (Watts)')
# plt.title('Training Power vs Task (All Data)')
# plt.gca().invert_yaxis()
# plt.tight_layout()
# plt.show()
# # -------------------------
# # Plot 6: FLOP vs System (All Data)
# # -------------------------

# plt.figure(figsize=(14, 6))             
# plt.bar(df.sort_values('training_compute_(flop)', ascending=False)['system'],
#         df.sort_values('training_compute_(flop)', ascending=False)['training_compute_(flop)'])              
# plt.xticks(rotation=75, ha='right')
# plt.ylabel('Training Compute (FLOP)')
# plt.title('Training Compute (FLOP) vs System (All Data)')
# plt.tight_layout()
# plt.show()

