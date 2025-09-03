# Citi Bike Data Analysis – NYC 2022

## Objective
As the lead analyst for a bike-sharing service in New York City, the goal of this project is to analyze user behavior and support the business strategy team in assessing the current logistics model for bike distribution. The project aims to uncover actionable insights that can help the company optimize bike availability, identify expansion opportunities, and maintain its position as a leader in eco-friendly transportation.

## Context
Citi Bike, launched in 2013, has become increasingly popular, especially during and after the Covid-19 pandemic, when residents sought alternative and sustainable transportation options. The rise in demand has resulted in distribution challenges, such as:

- Popular stations running out of bikes  
- Docking stations being full, preventing returns  
- Customer complaints and reduced satisfaction  

As lead analyst, the task is to diagnose the root causes of these distribution issues—whether due to sheer bike numbers, seasonal demand, or other factors—and provide actionable recommendations. Insights will be communicated to the business strategy team through an interactive dashboard showing key metrics.

## Data
- **Citi Bike trip dataset (2022)** – Public trip records including start/end stations, times, bike types, and membership status.  
- **Weather dataset** – Daily temperature and precipitation data gathered using NOAA’s API to understand the impact of weather on ridership patterns.

## Tools & Libraries
- **Python**  
- **Data manipulation**: Pandas  
- **Visualization**: Matplotlib, Seaborn, Plotly  
- **Mapping**: Kepler.gl  
- **Dashboard**: Streamlit  

## Analysis Steps
1. Filter trips to match the weather dataset dates (2022-01-01 to 2022-09-07).  
2. Clean and transform data, including renaming columns and handling missing values.  
3. Calculate daily trip counts and merge with weather data.  
4. Visualize trends using dual-axis line charts for bike trips and temperature.  
5. Build interactive maps to show popular routes and high-demand stations.  
6. Develop a Streamlit dashboard to present insights to non-analysts and support strategic decision-making.