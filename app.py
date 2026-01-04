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
simulated_tasks_df = pd.read_csv("simulated_worker_tasks.csv", parse_dates=["task_date"])

# -------------------------------
# Sidebar - Tabs & Filters
# -------------------------------
st.sidebar.header("Navigation")
tabs = ["KPIs", "SLA Compliance", "Pareto Analysis", "Learning Curve", "Worker-Level Analysis"]
selected_tab = st.sidebar.radio("Select Tab", tabs)

# Segment Filter
segments = dashboard_df['performance_segment'].unique().tolist()
selected_segment = st.sidebar.multiselect(
    "Filter by Performance Segment:",
    options=segments,
    default=segments
)

filtered_df = dashboard_df[dashboard_df['performance_segment'].isin(selected_segment)]

# -------------------------------
# Tab 1: KPIs
# -------------------------------
if selected_tab == "KPIs":
    st.title("📊 SLA Dashboard - KPIs")
    st.markdown("High-level overview of workforce performance.")

    total_workers = len(filtered_df)
    avg_sla = filtered_df['sla_pct'].mean().round(2)
    top_workers = len(filtered_df[filtered_df['performance_segment']=='Top Performer'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Workers", total_workers)
    col2.metric("Average SLA Compliance (%)", avg_sla)
    col3.metric("Top Performers", top_workers)

# -------------------------------
# Tab 2: SLA Compliance
# -------------------------------
elif selected_tab == "SLA Compliance":
    st.title("🎯 SLA Compliance by Worker")

    fig_sla = px.bar(
        filtered_df.sort_values('sla_pct', ascending=False),
        x='worker_id',
        y='sla_pct',
        color='performance_segment',
        color_discrete_map={'Top Performer':'#2ca02c', 'Mid Performer':'#ff7f0e', 'Low Performer':'#d62728'},
        labels={'sla_pct':'SLA Compliance (%)','worker_id':'Worker ID'},
        hover_data=['avg_accuracy','total_tasks']
    )
    st.plotly_chart(fig_sla, use_container_width=True)

    # Horizontal Bars for Accuracy & Tasks
    st.subheader("Worker Performance Metrics")
    worker_perf_df = filtered_df.sort_values("total_tasks", ascending=True)

    fig_tasks = px.bar(
        worker_perf_df,
        x="total_tasks",
        y="worker_id",
        orientation="h",
        color="performance_segment",
        labels={"total_tasks":"Total Tasks Completed","worker_id":"Worker ID"},
        color_discrete_map={'Top Performer': '#2ca02c','Mid Performer':'#ff7f0e','Low Performer':'#d62728'},
        title="Total Tasks per Worker"
    )
    st.plotly_chart(fig_tasks, use_container_width=True)

    fig_accuracy = px.bar(
        worker_perf_df,
        x="avg_accuracy",
        y="worker_id",
        orientation="h",
        color="performance_segment",
        labels={"avg_accuracy":"Average Accuracy","worker_id":"Worker ID"},
        color_discrete_map={'Top Performer': '#2ca02c','Mid Performer':'#ff7f0e','Low Performer':'#d62728'},
        title="Average Accuracy per Worker"
    )
    st.plotly_chart(fig_accuracy, use_container_width=True)

    # SLA Met vs Not Met
    sla_days_df = worker_perf_df.melt(
        id_vars=["worker_id","performance_segment"],
        value_vars=["days_sla_met","days_sla_not_met"],
        var_name="SLA_Status",
        value_name="Days"
    )
    sla_days_df["SLA_Status"] = sla_days_df["SLA_Status"].map({"days_sla_met":"SLA Met","days_sla_not_met":"SLA Not Met"})

    fig_sla_days = px.bar(
        sla_days_df,
        x="Days",
        y="worker_id",
        orientation="h",
        color="SLA_Status",
        labels={"Days":"Number of Days","worker_id":"Worker ID"},
        color_discrete_map={"SLA Met":"#2ca02c","SLA Not Met":"#d62728"},
        title="Days SLA Met vs Not Met per Worker"
    )
    st.plotly_chart(fig_sla_days, use_container_width=True)

# -------------------------------
# Tab 3: Pareto Analysis
# -------------------------------
elif selected_tab == "Pareto Analysis":
    st.title("🏆 Pareto Analysis")
    pareto_df = filtered_df.sort_values('total_tasks', ascending=False)
    pareto_df['cumulative_tasks'] = pareto_df['total_tasks'].cumsum()
    pareto_df['cumulative_pct'] = 100 * pareto_df['cumulative_tasks'] / pareto_df['total_tasks'].sum()
    pareto_cutoff = int(0.2 * len(pareto_df))
    top_pareto_workers = pareto_df.iloc[:pareto_cutoff]

    st.write(f"Top 20% workers ({pareto_cutoff}) contribute {top_pareto_workers['total_tasks'].sum()} tasks out of {pareto_df['total_tasks'].sum()} total tasks.")

    fig_pareto = px.bar(
        pareto_df,
        x='worker_id',
        y='total_tasks',
        color='performance_segment',
        hover_data=['cumulative_pct'],
        labels={'total_tasks':'Tasks Completed','worker_id':'Worker ID'},
        color_discrete_map={'Top Performer':'#2ca02c','Mid Performer':'#ff7f0e','Low Performer':'#d62728'}
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

# -------------------------------
# Tab 4: Learning Curve
# -------------------------------
elif selected_tab == "Learning Curve":
    st.title("📈 Learning Curve Simulation")
    st.markdown("Visualize cumulative accuracy improvement over tasks for a selected worker.")

    worker_choice = st.selectbox("Select Worker:", filtered_df['worker_id'].tolist())
    df_worker = simulated_tasks_df[simulated_tasks_df['worker_id']==worker_choice].sort_values(['task_date','task_id'])
    df_worker['cumulative_accuracy'] = df_worker['accuracy'].expanding().mean()

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df_worker['task_id'], df_worker['cumulative_accuracy'], marker='o', linestyle='-', color='blue')
    ax.set_xlabel("Task Sequence")
    ax.set_ylabel("Cumulative Accuracy")
    ax.set_title(f"Learning Curve for {worker_choice}")
    st.pyplot(fig)

# -------------------------------
# Tab 5: Worker-Level Analysis
# -------------------------------
elif selected_tab == "Worker-Level Analysis":
    st.title("🔍 Detailed Worker-Level Metrics")
    st.markdown("Explore individual worker performance and SLA history.")

    selected_worker = st.selectbox("Select Worker ID:", filtered_df['worker_id'].tolist())
    worker_data = filtered_df[filtered_df['worker_id']==selected_worker]
    st.dataframe(worker_data)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("© 2025 SLA Analytics Dashboard")
