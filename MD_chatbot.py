import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google import genai
import numpy as np

# ---------------------------
# 1. Gemini Client
# ---------------------------
client = genai.Client(api_key="AIzaSyBNuE1WsAeEKbYne0apxuZnVUCvM2bW7BY")  # Replace with your actual API key

# ---------------------------
# 2. Load CSVs
# ---------------------------
df_productivity = pd.read_csv("C:\\Users\\Asus\\Documents\\manfacture_downtime\\Line_Productivity.csv", encoding="utf-8")
df_product = pd.read_csv("C:\\Users\\Asus\\Documents\\manfacture_downtime\\Products.csv", encoding="utf-8")
df_factors = pd.read_csv("C:\\Users\\Asus\\Documents\\manfacture_downtime\\Downtime_Factors.csv", encoding="utf-8")
df_downtime = pd.read_csv("C:\\Users\\Asus\\Documents\\manfacture_downtime\\Line_Downtime.csv", encoding="utf-8")


# ---------------------------
# 3. Streamlit Setup
# ---------------------------
st.set_page_config(page_title="Manufacturing Downtime Chatbot", page_icon="🏭", layout="wide")

st.markdown("""
<style>
/* Set the background of the entire page */
body {
  background-color: #E9E3DF;
}

/* Optional: Streamlit main container */
[data-testid="stAppViewContainer"] {
  background-color: #E9E3DF;
}

/* Banner styling */
.banner {
  background: linear-gradient(90deg, #6CA6CD, #8FCB9B);
  color: white;
  padding: 2rem 1rem;
  border-radius: 0 0 25px 25px;
  text-align: center;
  box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
}
.banner h1 {
  font-size: 2.3rem;
  margin-bottom: 0.4rem;
  font-weight: 800;
}
.banner p {
  font-size: 1.1rem;
  opacity: 0.95;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #E9E3DF 0%, #6CA6CD 100%);
}

/* Response box styling */
.response-box {
  background-color: #E9E3DF;
  border-radius: 12px;
  border-left: 6px solid #8FCB9B;
  padding: 1.2rem;
  margin-top: 1rem;
  font-size: 1.05rem;
  box-shadow: 0px 2px 8px rgba(140,200,160,0.2);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner">
    <h1>🏭 Manufacturing Downtime Chatbot</h1>
    <p>Analyze productivity, downtime causes, and operator performance</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------
# 5. AI Question Section
# ---------------------------
st.sidebar.header("💬 Ask a Question")
preset_questions = [
    "Which operator has the highest downtime?",
    "What are the top causes of downtime?",
    "Which product is most efficient?",
    "Is there a pattern in downtime across days?",
    "How does batch duration compare to expected time?"
]
selected_question = st.sidebar.radio("Choose a question:", options=[""] + preset_questions)

if selected_question:
    user_question = selected_question
else:
    user_question = st.text_area("💬 Type your own question below:")

 

if st.button("🔍 Get Answer"):
    if not user_question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("🔬 Analyzing data ..."):
            prompt = f"""
            You are a manufacturing analyst. Here's the full dataset:

            Line_Downtime:
            {df_downtime.to_csv(index=False)}

            Line_Productivity:
            {df_productivity.to_csv(index=False)}

            Products:
            {df_product.to_csv(index=False)}

            Downtime_Factors:
            {df_factors.to_csv(index=False)}



            Question: {user_question}

            Please answer clearly, in a professional and human-friendly way suitable for factory insights, Give summarized answer with recommendations.
            """
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.markdown("### ✅ Analysis:")
                st.write(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                # ---------------------------
                # Generate relevant chart based on question
                chart_data = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""based on the manufacturing downtime dataset,
                Line_Downtime:
                {df_downtime.to_csv(index=False)}

                Line_Productivity:
                {df_productivity.to_csv(index=False)}

                Products:
                {df_product.to_csv(index=False)}

                Downtime_Factors:
                {df_factors.to_csv(index=False)} ,
                and the user question {user_question}, Provide only Python code using pandas and matplotlib to generate relevant charts based on the following preloaded DataFrames:
                - df_downtime: contains columns Batch, Factor, Downtime
                - df_factors: contains columns Factor, Description, Operator Error
                - df_productivity: contains columns Date, Product, Batch, Operator, Start Time, End Time
                - df_product: contains columns Product, Flavor, Size, Min batch time
                Ensure the code can be run as-is in a Streamlit app. Do not include any explanations or additional text.
                Do not import libraries; assume pandas, matplotlib.pyplot, seaborn, and streamlit are already imported as pd, plt, sns, and st respectively.
                Do not include data loading; assume the DataFrames are preloaded. Provide only the code.
                Do not write the code in a markdown block; provide it as plain text.
                write the code in a way that it displays the chart directly in Streamlit using st.pyplot().
                write the code in a simple and straight way , no need to use unnecessary details.
                """
                )
                st.markdown("### 📊 Chart :")
                exec(chart_data.text)
            except Exception as e:
                st.error(f"Error: {e}")
    
# ---------------------------
# 6. Interactive Dashboard Section
# ---------------------------
st.markdown("""<div class="banner"><h1>🏭 Manufacturing Downtime Dashboard</h1></div>""", unsafe_allow_html=True)

