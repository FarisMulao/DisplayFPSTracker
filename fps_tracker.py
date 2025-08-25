

import time
import csv
import mss
import numpy as np
import pygetwindow as gw
from datetime import datetime

# --- Configuration ---
RUN_DURATION_SECONDS = 60  # How long to run the tracker
OUTPUT_CSV_FILE = 'fps_log.csv' # Name of the output file

def get_active_window_title():
    """
    Gets the title of the currently active window.
    Returns 'N/A' if no active window is found or if it has no title.
    """
    try:
        active_window = gw.getActiveWindow()
        return active_window.title if active_window else 'N/A'
    except gw.PyGetWindowException:
        # Can happen on certain platforms or when no window is available
        return 'Desktop'

def run_tracker(duration_seconds, output_file):
    """
    Main function to run the FPS tracker.

    Args:
        duration_seconds (int): The duration in seconds for which to run the tracker.
        output_file (str): The path to the CSV file where results are saved.
    """
    print("--- NVIDIA Performance Engineering Simulation: FPS Tracker ---")
    print(f"Starting FPS and Active Window tracking for {duration_seconds} seconds.")
    print(f"Data will be saved to: {output_file}")
    print("Press Ctrl+C to stop early.")
    print("-" * 60)

    # Prepare the CSV file and write the header
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'fps', 'active_window'])

    start_time = time.time()
    # --- New variables for averaging logic ---
    frame_count = 0
    last_log_time = start_time
    total_frames_captured = 0

    try:
        with mss.mss() as sct:
            # Use a small, fast-to-capture region of the screen (1x1 pixel)
            # minimizes the performance impact of screen capture itself.
            monitor = {"top": 0, "left": 0, "width": 1, "height": 1}

            # loop to capture as fast as possible
            while time.time() - start_time < duration_seconds:
                sct.grab(monitor)
                frame_count += 1
                total_frames_captured += 1
                current_time = time.time()

                # --- Averaging and Logging Logic ---
                # Check if 1 second has passed since the last log
                if current_time - last_log_time >= 1.0:
                    # Calculate FPS over the last second
                    elapsed_time = current_time - last_log_time
                    fps = frame_count / elapsed_time if elapsed_time > 0 else 0
                    
                    active_window = get_active_window_title()
                    timestamp = datetime.now().isoformat()

                    # Log the averaged FPS to the CSV
                    with open(output_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, f"{fps:.2f}", active_window])
                    
                    # Print the averaged FPS to the console
                    print(f"Time: {int(current_time - start_time)}s | Avg FPS (1s): {fps:<8.2f} | Active Window: {active_window}")

                    # Reset the counter and timer for the next 1-second interval
                    frame_count = 0
                    last_log_time = current_time

    except KeyboardInterrupt:
        print("\nTracker stopped by user.")
    finally:
        end_time = time.time()
        total_time = end_time - start_time
        # The overall average FPS is now more accurate
        avg_fps = total_frames_captured / total_time if total_time > 0 else 0
        print("-" * 60)
        print("Tracking finished.")
        print(f"Total duration: {total_time:.2f} seconds")
        print(f"Overall Average FPS: {avg_fps:.2f}")
        print(f"Log file '{output_file}' has been created.")

if __name__ == "__main__":
    run_tracker(RUN_DURATION_SECONDS, OUTPUT_CSV_FILE)
