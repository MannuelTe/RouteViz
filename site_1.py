import streamlit as st
import pandas as pd
import numpy as np
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import folium
import leafmap.foliumap as leafmap
from IPython.display import display
import plotly.express as px
import plotly.graph_objects as go
import haversine as hs
from streamlit_folium import st_folium
import requests
import io

import func

stage_l = [None]*10
stage_l[0] = "Geneva -  Ambérieu"
stage_l[1] = "Ambérieu - Saint-Etienne"
stage_l[2] = "Saint-Etienne - Aubenas"
stage_l[3] = "Aubenas - Mende"
stage_l[4] = "Mende - Albi"
stage_l[5] = "Ablbi - Limoux"
stage_l[6] = "Limoux - Amdorra la V. "
stage_l[7] = "Andorra la V. - Campordon"
stage_l[8] = "Campordon - Sagaro"
stage_l[9] = "Overview"


stage_d = [None]*10
stage_d[0] = "Leaving Sitzerland we head west and end up just before Lyon. Potential hotel: ibis budget Ambérieu-en-Bugey Château-Gaillard"
stage_d[1] = "Placeholder Description."
stage_d[2] = "Moving on the edge of the Massiv Central and occasionally dropping into the lowlands."
stage_d[3] = "Placeholder"
stage_d[4] = "Placeholder Description."
stage_d[5] = "We cross the windy flats of the south of france with a hill in the middle."
stage_d[6] = "From the foothills we move south-west into the high Pyrenees and finish off roaring into Andorra la Vella. A hefty day of climbing"
stage_d[7] = "Leaving Andorra from the south we climb through el Parc del Cadi heading east for Ripoll and the mountain town of Campordon."
stage_d[8] = "A short detour into one of the most lost corners of france brings us back into spain from the north and where we cross the emporda basin and climb the last hill before arriving home."
stage_d[9] = "This is the actual overview"


st.set_page_config(
    layout="wide",
    page_title="Geneva-Sagaro",
    page_icon="🧊",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'https://www.strava.com/athletes/18473240',
        'Report a bug': "https://www.extremelycoolapp.com/bug",

    }
)


with st.sidebar:
    stage_name = st.radio("Select the Stage", stage_l)
    stage_nr = stage_l.index(stage_name)+1
    if stage_nr < 10: #downloads the stage in advance
        url = fr"https://raw.githubusercontent.com/MannuelTe/RouteViz/main/stage_{stage_nr}.gpx" # Make sure the url is the raw version of the file on GitHub
        download = requests.get(url).content.decode("UTF-8")
        gpx  = gpxpy.parse(download)
        

st.subheader("Vienna - Zurich Route")
if stage_nr < 10:
    my_bar = st.progress(0)
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
    
    st.title("Map")
    #col11, col22 = st.columns([1,1])
#    options = list(leafmap.basemaps.keys())
#    index = options.index("CyclOSM")
#    with col11:
#        basemap = st.selectbox("Select a basemap:", options, index)
#    with col22:
#        coolr = st.color_picker('Pick A Color', '#00f900')
#        st.write('The current color is', coolr)
#    m = func.improvedmap(route_df, coolr, options, index, basemap)
    
#    m.to_streamlit(height=900)


    map = func.map_show(route_df)
    my_bar.progress(60)
    st_folium(map, width=1250)

    ##make elevation profile:
    st.plotly_chart(func.elevationprof(route_df))
    my_bar.progress(80)
    st.plotly_chart(func.Histmaker(grad_df))
    my_bar.progress(100)
    ##########################
    
        
else:
    my_bar = st.progress(0)
    distancelist = []
    elevlist= []
    peaklist = []
    for i in range(0,9):
        my_bar.progress((i+1)*8)
        if i == 0:
            stage_nr = 1
            url = fr"https://raw.githubusercontent.com/MannuelTe/RouteViz/main/stage_{stage_nr}.gpx" # Make sure the url is the raw version of the file on GitHub
            download = requests.get(url).content.decode("UTF-8")
            gpx  = gpxpy.parse(download)
            stage_df= func.df_maker(gpx)
            base_df = stage_df
        else:
            stage_nr = i +1     
            url = fr"https://raw.githubusercontent.com/MannuelTe/RouteViz/main/stage_{stage_nr}.gpx" # Make sure the url is the raw version of the file on GitHub
            download = requests.get(url).content.decode("UTF-8")
            gpx  = gpxpy.parse(download)
            stage_df = func.df_maker(gpx)
            #base_df = base_df.append(stage_df)  
            base_df = pd.concat([base_df, stage_df], ignore_index=True)

        stage_df = func.add_distances(stage_df)
        stage_df['elevation_diff'] = stage_df['elevation'].diff()    
        stage_df[stage_df['elevation_diff'] >= 0]['elevation_diff'].sum()
        stage_df['distance'].sum()
        stage_df['cum_elevation'] = stage_df['elevation_diff'].cumsum()
        stage_df['cum_distance'] = stage_df['distance'].cumsum()
        distancelist.append((stage_df.cum_distance.max()/1000).round(2))
        elevlist.append( int(stage_df[stage_df['elevation_diff'] > 0]['elevation_diff'].sum().round()) )
        peaklist.append([ int(stage_df.elevation.max().round(0)), int(stage_df.elevation.min().round(0)) ])
        #print(stage_df.head())
    base_df['elevation_diff'] = base_df['elevation'].diff()
    my_bar.progress(85)
    base_df = func.add_distances(base_df)
    my_bar.progress(90)
    base_df[base_df['elevation_diff'] >= 0]['elevation_diff'].sum()
    base_df['distance'].sum()
    base_df['cum_elevation'] = base_df['elevation_diff'].cumsum()
    base_df['cum_distance'] = base_df['distance'].cumsum()
    base_df = base_df.fillna(0)
    with st.container():
        st.subheader("Some info")
        st.write(stage_d[stage_nr])
        st.subheader("Key Facts")
        col1, col2, col3 = st.columns(3)
        col1.metric("Distance", f"{(base_df.cum_distance.max()/1000).round(2)} km", )
        col2.metric("Elevation gain", f"{int(base_df[base_df['elevation_diff'] > 0]['elevation_diff'].sum().round())} m", f"Loss: {int(base_df[base_df['elevation_diff'] < 0]['elevation_diff'].sum().round())}", delta_color="inverse")
        col3.metric("Highest point", f"{int(base_df.elevation.max().round(0))} m", f"Lowest: {int(base_df.elevation.min().round(0))} m", delta_color="inverse")
        
    my_bar.progress(92)
    mapp = func.map_show(base_df)
    my_bar.progress(94)
    st_folium(mapp,  width=1250)
    
    #my_bar.progress(96)
    #base_df = func.Gradientcalc(base_df)
    #st.plotly_chart(func.elevationprof(base_df))
    my_bar.progress(100)
    st.subheader("Stages (colour) by elevation gain (y-axis), distance (x-axis) and highest point (sizes)")
    #st.write(distancelist)
    #st.write(elevlist)
    #st.write(peaklist)
    stagelist = [f"stage {i+1}" for i in range(0,9)]
    fig_scat = px.scatter(x= distancelist, y= elevlist, size= [i[0] for i  in peaklist],color=stagelist)
    st.plotly_chart(fig_scat)
