

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
from pathlib import Path

# --- Configuration ---
ANOMALY_THRESHOLD_Z_SCORE = 3.0 # Z-score to identify a data point as an anomaly

def find_timestamp_column(df):
    """Finds the first column in the DataFrame that likely represents a timestamp."""
    for col in df.columns:
        if 'time' in col.lower():
            print(f"Timestamp column detected: '{col}'")
            return col
    print("Warning: No timestamp column found. Using DataFrame index instead.")
    return None

def find_numeric_columns(df, time_col):
    """Finds all numeric columns, excluding the timestamp column."""
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if time_col in numeric_cols:
        numeric_cols.remove(time_col)
    print(f"Numeric data columns detected: {numeric_cols}")
    return numeric_cols

def detect_anomalies(df, numeric_col, threshold):
    """Detects anomalies in a series using the Z-score method."""
    series = df[numeric_col]
    mean = series.mean()
    std = series.std()
    
    # Handle cases with zero standard deviation
    if std == 0:
        return pd.Series([False] * len(df), index=df.index)
        
    z_scores = (series - mean) / std
    anomalies = np.abs(z_scores) > threshold
    print(f"Found {anomalies.sum()} anomalies in '{numeric_col}' (Z-score > {threshold})")
    return anomalies

def create_and_save_plots(df, time_col, numeric_cols, output_dir):
    """
    Generates and saves plots for each numeric column against the timestamp column,
    highlighting any detected anomalies.
    """
    print(f"\nGenerating plots and saving to: '{output_dir}'")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for col in numeric_cols:
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(15, 7))

        # Main line plot
        sns.lineplot(data=df, x=time_col, y=col, ax=ax, label=f'{col} Over Time', color='#1f77b4')

        # Highlight anomalies
        anomalies = detect_anomalies(df, col, ANOMALY_THRESHOLD_Z_SCORE)
        if anomalies.any():
            ax.scatter(
                df.index[anomalies],
                df[col][anomalies],
                color='#ff7f0e', 
                s=100, 
                label=f'Anomaly (Z > {ANOMALY_THRESHOLD_Z_SCORE})',
                zorder=5
            )

        # Formatting
        ax.set_title(f'Performance Analysis: {col} vs. Time', fontsize=16, weight='bold')
        ax.set_xlabel(f'Timestamp ({time_col})', fontsize=12)
        ax.set_ylabel(col, fontsize=12)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # Save the plot
        output_path = os.path.join(output_dir, f"plot_{col}.png")
        plt.savefig(output_path, dpi=150)
        plt.close(fig)
        print(f" -> Saved plot: '{output_path}'")

def main(csv_path, output_dir):
    """
    Main function to load, process, and plot data from a CSV file.
    """
    print("--- NVIDIA Performance Engineering Simulation: CSV Plotter ---")
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at '{csv_path}'")
        return

    print(f"Loading data from: '{csv_path}'")
    # Attempt to load CSV with common delimiters
    try:
        df = pd.read_csv(csv_path, sep=',')
    except pd.errors.ParserError:
        try:
            df = pd.read_csv(csv_path, sep=';')
        except Exception as e:
            print(f"Error: Could not parse CSV file. Please check format. Details: {e}")
            return

    # --- Column Detection ---
    time_col = find_timestamp_column(df)
    numeric_cols = find_numeric_columns(df, time_col)

    if not numeric_cols:
        print("Error: No numeric data columns found to plot.")
        return

    # --- Data Conversion ---
    if time_col:
        # Convert timestamp column to datetime objects for proper plotting
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        # Drop rows where timestamp conversion failed
        df.dropna(subset=[time_col], inplace=True)
        df.set_index(time_col, inplace=True)
    else:
        # If no time column, use the integer index for the x-axis
        df.reset_index(inplace=True)
        time_col = 'index'

    # --- Plotting and Anomaly Detection ---
    create_and_save_plots(df, time_col, numeric_cols, output_dir)
    print("\nProcessing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load a CSV file, plot numeric data, and detect anomalies.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'csv_path',
        type=str,
        help='Path to the input CSV file (e.g., fps_log.csv)'
    )
    parser.add_argument(
        '--output_dir', 
        type=str, 
        default='plots', 
        help='Directory to save the output plots (default: ./plots)'
    )
    args = parser.parse_args()
    main(args.csv_path, args.output_dir)

