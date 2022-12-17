import streamlit as st
import pandas as pd
import numpy as np
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import folium
from IPython.display import display
import plotly.express as px
import plotly.graph_objects as go
import haversine as hs
from streamlit_folium import st_folium
import requests
import io

import func



my_bar = st.progress(0)
st.title("Vienna 2 Zurigo Route Viz tool")

with st.sidebar:
    stage_nr = st.radio("Select the Stage", (1,2,3,4,5,6,7,8))
    url = fr"https://raw.githubusercontent.com/MannuelTe/RouteViz/main/stage_{stage_nr}.gpx" # Make sure the url is the raw version of the file on GitHub
    download = requests.get(url).content.decode("UTF-8")
    gpx  = gpxpy.parse(download)

route_df = func.df_maker(gpx)
my_bar.progress(10)
##compute elevations and distances
route_df['elevation_diff'] = route_df['elevation'].diff()
route_df = func.add_distances(route_df)
my_bar.progress(20)
route_df[route_df['elevation_diff'] >= 0]['elevation_diff'].sum()
route_df['distance'].sum()
route_df['cum_elevation'] = route_df['elevation_diff'].cumsum()
route_df['cum_distance'] = route_df['distance'].cumsum()
route_df = route_df.fillna(0)

##compute gradients
route_df = func.Gradientcalc(route_df)
my_bar.progress(30)
grad_df = func.Gradientinterval(route_df)
my_bar.progress(40)


with st.container():
    st.subheader("Some info about each stage")
    st.text("info here, might have it in separate files each")
    st.subheader("Some so called KPIs")
    col1, col2, col3 = st.columns(3)
    col1.metric("Distance", f"{(route_df.cum_distance.max()/1000).round(2)} km", )
    col2.metric("Elevation gain", f"{int(route_df[route_df['elevation_diff'] > 0]['elevation_diff'].sum().round())} m", f"Loss: {int(route_df[route_df['elevation_diff'] < 0]['elevation_diff'].sum().round())}", delta_color="inverse")
    col3.metric("Highest point", f"{int(route_df.elevation.max().round(0))} m", f"Lowest: {int(route_df.elevation.min().round(0))} m", delta_color="inverse")



##show map
map = func.map_show(route_df)
my_bar.progress(60)
st_folium(map)

##make elevation profile:
st.plotly_chart(func.elevationprof(route_df))
my_bar.progress(80)
st.plotly_chart(func.Histmaker(grad_df))
my_bar.progress(100)


