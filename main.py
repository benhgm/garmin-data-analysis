import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os
from fitparse import FitFile
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64

from utils import load_data, extract_race_segment

st.set_page_config(page_title="Canoe Sprint Training Analysis", layout="wide")

def main():
    st.title("Canoe Sprint Training Analysis")
    st.write("Upload one or more .fit files from your GPS fitness device to analyze your activities.")
    
    # File uploader
    uploaded_files = st.file_uploader("Choose FIT files", type="fit", accept_multiple_files=True)
    
    if uploaded_files:
        # Display a select box for file selection if multiple files are uploaded
        dfs = [(f.name, load_data(f)) for f in uploaded_files]
        st.subheader(f"Analyzing races")
        
        # Process the selected file
        race_segments = [(name, extract_race_segment(df)) for name, df in dfs]
        
        fig1 = go.Figure()

        for name, df in race_segments:
            fig1.add_trace(go.Scatter(
                x=df["distance_relative"],
                y=df["speed"],
                mode="lines",
                name=name
            ))

        fig1.update_layout(
            title="Speed vs Distance",
            xaxis_title="Distance (m)",
            yaxis_title="Speed (km/h)",
            template="plotly_white"
        )

        st.plotly_chart(fig1, use_container_width=True)

        fig2 = go.Figure()

        for name, df in race_segments:
            fig2.add_trace(go.Scatter(
                x=df["time_seconds_relative"],
                y=df["distance_relative"],
                mode="lines",
                name=name
            ))

        fig2.update_layout(
            title="Distance vs Time",
            xaxis_title="Time (s)",
            yaxis_title="Distance (m)",
            template="plotly_white"
        )

        st.plotly_chart(fig2, use_container_width=True)

        fig3 = go.Figure()

        for name, df in race_segments:
            fig3.add_trace(go.Scatter(
                x=df["time_seconds_relative"],
                y=df["speed"],
                mode="lines",
                name=name
            ))

        fig3.update_layout(
            title="Speed vs Time",
            xaxis_title="Time (s)",
            yaxis_title="Speed (km/h)",
            template="plotly_white"
        )

        st.plotly_chart(fig3, use_container_width=True)


            
            

if __name__ == "__main__":
    main()