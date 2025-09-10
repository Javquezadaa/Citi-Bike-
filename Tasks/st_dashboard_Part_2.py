# ------------------------- IMPORT LIBRARIES -------------------------
import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime as dt
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------- PAGE CONFIG -------------------------
st.set_page_config(page_title='Citi Bike Dashboard', layout='wide')

# ------------------------- PAGE SELECTION -------------------------
page = st.sidebar.selectbox(
    "Select an aspect of the analysis",
    [
        "Intro page",
        "Weather component and bike usage",
        "Most popular stations",
        "Hourly Heatmap",
        "Interactive map with aggregated bike trips",
        "Recommendations"
    ]
)

# ------------------------- LOAD DATA -------------------------
df = pd.read_csv('..Data/df_2022.csv', parse_dates=['started_at','ended_at','date'])

# ------------------------- CREATE COLUMNS -------------------------
df['month'] = df['date'].dt.month.astype(int)
df['hour'] = df['started_at'].dt.hour
df['weekday'] = df['started_at'].dt.day_name()

df['season'] = [
    "winter" if (month == 12 or 1 <= month <= 2)
    else "spring" if (3 <= month <= 5)
    else "summer" if (6 <= month <= 8)
    else "fall"
    for month in df['month']
]

# ========================= INTRO PAGE =========================
if page == "Intro page":
    st.title("Citi Bike 2022 Analysis")
    
    st.markdown("""
    Welcome to the Citi Bike 2022 interactive dashboard.  

    **Objective:**  
    Analyze Citi Bike usage to help the business strategy team optimize bike distribution, address availability issues, and guide future expansion efforts.

    **Context:**  
    Citi Bike has seen increasing demand, especially after the Covid-19 pandemic, which has led to distribution problems such as empty or full stations.  
    This dashboard helps visualize key metrics and trends to make data-driven decisions.

    Use the dropdown menu on the left to explore the analysis pages:

    - Weather component and bike usage  
    - Most popular stations  
    - Hourly Heatmap  
    - Interactive map with aggregated bike trips  
    - Recommendations
    """)
    
    cover_image = Image.open("Tasks/spenser-sembrat-grJeAdDMxEc-unsplash.jpg")
    st.image(cover_image, use_container_width=True)

# ========================= WEATHER COMPONENT & BIKE USAGE =========================
elif page == "Weather component and bike usage":
    st.header("Daily Bike Rides vs Temperature")
    
    df_daily = df.groupby('date', as_index=False).agg({'started_at':'count'})
    df_daily.rename(columns={'started_at':'bike_rides_daily'}, inplace=True)
    
    if 'TAVG' in df.columns:
        df_temp = df.groupby('date', as_index=False).agg({'TAVG':'mean'})
        df_daily = df_daily.merge(df_temp, on='date', how='left')
    else:
        df_daily['TAVG'] = np.nan
    
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_line.add_trace(
        go.Scatter(
            x=df_daily['date'],
            y=df_daily['bike_rides_daily'],
            name='Daily Bike Rides',
            line=dict(color='blue')
        ),
        secondary_y=False
    )
    
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
    
    # Insights
    monthly_avg = df_daily.groupby(df_daily['date'].dt.month).agg({'bike_rides_daily':'mean'}).reset_index()
    st.markdown(f"""
    **Insights:**
    - Bike usage peaks in summer (highest monthly average: {monthly_avg['bike_rides_daily'].max():.0f} rides) and dips in winter (lowest monthly average: {monthly_avg['bike_rides_daily'].min():.0f} rides).
    - Clear correlation between temperature and bike usage.
    """)

# ========================= MOST POPULAR STATIONS =========================
elif page == "Most popular stations":
    st.header("Top 20 Most Popular Start Stations")
    
    season_filter = st.sidebar.multiselect(
        "Select the season",
        options=df['season'].unique(),
        default=df['season'].unique()
    )
    
    df1 = df.query('season == @season_filter')
    total_rides = float(df1.shape[0])
    st.metric(label="Total Bike Rides", value=f"{int(total_rides):,}")
    
    df1['value'] = 1
    top20 = df1.groupby('start_station_name', as_index=False).agg({'value':'sum'}).nlargest(20,'value')
    
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
    
    st.markdown("""
    **Insights:**
    - Top stations are dynamically calculated from the dataset.
    - Seasonal patterns show summer has the highest activity at top stations.
    - Filtering by season highlights bottlenecks in high-demand periods.
    """)

