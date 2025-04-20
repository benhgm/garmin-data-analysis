import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt

from fitparse import FitFile
from scipy.signal import find_peaks

def load_data(file):
    # Create a temporary file to save the uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.fit') as temp_file:
        temp_file.write(file.getbuffer())
        file_path = temp_file.name
        
    # Load the .FIT file
    fitfile = FitFile(file_path)

    # Prepare lists for data
    full_data = []

    # Extract data from "record" messages
    for record in fitfile.get_messages("record"):
        data = {d.name: d.value for d in record}
        speed = data.get("speed")
        full_data.append(data)

    df = pd.DataFrame(full_data)

    # Get the reference start time
    start_time = df["timestamp"].iloc[0]

    # Apply to compute seconds since start
    df["time_seconds"] = df["timestamp"].apply(lambda x: (x - start_time).total_seconds())
    df['pace'] = df['enhanced_speed'].apply(lambda x: 1000 / (x * 60) if x > 0 else 0.0)
    df['speed'] = df['enhanced_speed'].apply(lambda x: x * 3.6)

    return df

def extract_race_segment(df):
    """
    Function for extracting race segments from speed data.

    Returns:
    - race_segment_df: DataFrame containing the race segment (all columns), or
    - None if no high-speed segment is found
    """
    # Set thresholds
    high_speed_thresh = df['speed'].quantile(0.9)
    low_speed_thresh = df['speed'].quantile(0.1)  # Define what "not moving" means (can tweak this)

    # Mask for high speed
    mask = df['speed'] > high_speed_thresh
    if not mask.any():
        return None  # No high-speed data at all

    group_ids = (mask != mask.shift()).cumsum()
    df = df.copy()
    df['group'] = group_ids
    df['above'] = mask

    # Group segments and check if any exist
    segments = df[df['above']].groupby('group')
    if segments.ngroups == 0:
        return None

    # Find longest high-speed segment
    longest_segment = max(segments, key=lambda x: len(x[1]))[1]

    # Get index range of the high-speed segment
    start_idx = longest_segment.index[0]
    end_idx = longest_segment.index[-1]

    # Extend backward to race start
    while start_idx > 0 and df.loc[start_idx - 1, 'speed'] > low_speed_thresh:
        start_idx -= 1

    # Extend forward to race end
    while end_idx < len(df) - 1 and df.loc[end_idx + 1, 'speed'] > low_speed_thresh:
        end_idx += 1

    # Extract full race segment
    race_segment_df = df.loc[start_idx:end_idx].reset_index(drop=True)
    
    # Add relative time column (starting from zero)
    race_segment_df['time_seconds_relative'] = race_segment_df['time_seconds'] - race_segment_df['time_seconds'].iloc[0]
    race_segment_df['distance_relative'] = race_segment_df['distance'] - race_segment_df['distance'].iloc[0]

    if race_segment_df['distance_relative'].iloc[-1] <= 500:
        return race_segment_df[race_segment_df['distance_relative'] <= 200]
    elif race_segment_df['distance_relative'].iloc[-1] <= 1000:
        return race_segment_df[race_segment_df['distance_relative'] <= 500]
    elif race_segment_df['distance_relative'].iloc[-1] <= 1500:
        return race_segment_df[race_segment_df['distance_relative'] <= 1000]
    elif race_segment_df['distance_relative'].iloc[-1] <= 2500:
        return race_segment_df[race_segment_df['distance_relative'] <= 2000]

    # return race_segment_df