# Clean timestamps
df_productivity['Start Time'] = df_productivity['Start Time'].str.strip()
df_productivity['End Time'] = df_productivity['End Time'].str.strip()
df_productivity['Start Time'] = pd.to_datetime(df_productivity['Date'] + ' ' + df_productivity['Start Time'], errors='coerce')
df_productivity['End Time'] = pd.to_datetime(df_productivity['Date'] + ' ' + df_productivity['End Time'], errors='coerce')
df_productivity['End Time'] = df_productivity.apply(
    lambda row: row['End Time'] + pd.Timedelta(days=1) if row['End Time'] < row['Start Time'] else row['End Time'],
    axis=1
)
df_productivity['Actual Duration'] = (df_productivity['End Time'] - df_productivity['Start Time']).dt.total_seconds() / 60
df_productivity['Date'] = pd.to_datetime(df_productivity['Date'])

# Merge data
df = df_productivity.merge(df_product, on='Product', how='left')
batch_downtime = df_downtime.groupby('Batch')['Downtime'].sum().reset_index()
df = df.merge(batch_downtime, on='Batch', how='left')
df['Downtime'] = df['Downtime'].fillna(0)
df['Efficiency'] = df['Actual Duration'] / df['Min batch time']

# Sidebar filters
st.sidebar.header("🔍 Filter Panel")
min_date = df['Date'].min()
max_date = df['Date'].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])
selected_products = st.sidebar.multiselect("Select Products", df['Product'].unique(), default=df['Product'].unique())
selected_operators = st.sidebar.multiselect("Select Operators", df['Operator'].unique(), default=df['Operator'].unique())

# Apply filters
df_filtered = df[
    (df['Date'] >= pd.to_datetime(selected_dates[0])) &
    (df['Date'] <= pd.to_datetime(selected_dates[1])) &
    (df['Product'].isin(selected_products)) &
    (df['Operator'].isin(selected_operators))
]

# CSS styling
st.markdown("""
<style>
body { background-color: #E9E3DF; }
[data-testid="stAppViewContainer"] { background-color: #E9E3DF; }
.kpi-card {
    background-color: #F0F8FF;
    border-left: 6px solid #6CA6CD;
    padding: 1.2rem;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 1rem;
}
.kpi-title {
    font-size: 1.1rem;
    color: #2A4D69;
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: #1B6CA8;
}
.chart-title {
    font-size: 1.2rem;
    color: #2A4D69;
    background-color: #F0F8FF;
    border-left: 6px solid #6CA6CD;
    padding: 1.2rem;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)



# KPIs
total_batches = len(df_filtered)
total_downtime = df_filtered['Downtime'].sum()
average_efficiency = df_filtered['Efficiency'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Total Batches</div><div class="kpi-value">{total_batches}</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Total Downtime</div><div class="kpi-value">{total_downtime:.0f} min</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Avg Efficiency</div><div class="kpi-value">{average_efficiency:.2f}</div></div>""", unsafe_allow_html=True)

# Chart 1: Top Downtime Causes
downtime_summary = df_downtime.merge(df_factors, on='Factor')
downtime_by_factor = downtime_summary.groupby('Description')['Downtime'].sum().sort_values(ascending=False).head(10)

col4, col5 = st.columns(2)
with col4:
    st.markdown('<div class="chart-title">🔧 Top 10 Downtime Causes</div>', unsafe_allow_html=True)
    fig1, ax1 = plt.subplots(figsize=(7, 5))
    sns.barplot(x=downtime_by_factor.values, y=downtime_by_factor.index, ax=ax1, palette='Blues_r')
    ax1.set_xlabel("Total Downtime (min)")
    ax1.set_ylabel("Cause")
    st.pyplot(fig1)
    st.markdown('</div>', unsafe_allow_html=True)

# Chart 2: Downtime by Operator
operator_downtime = df_filtered.groupby('Operator')['Downtime'].sum().sort_values(ascending=False).reset_index()
with col5:
    st.markdown('<div class="chart-title">👷‍♂️ Downtime by Operator</div>', unsafe_allow_html=True)
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    sns.barplot(data=operator_downtime, x='Downtime', y='Operator', ax=ax2, palette='Greens')
    ax2.set_xlabel("Total Downtime (min)")
    ax2.set_ylabel("Operator")
    st.pyplot(fig2)
    st.markdown('</div>', unsafe_allow_html=True)

# Chart 3: Efficiency by Product
col6, col7 = st.columns(2)
with col6:
    st.markdown('<div class="chart-title">📦 Efficiency by Product</div>', unsafe_allow_html=True)
    fig3, ax3 = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=df_filtered, x='Efficiency', y='Product', palette='Blues')
    ax3.set_xlabel("Efficiency Ratio")
    ax3.set_ylabel("Product")
    st.pyplot(fig3)
    st.markdown('</div>', unsafe_allow_html=True)

# Chart 4: Downtime Over Time
daily_downtime = df_filtered.groupby('Date')['Downtime'].sum().reset_index()
with col7:
    st.markdown('<div class="chart-title">📅 Downtime Over Time</div>', unsafe_allow_html=True)
    fig4, ax4 = plt.subplots(figsize=(7, 5))
    sns.lineplot(data=daily_downtime, x='Date', y='Downtime', marker='o', ax=ax4)
    ax4.set_ylabel("Downtime (min)")
    ax4.set_xlabel("Date")
    plt.xticks(rotation=45)
    st.pyplot(fig4)
    st.markdown('</div>', unsafe_allow_html=True)