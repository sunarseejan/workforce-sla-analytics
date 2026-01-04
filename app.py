import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

sns.set_theme(style="whitegrid")

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Gig Workers SLA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Load Dashboard Dataset
# -------------------------------
dashboard_df = pd.read_csv("dashboard_worker_metrics.csv")

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

segments = dashboard_df['performance_segment'].unique().tolist()
selected_segment = st.sidebar.multiselect(
    "Select Performance Segment:",
    options=segments,
    default=segments
)

# Filter data
filtered_df = dashboard_df[dashboard_df['performance_segment'].isin(selected_segment)]

# -------------------------------
# Main Page
# -------------------------------
st.title("📊 SLA Analytics Dashboard")
st.markdown("""
This interactive dashboard allows stakeholders to monitor SLA compliance, identify top performers, and explore workforce performance trends.
""")

# -------------------------------
# KPI Cards
# -------------------------------
total_workers = len(filtered_df)
avg_sla = filtered_df['sla_pct'].mean().round(2)
top_workers = len(filtered_df[filtered_df['performance_segment']=='Top Performer'])

col1, col2, col3 = st.columns(3)
col1.metric("Total Workers", total_workers)
col2.metric("Average SLA Compliance (%)", avg_sla)
col3.metric("Top Performers", top_workers)

# -------------------------------
# SLA Compliance Bar Chart
# -------------------------------
st.subheader("SLA Compliance by Worker")
fig_sla = px.bar(
    filtered_df.sort_values('sla_pct', ascending=False),
    x='worker_id',
    y='sla_pct',
    color='performance_segment',
    color_discrete_map={
        'Top Performer':'#2ca02c',
        'Mid Performer':'#ff7f0e',
        'Low Performer':'#d62728'
    },
    labels={'sla_pct':'SLA Compliance (%)','worker_id':'Worker ID'},
    hover_data=['avg_accuracy','total_tasks']
)
st.plotly_chart(fig_sla, use_container_width=True)

# -------------------------------
# Accuracy vs Task Count Scatter
# -------------------------------
st.subheader("Worker Accuracy vs Task Count")
fig_scatter = px.scatter(
    filtered_df,
    x='total_tasks',
    y='avg_accuracy',
    color='performance_segment',
    size='sla_pct',
    hover_name='worker_id',
    color_discrete_map={
        'Top Performer':'#2ca02c',
        'Mid Performer':'#ff7f0e',
        'Low Performer':'#d62728'
    },
    labels={'avg_accuracy':'Average Accuracy','total_tasks':'Total Tasks'}
)
st.plotly_chart(fig_scatter, use_container_width=True)

# -------------------------------
# Pareto Analysis
# -------------------------------
st.subheader("Pareto Analysis: Top 20% Workers")
# Sort by total tasks
pareto_df = filtered_df.sort_values('total_tasks', ascending=False)
pareto_df['cumulative_tasks'] = pareto_df['total_tasks'].cumsum()
pareto_df['cumulative_pct'] = 100 * pareto_df['cumulative_tasks'] / pareto_df['total_tasks'].sum()
pareto_cutoff = int(0.2 * len(pareto_df))
top_pareto_workers = pareto_df.iloc[:pareto_cutoff]

st.write(f"Top 20% workers ({pareto_cutoff} workers) contribute {top_pareto_workers['total_tasks'].sum()} tasks out of {pareto_df['total_tasks'].sum()} total tasks.")

fig_pareto = px.bar(
    pareto_df,
    x='worker_id',
    y='total_tasks',
    color='performance_segment',
    labels={'total_tasks':'Tasks Completed','worker_id':'Worker ID'},
    hover_data=['cumulative_pct']
)
st.plotly_chart(fig_pareto, use_container_width=True)

# -------------------------------
# Learning Curve Simulation (Optional)
# -------------------------------
st.subheader("Learning Curve Simulation")
st.markdown("Visualize cumulative accuracy improvement for a selected worker over tasks.")

worker_choice = st.selectbox("Select Worker:", filtered_df['worker_id'].tolist())

# Load synthetic dataset for learning curve
df_tasks = pd.read_csv("simulated_worker_tasks.csv", parse_dates=["task_date"])
df_worker = df_tasks[df_tasks['worker_id']==worker_choice].sort_values(['task_date','task_id'])
df_worker['cumulative_accuracy'] = df_worker['accuracy'].expanding().mean()

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df_worker['task_id'], df_worker['cumulative_accuracy'], marker='o', linestyle='-', color='blue')
ax.set_xlabel("Task Sequence")
ax.set_ylabel("Cumulative Accuracy")
ax.set_title(f"Learning Curve for {worker_choice}")
st.pyplot(fig)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("© 2025 CloudFactory SLA Analytics Dashboard")
