import json
import pandas as pd
import streamlit as st
from common import api

st.set_page_config(
    page_title="Superadmin Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

def theatreadmin_dashboard():
    theatre_id = st.session_state.get("theatre_id")
    if not theatre_id:
        st.switch_page("pages/app.py")
        st.stop()
        
    st.title("Theatre Name")
    st.subheader("Theatre City")
    st.divider()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    ok, data, _ = api(method="GET", path="/get_analytics_theatreadmin/total_movies")
    with col1:
        if ok:
            st.metric(label="Total Movies", value=data)
            
    ok, data, _ = api(method="GET", path="/get_analytics_theatreadmin/total_screens", params={"admin_id": theatre_id})
    with col2:
        if ok:
            st.metric(label="Total Screens", value=data)
            
    ok, data, _ = api(method="GET", path="/get_analytics_theatreadmin/total_shows", params={"admin_id": theatre_id})
    with col3:
        if ok:
            st.metric(label="Total Shows", value=data)
            
    ok, data, _ = api(method="GET", path="/get_analytics_theatreadmin/theatre_name", params={"admin_id": theatre_id})
    with col4:
        if ok:
            st.metric(label="Your Theatre", value=data)
            
    ok, data, _ = api(method="GET", path="/get_analytics_theatreadmin/city_name", params={"admin_id": theatre_id})
    with col5:
        if ok:
            st.metric(label="Your City", value=data)
            
    st.divider()
    
    table_col1, table_col2 = st.columns(2)
    
    ok_movies, movie_data, _ = api("GET", "/get_analytics/get_movies_list")
    with table_col1:
        if ok_movies:
            st.subheader("Movie List")
            df_movies = pd.DataFrame(movie_data if isinstance(movie_data, list) else [movie_data], columns=["Movie Name"])
            st.dataframe(df_movies, width="stretch")
            
    ok_cities, city_data, _ = api("GET", "/get_analytics_theatreadmin/get_cities_list")
    with table_col2:
        if ok_cities:
            st.subheader("City List")
            df_cities = pd.DataFrame(city_data if isinstance(city_data, list) else [city_data], columns=["City Name"])
            st.dataframe(df_cities, width="stretch")
            
    st.divider()
    
    
    
    ok_shows, show_data, _ = api("GET", "/get_analytics_theatreadmin/get_screen_shows_list", params={"admin_id": theatre_id})

    if ok_shows:
        st.subheader("Screens & Scheduled Movies")
        df_shows = pd.DataFrame(show_data if isinstance(show_data, list) else [show_data])
        df_shows = df_shows[["Screen Name", "Movie Title", "Language", "Duration"]]
        st.dataframe(df_shows, width="stretch")
    
    bottom_col1, bottom_col2 = st.columns(2)
    
    top_movies_ok, top_movies_data, _ = api("GET", "/get_analytics_theatreadmin/get_top_movies", params={"admin_id": theatre_id})
    
    with bottom_col1:
        st.subheader("Top Movies Revenue")
        if top_movies_ok and top_movies_data:
            df_chart = pd.DataFrame(top_movies_data)
            df_chart = df_chart.set_index("Category") 
            st.bar_chart(df_chart)
        else:
            empty_df = pd.DataFrame(columns=["Category", "Value"]).set_index("Category")
            st.bar_chart(empty_df)
            st.caption("No revenue data available for this theatre admin.")

    shows_sold_ok, shows_sold_data, _ = api("GET", "/get_analytics_theatreadmin/get_shows_sold", params={"admin_id": theatre_id})
    
    with bottom_col2:
        st.subheader("Shows Sold per Movie")
        if shows_sold_ok and shows_sold_data:
            df_shows_chart = pd.DataFrame(shows_sold_data)
            df_shows_chart = df_shows_chart.set_index("Category") 
            st.bar_chart(df_shows_chart)
        else:
            empty_df = pd.DataFrame(columns=["Category", "Value"]).set_index("Category")
            st.bar_chart(empty_df)
            st.caption("No shows analytics available for this theatre admin.")