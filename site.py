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




st.title("Vienna 2 Zurigo Route Viz tool")
with st.sidebar:
    stage_nr = st.radio("Which stage?", (1,2,3,4,5,6,7,8))
    url = fr"https://raw.githubusercontent.com/MannuelTe/RouteViz/main/stage_{stage_nr}.gpx" # Make sure the url is the raw version of the file on GitHub
    download = requests.get(url).content.decode("UTF-8")
    gpx  = gpxpy.parse(download)
##route Upload:


route_df = func.df_maker(gpx)

##compute elevations and distances
route_df['elevation_diff'] = route_df['elevation'].diff()
route_df = func.add_distances(route_df)
route_df[route_df['elevation_diff'] >= 0]['elevation_diff'].sum()
route_df['distance'].sum()
route_df['cum_elevation'] = route_df['elevation_diff'].cumsum()
route_df['cum_distance'] = route_df['distance'].cumsum()
route_df = route_df.fillna(0)

##compute gradients
route_df = func.Gradientcalc(route_df)
grad_df = func.Gradientinterval(route_df)

##show map
map = func.map_show(route_df)
st_folium(map)

##make elevation profile:
st.plotly_chart(func.elevationprof(route_df))

st.plotly_chart(func.Histmaker(grad_df))