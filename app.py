import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from scipy.stats import gaussian_kde
from datetime import date

st.set_page_config("Analysis of weather data in Canada", layout="wide")
st.title("Analysis of weather data in Canada ☔️")
st.markdown("---")
st.subheader("Overview")
st.markdown("This dashboard provides a multifaceted analysis of the weather dataset, enabling users to explore trends, patterns, and key metrics across temperature, humidity, wind, visibility, pressure, and weather conditions. The visualizations support understanding of temporal changes, distribution of weather phenomena, and relationships between variables, empowering data-driven insights for climate analysis and operational planning.")

def load_data():
    return pd.read_csv(".venv/weather_dataset.csv")
df = load_data()

df['Date/Time'] = pd.to_datetime(df['Date/Time'])
columns = df.select_dtypes(include=['number']).columns.tolist()

with st.expander("Standart metrics 📊"):
    st.dataframe(df[columns].describe())

st.markdown("---")
select_date = st.sidebar.date_input('Select time interval', (df['Date/Time'].min(), df['Date/Time'].max()),
                                    min_value=df['Date/Time'].min(), max_value=df['Date/Time'].max(),
                                    key='select_date')
df_filtred = df[df['Date/Time'].dt.date.between(select_date[0], select_date[1])]

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average temperature 🌡️", f"{df_filtred['Temp_C'].mean():.2f}")
    with col2:
        st.metric("Maximum wind speed 💨", f"{df_filtred['Wind Speed_km/h'].max()}")
    with col3:
            st.metric("Average humidity 💧", f"{df_filtred['Rel Hum_%'].mean():.2f}")

#Interactive graph of daily average temperature
df_daily = df_filtred.groupby(df_filtred['Date/Time'].dt.date)['Temp_C'].mean().reset_index()
fig1 = px.line(
    df_daily,
    x='Date/Time',
    y='Temp_C',
    title='Daily Average Temperature Trend'
)
fig1.update_xaxes(
    tickformat='%d-%b',
    title_text='Date'
)
fig1.update_yaxes(
    title_text='Temperature, °C'
)
fig1.update_traces(
    hovertemplate="<br>".join([
        "Date: %{x|%d-%b-%Y}",
        "Temperature: %{y:.2f}°C",
    ])
)
st.plotly_chart(fig1, use_container_width=True)

with st.container():
    cola,colb = st.columns(2)
    with cola:
        #Interactive pie chart of weather type
        weather_counts = df_filtred['Weather'].value_counts()
        df_weather = weather_counts.reset_index()
        df_weather.columns = ['Weather', 'Count']
        fig = px.pie(
            df_weather,
            names='Weather',
            values='Count',
            title='Weather Condition Distribution',
            hole=0.5
        )
        fig.update_traces(
            textposition='inside',
            textinfo='value',
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)
    with colb:
        #Interactive histogram of weather types
        df_weather_top = df_weather.sort_values(by='Count', ascending=False).head(10)
        fig = px.bar(
            df_weather_top,
            x='Weather',
            y='Count',
            title='Weather Type Frequency'
        )
        fig.update_traces(
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)

#Interactive humidity kde plot
if not df_filtred.empty:
    kde = gaussian_kde(df_filtred['Rel Hum_%'])
    x_vals = np.linspace(df_filtred['Rel Hum_%'].min(), df_filtred['Rel Hum_%'].max(), 100)
    y_vals = kde(x_vals)
    kde_df = pd.DataFrame({'Humidity': x_vals, 'Density': y_vals})
    fig = px.line(
        kde_df,
        x='Humidity',
        y='Density',
        title='Relative humidity density chart'
    )
    fig.update_xaxes(title_text='Relative humidity (%)')
    fig.update_yaxes(title_text='Density')
    fig.update_layout(
        title_font_size=24,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Error: There is no data to display for the selected date range")

st.markdown("---")
with st.container():
    st.subheader('Daytime temperature trend')
    df['Date'] = df['Date/Time'].dt.date
    dates = df['Date'].unique()
    select_day = st.selectbox('Select day:', options=dates, index=0, key='select_day')
    df_days = df[df['Date'] == select_day]
    fig4 = px.line(
        df_days,
        x='Date/Time',
        y='Temp_C'
    )
    fig4.update_xaxes(title_text='Date and time')
    fig4.update_yaxes(title_text='Temperature °C')
    fig4.update_traces(
        hovertemplate="<br>".join([
            "Time: %{x|%H:%M}",
            "Temperature: %{y:.2f}°C",
        ])
    )
    st.plotly_chart(fig4, use_container_width=True)
