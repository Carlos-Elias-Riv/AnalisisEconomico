import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import awswrangler as wr

# Set page config
st.set_page_config(
    page_title="Economic Indicators Analysis",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("Economic Indicators Analysis")
st.markdown("""
This app displays regression analyses between different economic indicators:
- Exchange Rate vs Interest Rate
- Interest Rate vs Inflation
- Exchange Rate vs Inflation
""")

# Function to load data from Athena
def load_data():
    # Query to join all tables
    query = """
    SELECT 
        tc.date,
        tc.tipo_de_cambio,
        ti.tasa_de_interes,
        inf.inflacion
    FROM tipo_de_cambio tc
    JOIN tasa_de_interes ti ON tc.date = ti.date 
    JOIN inflacion inf ON tc.date = inf.date
    """
    
    return wr.athena.read_sql_query(
        sql=query,
        database="econ"
    )

# Function to create regression plot
def create_regression_plot(x, y, xlabel, ylabel, title):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create scatter plot
    ax.scatter(x, y, alpha=0.5)
    
    # Fit regression line
    model = LinearRegression()
    X = x.values.reshape(-1, 1)
    model.fit(X, y)
    
    # Generate points for regression line
    x_line = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)
    y_line = model.predict(x_line)
    
    # Plot regression line
    ax.plot(x_line, y_line, 'r-', label=f'R² = {model.score(X, y):.4f}')
    
    # Customize plot
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig

# Load data
try:
    with st.spinner('Loading data from Athena...'):
        df = load_data()
    
    # Create three columns for the plots
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Exchange Rate vs Interest Rate")
        fig1 = create_regression_plot(
            df['tasa_de_interes'],
            df['tipo_de_cambio'],
            'Interest Rate',
            'Exchange Rate',
            'Exchange Rate vs Interest Rate'
        )
        st.pyplot(fig1)
    
    with col2:
        st.subheader("Interest Rate vs Inflation")
        fig2 = create_regression_plot(
            df['inflacion'],
            df['tasa_de_interes'],
            'Inflation',
            'Interest Rate',
            'Interest Rate vs Inflation'
        )
        st.pyplot(fig2)
    
    with col3:
        st.subheader("Exchange Rate vs Inflation")
        fig3 = create_regression_plot(
            df['inflacion'],
            df['tipo_de_cambio'],
            'Inflation',
            'Exchange Rate',
            'Exchange Rate vs Inflation'
        )
        st.pyplot(fig3)
    
    # Display data table
    st.subheader("Raw Data")
    st.dataframe(df)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please make sure you have the correct AWS credentials and permissions to access Athena.") 