# ========================= HOURLY HEATMAP =========================
elif page == "Hourly Heatmap":
    st.header("Heatmap of Trips by Hour and Weekday")
    
    hourly = df.groupby(['weekday', 'hour']).size().reset_index(name='trip_count')
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hourly['weekday'] = pd.Categorical(hourly['weekday'], categories=weekday_order, ordered=True)
    
    heatmap_data = hourly.pivot(index="weekday", columns="hour", values="trip_count")
    
    fig, ax = plt.subplots(figsize=(14,6))
    sns.heatmap(heatmap_data, cmap="YlGnBu", linewidths=.5, ax=ax)
    ax.set_title("Heatmap of Trips by Hour and Weekday")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week")
    
    st.pyplot(fig)
    
 st.header("Hourly Heatmap: Trips by Weekday and Hour")
st.pyplot(fig_heatmap)  # assuming you created fig_heatmap with seaborn/matplotlib

st.markdown("""
**Insights from Heatmap:**
- Morning (7–9 AM) and evening (5–7 PM) peaks indicate heavy commuter traffic.  
- Weekday demand concentrates around work/business districts.  
- Weekend patterns are more leisure-oriented, spreading trips across mid-day.""")

# ========================= INTERACTIVE MAP =========================
elif page == "Interactive map with aggregated bike trips":
    st.header("Aggregated Bike Trips in NYC")
    path_to_html = "Tasks/citibike_2022_map.html"
    
    try:
        with open(path_to_html, 'r') as f:
            html_data = f.read()
        st.components.v1.html(html_data, height=1000)
    except:
        st.warning(f"{path_to_html} not found. Skipping map display.")
    
    st.markdown("""
    **Insights:**
    - Aggregated trips highlight the most trafficked routes and stations.
    - Clusters appear in downtown and tourist areas; sparse trips elsewhere.
    - Useful for planning station expansions or redistribution efforts.
    """)

# ========================= RECOMMENDATIONS =========================
else:
    st.header("Conclusion and Recommendations")
    
    recs_image = Image.open("Tasks/broadway-5813302_1280.jpg")
    st.image(recs_image, use_container_width=True)
    
    st.markdown("### Strategic Recommendations for Citi Bike NYC")
    
    st.markdown("1. **Optimize Bike Distribution Seasonally**  \n"
                "- Increase bike availability during warmer months (May–October) when usage peaks.  \n"
                "- Reduce surplus in colder months to minimize logistics costs.")
    
    st.markdown("2. **Expand Stations at High-Demand Locations**  \n"
                "- Focus on areas along the waterfront and major tourist or business hubs.  \n"
                "- Key locations include Millennium Park, Streeter Drive/Grand Avenue, and Canal Street/Adams Street.")
    
    st.markdown("3. **Address Popular Station Bottlenecks**  \n"
                "- Monitor top stations with high bike traffic to prevent empty or full stations.  \n"
                "- Implement dynamic redistribution or add docks where necessary.")
    
    st.markdown("4. **Leverage Weather Data for Operational Planning**  \n"
                "- Use temperature and weather trends to anticipate demand.  \n"
                "- Adjust bike availability dynamically for sunny, rainy, or extremely cold days.")
    
    st.markdown("5. **Enhance User Experience with Real-Time Updates**  \n"
                "- Provide users with live bike and dock availability via the app.  \n"
                "- Suggest alternative stations to reduce congestion at popular locations.")
    
    st.markdown("""**Conclusion:** These recommendations integrate **seasonality, location, and time-of-day patterns**.
Implementing them will improve availability, reduce customer complaints, and guide Citi Bike NYC’s strategic growth.""")