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

stage_l = [None]*8
stage_l[0] = "Wien - Mariazell"
stage_l[1] = "Mariazell - Liezen"
stage_l[2] = "Liezen - Salzburg"
stage_l[3] = "Salzburg - Kufstein"
stage_l[4] = "Kufstein - Innsbruck"
stage_l[5] = "Innsbruck - Meran"
stage_l[6] = "Meran - Davos"
stage_l[7] = "Davos - Zürich"


stage_d = [None]*8
stage_d[0] = "The first stage gently introduces us to the Austrian alps, leading out of Vienna and through a plethora of small hills to the historic (?) town of Mariazell. We follow the so called Traisentalradweg on the last couple of ks. "
stage_d[1] = "The second stage leaves in Mariazell and features a long descent into a national park before Arriving into Liezen. Some of the stage follows the so called 'Ybbistalradweg' and the 'Mendlingtalrunde'. "
stage_d[2] = "Leaving Liezen, we cross a plateau in order to get to Bad Ischgl where we take on a mountainn pass to drop into Salzburg."
stage_d[3] = "We climb into Germany after taking some backcountry roads and finally gettin back into Austria to overnight in Kufstein."
stage_d[4] = "We again climb into Germany whereafter we turn south in order to drop into the Innsbruck vally where we pernoctate."
stage_d[5] = "Leaving Innsbruck, two HUGE increasingly harder passes await us, a long descent brings us into the Tirol Valley"
stage_d[6] = "From the Tirol, we climb Stelvio, the obvious Cima Coppi, cross Zernez and make our way into Davos."
stage_d[7] = "The last stage sees us leave Davos and descent along the Rhine before Climbing onto the Toggenburg Valley from where we reach Zurich. "



st.set_page_config(
    page_title="Vienna - Zhr Route Viz",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'https://www.strava.com/athletes/18473240',
        'Report a bug': "https://www.extremelycoolapp.com/bug",

    }
)


with st.sidebar:
    stage_name = st.radio("Select the Stage", stage_l)
    stage_nr = stage_l.index(stage_name)+1
    url = fr"https://raw.githubusercontent.com/MannuelTe/RouteViz/main/stage_{stage_nr}.gpx" # Make sure the url is the raw version of the file on GitHub
    download = requests.get(url).content.decode("UTF-8")
    gpx  = gpxpy.parse(download)
my_bar = st.progress(0)

st.subheader("Vienna - Zurich Route")
st.title(f"Stage {stage_nr}: {stage_name}")


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
    st.subheader("Some info")
    st.write(stage_d[stage_nr-1])
    st.subheader("Key Facts")
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
