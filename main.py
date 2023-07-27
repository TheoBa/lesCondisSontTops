import folium as fl
from streamlit_folium import st_folium
import pandas as pd
import requests
from datetime import datetime, timedelta
import streamlit as st
import json
import plotly.express as px


st.set_page_config(page_title='Les Condis Sont Tops', page_icon=":surfer:", layout="wide")


def get_pos(lat, lng):
    return [str(lat), str(lng)]


def query_open_meteo(
        lat=str(46.6573), 
        lng=str(-1.9243), 
        fields="wind_wave_height,wind_wave_direction,swell_wave_height,swell_wave_direction,swell_wave_period", 
        startDate=datetime.now().strftime("%Y-%m-%d"), 
        endDate=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        ):
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lng}&hourly={fields}&start_date={startDate}&end_date={endDate}"
    response = requests.get(url=url)
    return response.text


def process_open_meteo(response):
    res = json.loads(response)
    res_df = pd.DataFrame(res["hourly"])
    res_df["time"] = res_df["time"].map(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:00"))
    return res_df


def build_figs(
        df,
        fields=["swell_wave_height",
                "swell_wave_direction",
                "swell_wave_period",
                "wind_wave_height", 
                "wind_wave_direction"]
        ):
    figs = {field: px.line(df, x="time", y=field) for field in fields}
    return figs


def display_current_condis(df):
    st.markdown("## Les condis actuelles:")
    st.markdown("### SWELL")
    st.markdown(f"Swell size (in m): {df.loc[0, 'swell_wave_height']}")
    st.markdown(f"Swell period (in s): {df.loc[0, 'swell_wave_period']}")
    st.markdown(f"Swell direction (in °): {df.loc[0, 'swell_wave_direction']}")
    st.markdown("### WIND")
    st.markdown(f"Wind waves size (in m): {df.loc[0, 'wind_wave_height']}")
    st.markdown(f"Wind direction (in °): {df.loc[0, 'wind_wave_direction']}")


def display_forcast_condis(figures):
    st.markdown("## Forecast des condis de la journée:")
    st.markdown("### SWELL")
    st.plotly_chart(figures['swell_wave_height'])
    st.plotly_chart(figures['swell_wave_period'])
    st.plotly_chart(figures['swell_wave_direction'])
    st.markdown("### WIND")
    st.plotly_chart(figures['wind_wave_height'])
    st.plotly_chart(figures['wind_wave_direction'])


st.markdown("# Les Condis Sont Tops")
col1, col2 = st.columns(2)
with col1:
    st.markdown("## Choisi ton spot de surf")
    m = fl.Map()
    m.add_child(fl.LatLngPopup())
    map = st_folium(m, height=350, width=700)
    data = None
    if map.get("last_clicked"):
        data = get_pos(map["last_clicked"]["lat"], map["last_clicked"]["lng"])

    if st.button(label='Les condis y-sont-elles tops ?'):
        with col2:
            if data is None:
                st.write("Please select a location")
            else:
                resp = query_open_meteo(lat=data[0], lng=data[1])
                resp_df = process_open_meteo(resp)
                figs = build_figs(resp_df)
                display_current_condis(resp_df)
                display_forcast_condis(figs)
