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

def df_maker ( gpx):
    route_info = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                route_info.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation
                })
    route_df = pd.DataFrame(route_info)
    return(route_df)

def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    distance = hs.haversine(
        point1=(lat1, lon1),
        point2=(lat2, lon2),
        unit=hs.Unit.METERS
    )
    return np.round(distance, 2)


def add_distances( route_df):
    haversine_distance(
        lat1=route_df.iloc[0]['latitude'],
        lon1=route_df.iloc[0]['longitude'],
        lat2=route_df.iloc[1]['latitude'],
        lon2=route_df.iloc[1]['longitude']
    )    
        
    distances = [np.nan]

    for i in range(len(route_df)):
        if i == 0:
            continue
        else:
            distances.append(haversine_distance(
                lat1=route_df.iloc[i - 1]['latitude'],
                lon1=route_df.iloc[i - 1]['longitude'],
                lat2=route_df.iloc[i]['latitude'],
                lon2=route_df.iloc[i]['longitude']
            ))
            
    route_df['distance'] = distances
    return(route_df)



def map_show(route_df):

    lat_center = route_df.iloc[0][0]
    lon_center = route_df.iloc[0][1]
    route_map = folium.Map(
        location=[lat_center, lon_center],
        zoom_start=11,
        tiles='OpenStreetMap',
        
    )

    coordinates = [tuple(x) for x in route_df[['latitude', 'longitude']].to_numpy()]
    folium.PolyLine(coordinates, weight=4).add_to(route_map)

    return(route_map)

def Gradientcalc(route_df):
    gradients = [np.nan]

    for ind, row in route_df.iterrows(): 
        if ind == 0:
            continue
            
        grade = (row['elevation_diff'] / row['distance']) * 100
        
        if grade > 30:
            gradients.append(np.nan)
        else:
            gradients.append(np.round(grade, 1))
            
    route_df['gradient'] = gradients
    return(route_df)

def Gradientinterval(route_df):
        
    bins = pd.IntervalIndex.from_tuples([
        (-30, -10),
        (-10, -5), 
        (-5, -3), 
        (-3, -1), 
        (-1, 0),
        (0, 1), 
        (1, 3), 
        (3, 5), 
        (5, 7), 
        (7, 10), 
        (10, 12), 
        (12, 15), 
        (15, 20)
    ], closed='left')

    route_df['gradient_range'] = pd.cut(route_df['gradient'], bins=bins)
    gradient_details = []

    # For each unique gradient range
    for gr_range in route_df['gradient_range'].unique():
        # Keep that subset only
        subset = route_df[route_df['gradient_range'] == gr_range]
        
        # Statistics
        total_distance = subset['distance'].sum()
        pct_of_total_ride = (subset['distance'].sum() / route_df['distance'].sum()) * 100
        elevation_gain = subset[subset['elevation_diff'] > 0]['elevation_diff'].sum()
        elevation_lost = subset[subset['elevation_diff'] < 0]['elevation_diff'].sum()
        
        # Save results
        gradient_details.append({
            'gradient_range': gr_range,
            'total_distance': np.round(total_distance, 2),
            'pct_of_total_ride': np.round(pct_of_total_ride, 2),
            'elevation_gain': np.round(elevation_gain, 2),
            'elevation_lost': np.round(np.abs(elevation_lost), 2)
        })
        
    gradient_details_df = pd.DataFrame(gradient_details).sort_values(by='gradient_range').reset_index(drop=True)
    return(gradient_details_df)


def Histmaker(gradient_details_df):     
    
    colors = [
        '#0d46a0', '#2f3e9e', '#2195f2', '#4fc2f7',
        '#a5d6a7', '#66bb6a', '#fff59d', '#ffee58',
        '#ffca28', '#ffa000', '#ff6f00', '#f4511e', '#bf360c' ]
        
    custom_text = [f'''<b>{gr}%</b> - {dst}km''' for gr, dst in zip(
        gradient_details_df['gradient_range'].astype('str'),
        gradient_details_df['total_distance'].apply(lambda x: round(x / 1000, 2))
    )]

    fig = go.Figure(
        data=[go.Bar(
            x=gradient_details_df['gradient_range'].astype(str),
            y=gradient_details_df['total_distance'].apply(lambda x: round(x / 1000, 2)),
            marker_color=colors,
            text=custom_text
        )],
        layout=go.Layout(
            bargap=0,
            title='Gradient profile of the stage',
            xaxis_title='Gradient range (%)',
            yaxis_title='Distance covered (km)',
            autosize=True,
            template='simple_white'
        )
    )
    return(fig)
    

def elevationprof(route_df):

# Create figure
    fig_elev_s = go.Figure()

    fig_elev_s.add_trace(
        go.Scatter(x=list(route_df.cum_distance), y=list(route_df.elevation),text=route_df.gradient,
                        hoverinfo="text",
                        line_shape='spline'))

    # Set title
    fig_elev_s.update_layout(
        title_text="Elevation profile"
    )

    # Add range slider
    fig_elev_s.update_layout(
        xaxis=dict(
            title = 'Distance in km', 
            rangeselector=dict(
                buttons=list([
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="linear"
        ),
        yaxis = dict(
            title = "Elevation"
        )
    )

    return(fig_elev_s)
    
