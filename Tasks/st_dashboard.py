# Step 5.------------------------- IMPORT LIBRARIES -------------------------
import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
from datetime import datetime as dt

# ------------------------- PAGE CONFIG -------------------------
st.set_page_config(page_title='Citi Bike Dashboard', layout='wide')
st.title("Citi Bike 2022 Dashboard")
st.markdown("This dashboard visualizes bike trips in New York City with interactive charts and a map.")

# ------------------------- LOAD DATA -------------------------
df = pd.read_csv('..Data/df_2022.csv', parse_dates=['started_at','ended_at','date'])

# ------------------------- CREATE COLUMNS -------------------------
df['month'] = df['date'].dt.month.astype(int)
df['season'] = [
    "winter" if (month == 12 or 1 <= month <= 2)
    else "spring" if (3 <= month <= 5)
    else "summer" if (6 <= month <= 8)
    else "fall"
    for month in df['month']
]

# ------------------------- BAR CHART: TOP 20 STATIONS -------------------------
df['value'] = 1
top20 = df.groupby('start_station_name', as_index=False).agg({'value':'sum'}).nlargest(20,'value')

fig_bar = go.Figure(go.Bar(
    x=top20['start_station_name'],
    y=top20['value'],
    marker={'color': top20['value'], 'colorscale': 'Blues'}
))
fig_bar.update_layout(
    title='Top 20 Most Popular Start Stations',
    xaxis_title='Start Station',
    yaxis_title='Number of Trips',
    width=900,
    height=600
)
st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------- DUAL-AXIS LINE CHART -------------------------
# Aggregate daily bike rides
df_daily = df.groupby('date', as_index=False).agg({'value':'sum'})
df_daily.rename(columns={'value':'bike_rides_daily'}, inplace=True)

# Average temperature (TAVG) per day
df_temp = df.groupby('date', as_index=False).agg({'TAVG':'mean'})
df_daily = df_daily.merge(df_temp, on='date', how='left')

fig_line = make_subplots(specs=[[{"secondary_y": True}]])

# Daily bike rides
fig_line.add_trace(
    go.Scatter(
        x=df_daily['date'], 
        y=df_daily['bike_rides_daily'], 
        name='Daily Bike Rides',
        line=dict(color='blue')
    ),
    secondary_y=False
)

# Average daily temperature
fig_line.add_trace(
    go.Scatter(
        x=df_daily['date'], 
        y=df_daily['TAVG'], 
        name='Average Temp',
        line=dict(color='red')
    ),
    secondary_y=True
)

fig_line.update_layout(
    title='Daily Bike Rides vs Average Temperature',
    xaxis_title='Date',
    yaxis_title='Number of Bike Rides',
    height=600
)
fig_line.update_yaxes(title_text="Average Temperature (°F)", secondary_y=True)

st.plotly_chart(fig_line, use_container_width=True)

# ------------------------- ADD KEPLER MAP -------------------------
path_to_html = "Tasks/citibike_2022_map.html"

# Read file and keep in variable 
with open(path_to_html, 'r') as f:
    html_data = f.read()

# Show in web page
st.header("Aggregated Bike Trips in Chicago")
st.components.v1.html(html_data, height=1000)