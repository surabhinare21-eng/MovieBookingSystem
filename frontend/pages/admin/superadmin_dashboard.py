import json
import pandas as pd
import streamlit as st
from common import api

st.set_page_config(
    page_title="Superadmin Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


def superadmin_dashboard():
    st.title("SuperAdmin Dashboard")

    ok, data, _ = api("GET", "/get_analytics/superadmin")
    if not ok:
        return st.error(
            f"Failed to load dashboard metrics. Backend response: {data}"
        )

    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.metric(
            label="Total Customers", value=data.get("total_customers_count", 0)
        )
    with m_col2:
        st.metric(
            label="Total Theatre Admins",
            value=data.get("total_theatre_admin_count", 0),
        )
    with m_col3:
        st.metric(
            label="Total theatres", value=data.get("total_theatre_count", 0)
        )
    with m_col4:
        st.metric(label="Total Cities", value=data.get("total_cities", 0))
    with m_col5:
        st.metric(label="Total Movies", value=data.get("total_movies", 0))

    st.markdown("---")

    ok, map_data, _ = api("GET", "/get_analytics/map_data")
    if isinstance(map_data, str):
        try:
            map_data = json.loads(map_data)
        except json.JSONDecodeError:
            map_data = None

    st.subheader("Geographic Theatre Distribution")
    if ok and isinstance(map_data, list) and len(map_data) > 0:
        city_data = pd.DataFrame(map_data)
        if "latitude" in city_data.columns and "longitude" in city_data.columns:
            city_data = city_data.dropna(subset=["latitude", "longitude"])
            if "city_name" in city_data.columns:
                city_data = city_data.rename(columns={"city_name": "name"})
            st.map(city_data)
        else:
            st.warning(
                "Map coordinates columns ('latitude', 'longitude') missing in data layout."
            )
    else:
        st.info("No active theatre geographic coordinate data found.")

    st.markdown("---")

    m_left_col, m_right_col = st.columns(2)

    with m_left_col:
        st.subheader("theatres vs City Distribution")
        view_mode_city = st.radio(
            "Select Chart View (City)",
            ["Bar Chart", "Heatmap"],
            horizontal=True,
            key="view_mode_city",
        )

        ok_city, data_city, _ = api("GET", "/get_analytics/graphical_theatre_city")
        if ok_city and isinstance(data_city, dict) and data_city:
            df_city = pd.DataFrame(
                {
                    "City": list(data_city.keys()),
                    "Total Theatres": list(data_city.values()),
                }
            )

            if view_mode_city == "Bar Chart":
                st.bar_chart(
                    data=df_city,
                    x="City",
                    y="Total Theatres",
                    color="City",
                    width="stretch",
                    height=280,
                )
            else:
                st.vega_lite_chart(
                    df_city,
                    {
                        "mark": {"type": "rect", "tooltip": True},
                        "encoding": {
                            "x": {"field": "City", "type": "nominal"},
                            "color": {
                                "field": "Total Theatres",
                                "type": "quantitative",
                                "scale": {"scheme": "viridis"},
                            },
                        },
                        "config": {"view": {"stroke": "transparent"}},
                    },
                    width="stretch",
                    height=280,
                )
        else:
            st.info("No city graphical theatre metrics logs available.")

    with m_right_col:
        st.subheader("Screens vs Theatre Distribution")
        view_mode_screen = st.radio(
            "Select Chart View (Screens)",
            ["Bar Chart", "Heatmap"],
            horizontal=True,
            key="view_mode_screen",
        )

        ok_scr, data_screen, _ = api(
            "GET", "/get_analytics/graphical_screen_theatre"
        )
        if ok_scr and isinstance(data_screen, dict) and data_screen:
            df_screen = pd.DataFrame(
                {
                    "Theatre Name": list(data_screen.keys()),
                    "Total Screens": list(data_screen.values()),
                }
            )

            if view_mode_screen == "Bar Chart":
                st.bar_chart(
                    data=df_screen,
                    x="Theatre Name",
                    y="Total Screens",
                    color="Theatre Name",
                    width="stretch",
                    height=280,
                )
            else:
                st.vega_lite_chart(
                    df_screen,
                    {
                        "mark": {"type": "rect", "tooltip": True},
                        "encoding": {
                            "x": {"field": "Theatre Name", "type": "nominal"},
                            "color": {
                                "field": "Total Screens",
                                "type": "quantitative",
                                "scale": {"scheme": "magma"},
                            },
                        },
                        "config": {"view": {"stroke": "transparent"}},
                    },
                    width="stretch",
                    height=280,
                )
        else:
            st.info("No interactive screen metrics data available.")

    st.markdown("---")

    # 4. Data Tables Section Below The Graphs
    t_left_col, t_right_col = st.columns(2)

    with t_left_col:
        st.subheader("All theatres")
        ok_t_list, theatre_list, _ = api("GET", "/get_analytics/get_theatre_list")
        if ok_t_list and isinstance(theatre_list, list):
            st.dataframe(
                pd.DataFrame(theatre_list, columns=["Theatre Names"]),
                width="stretch",
                height=300,
            )
        else:
            st.info("No theatre name registry details available.")

    with t_right_col:
        st.subheader("All Movies")
        ok_m_list, movies_list, _ = api("GET", "/get_analytics/get_movies_list")
        if ok_m_list and isinstance(movies_list, list):
            st.dataframe(
                pd.DataFrame(movies_list, columns=["Movies Names"]),
                width="stretch",
                height=300,
            )
        else:
            st.info("No movie record inventory details available.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Theatre Admins")
        ok_a, data_admin, _ = api("GET", "/get_analytics/theatre_admin_list")
        if ok_a and isinstance(data_admin, list):
            admin_df = pd.DataFrame(data=data_admin)
            if admin_df.empty:
                admin_df = pd.DataFrame(columns=["admin_name", "email", "phone_no"])
            st.dataframe(
                admin_df,
                width="stretch",
                column_config={
                    "admin_name": "Username",
                    "email": "Email",
                    "phone_no": "Phone Number",
                },
            )
        else:
            st.error("Failed to fetch theatre admin registry records.")

    with col2:
        st.subheader("Customers")
        ok_c, data_cust, _ = api("GET", "/get_analytics/get_customer_list")
        if ok_c and isinstance(data_cust, list):
            customer_df = pd.DataFrame(data=data_cust)
            if customer_df.empty:
                customer_df = pd.DataFrame(columns=["cust_name", "email", "phone_no"])
            st.dataframe(
                customer_df,
                width="stretch",
                column_config={
                    "cust_name": "Username",
                    "email": "Email",
                    "phone_no": "Phone Number",
                },
            )
        else:
            st.error("Failed to fetch customer profile records.")

    st.markdown("---")

    st.subheader("User Registrations Overview")
    ok_l, line_data, _ = api("GET", "/get_analytics/get_para_line_graph")
    if ok_l and isinstance(line_data, list):
        df_line = pd.DataFrame(data=line_data)
        if not df_line.empty and "date" in df_line.columns:
            df_line = df_line.sort_values(by="date")
            st.line_chart(
                data=df_line,
                x="date",
                y=["Admins", "Customers"],
                height=280,
                width="stretch",
            )
        else:
            st.info("No registration or timeline data history records present.")
    else:
        st.error("Failed to fetch timeline line graph metrics from backend.")


