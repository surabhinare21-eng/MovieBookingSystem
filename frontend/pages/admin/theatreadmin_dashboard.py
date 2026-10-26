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
    
    ok, data, _ = api(method="GET", path="/get_analytics_superadmin/total_movies")
    with col1:
        if ok:
            st.metric(label="Total Movies", value=data)
            
    ok, data, _ = api(method="GET", path="/get_analytics_superadmin/total_screens", params={"admin_id": theatre_id})
    with col2:
        if ok:
            st.metric(label="Total Screens", value=data)
            
    ok, data, _ = api(method="GET", path="/get_analytics_superadmin/total_shows", params={"admin_id": theatre_id})
    with col3:
        if ok:
            st.metric(label="Total Shows", value=data)
            
    ok, data, _ = api(method="GET", path="/get_analytics_superadmin/theatre_name", params={"admin_id": theatre_id})
    with col4:
        if ok:
            st.metric(label="Your Theatre", value=data)
            
    ok, data, _ = api(method="GET", path="/get_analytics_superadmin/city_name", params={"admin_id": theatre_id})
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
            st.dataframe(df_movies, use_container_width=True)
            
    ok_cities, city_data, _ = api("GET", "/get_analytics_superadmin/get_cities_list")
    with table_col2:
        if ok_cities:
            st.subheader("City List")
            df_cities = pd.DataFrame(city_data if isinstance(city_data, list) else [city_data], columns=["City Name"])
            st.dataframe(df_cities, use_container_width=True)
            
    st.divider()
    
    ok_shows, show_data, _ = api("GET", "/get_analytics_superadmin/get_screen_shows_list", params={"admin_id": theatre_id})
    if ok_shows:
        st.subheader("Screens & Scheduled Movies")
        df_shows = pd.DataFrame(show_data if isinstance(show_data, list) else [show_data])
        
        df_shows = df_shows[["Screen Name", "Movie Title", "Language", "Duration"]]
        st.dataframe(df_shows, use_container_width=True)
