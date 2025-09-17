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
import plotly.express as px  

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
        "Trip Duration by User Type",
        "Interactive map with aggregated bike trips",
        "Recommendations"
    ]
)

# ------------------------- LOAD DATA -------------------------
df = pd.read_csv(
    "Compressed CSV files/df_2022.csv.gz",
    compression="gzip",
    parse_dates=['started_at','ended_at','date']
)

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

# Calculate trip duration in minutes
df['duration_min'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60

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
    - Trip Duration by User Type  
    - Interactive map with aggregated bike trips  
    - Recommendations
    """)

    # Display cover image
    from PIL import Image
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
    
    df1 = df[df['season'].isin(season_filter)]  # fixed for list filtering
    total_rides = float(df1.shape[0])
    st.metric(label="Total Bike Rides", value=f"{int(total_rides):,}")
    
    df1['value'] = 1
    top20 = df1.groupby('start_station_name', as_index=False).agg({'value':'sum'}).nlargest(20,'value')
    top5_list = top20['start_station_name'].head(5).tolist()
    
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
    
    st.markdown(f"""
    **Insights:**
    - The busiest stations are concentrated in **Manhattan**, particularly near transit hubs and high-traffic areas.  
    - The current top 5 start stations are: **{top5_list}**.  
    - Seasonal filtering reveals higher usage in **summer months**, indicating increased strain on these popular docks.  
    - These high-demand locations are also where **dock imbalance issues** (empty or full stations) are most likely to occur.  
    """)

# ========================= INTERACTIVE HOURLY HEATMAP WITH HOUR SLIDER =========================
elif page == "Hourly Heatmap":
    st.header("Hourly Heatmap: Trips by Weekday and Hour")

    # Day filter
    filter_option = st.selectbox("Select days to display:", ["All Days", "Weekdays Only", "Weekend Only"])

    # Hour range slider
    hour_range = st.slider("Select hour range:", 0, 23, (0, 23))

    # Define weekday order
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Group by weekday and hour
    hourly = df.groupby(['weekday', 'hour']).size().reset_index(name='trip_count')

    # Filter by day
    if filter_option == "Weekdays Only":
        hourly = hourly[hourly['weekday'].isin(weekday_order[:5])]
        hourly['weekday'] = pd.Categorical(hourly['weekday'], categories=weekday_order[:5], ordered=True)
    elif filter_option == "Weekend Only":
        hourly = hourly[hourly['weekday'].isin(weekday_order[5:])]
        hourly['weekday'] = pd.Categorical(hourly['weekday'], categories=weekday_order[5:], ordered=True)
    else:
        hourly['weekday'] = pd.Categorical(hourly['weekday'], categories=weekday_order, ordered=True)

    # Filter by selected hour range
    hourly = hourly[(hourly['hour'] >= hour_range[0]) & (hourly['hour'] <= hour_range[1])]

    # Pivot for heatmap
    heatmap_data = hourly.pivot(index="weekday", columns="hour", values="trip_count").fillna(0)

    # Create interactive heatmap
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Hour of Day", y="Day of Week", color="Trip Count"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale="YlGnBu"
    )

    fig.update_layout(
        title="Interactive Heatmap of Trips by Hour and Weekday",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        yaxis=dict(categoryorder="array", categoryarray=heatmap_data.index)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Insights:**
    - Clear **commuter peaks**: 7–9 AM and 5–7 PM on weekdays.  
    - **Weekend demand** shifts to mid-day (10 AM-8PM).  
    - Time-of-day patterns highlight the need for **dynamic bike rebalancing**.
    """)

# ========================= TRIP DURATION BY USER TYPE =========================
elif page == "Trip Duration by User Type":
    st.header("Trip Duration by User Type")

    # Compute trip duration in minutes
    df['duration_min'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60

    fig_box = go.Figure()

    for user_type in df['member_casual'].unique():
        fig_box.add_trace(go.Box(
            y=df[df['member_casual'] == user_type]['duration_min'],
            name=user_type,
            boxpoints='outliers',
            marker_color='blue' if user_type == 'member' else 'orange'
        ))

    fig_box.update_layout(
        yaxis=dict(title="Trip Duration (minutes)", range=[0, 180]),  # cap at 3 hours
        xaxis_title="User Type",
        title="Distribution of Trip Duration by User Type",
        height=600
    )

    st.plotly_chart(fig_box, width='stretch')

    st.markdown("""
    **Insights:**
    - **Members** tend to have shorter trips on average, often using bikes for commuting or daily errands.  
    - **Casual riders** show a wider range of trip durations, including longer rides for leisure or tourism.  
    - By capping the Y-axis at 180 minutes, we focus on the majority of trips while still preserving the overall distribution.  
    - Operationally, this suggests **peak-duration bikes** should prioritize members during morning/evening commutes, while casual riders’ trips are more spread throughout the day.  
    """)
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
    st.image(recs_image, use_container_width=True)  # updated parameter
    
    st.markdown("### Strategic Recommendations for Citi Bike NYC")
    
    st.markdown("""
1. **Optimize Bike Distribution Seasonally**  
   - Increase bike availability during warmer months .  
   - Reduce surplus in colder months to minimize logistics costs.

2. **Expand Stations at High-Demand Locations**  
   - Focus on areas along the waterfront, major tourist destinations, and business hubs.  
   - Key locations include Manhattan hotspots like Millennium Park, Streeter Drive/Grand Avenue, Canal Street/Adams Street, and transit hubs.

3. **Address Popular Station Bottlenecks**  
   - Monitor top stations with high bike traffic to prevent empty or full stations.  
   
4. **Leverage Weather Data for Operational Planning**  
   - Use temperature and weather trends to anticipate daily demand.  
   
5. **Plan for Hourly Demand Peaks**  
   - Allocate extra bikes during weekday peaks to serve commuters.  
   - Redistribute bikes in the afternoon or on weekends based on leisure travel patterns identified.

6. **Enhance Repair and Maintenance System**  
   - Schedule maintenance and repairs based on usage patterns to ensure bikes are always functional.  
   - Implement rapid response for reported mechanical issues to minimize service disruption.

7. **Enhance User Experience with Real-Time Updates**  
   - Provide live bike and dock availability in the app.  
   - Suggest alternative stations during peak hours.  
   - Enable users to **report damaged or malfunctioning bikes** in the app.
                

**Conclusion:** These recommendations integrate **seasonality, location, time-of-day patterns, and bike maintenance**. Implementing them will improve bike availability, reduce customer complaints, and support strategic growth for Citi Bike NYC.
""")

# Check exact column names
print(df.columns.tolist())

# Strip whitespace just in case
df.columns = df.columns.str.strip()