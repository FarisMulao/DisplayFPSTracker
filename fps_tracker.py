

import time
import csv
import mss
import pygetwindow as gw
from datetime import datetime
import argparse

OUTPUT_CSV_FILE = 'fps_log.csv'  # Name of the output file


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


def run_tracker(duration, delay, output_file):
    """
    Main function to run the FPS tracker.

    Args:
        duration (str or int): The duration in seconds for which to run the tracker, or 'infinite'.
        delay (int): The delay in seconds before starting the tracker.
        output_file (str): The path to the CSV file where results are saved.
    """
    if delay > 0:
        print(f"Waiting for {delay} seconds before starting...")
        time.sleep(delay)

    duration_text = "indefinitely" if duration == 'infinite' else f"for {duration} seconds"
    print("--- NVIDIA Performance Engineering Simulation: FPS Tracker ---")
    print(f"Starting FPS and Active Window tracking {duration_text}.")
    print(f"Data will be saved to: {output_file}")
    print("Press Ctrl+C to stop.")
    print("-" * 60)

    # Prepare the CSV file and write the header
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'fps', 'active_window'])

    start_time = time.time()
    frame_count = 0
    last_log_time = start_time
    total_frames_captured = 0

    try:
        with mss.mss() as sct:
            monitor = {"top": 0, "left": 0, "width": 1, "height": 1}

            while True:
                if duration != 'infinite' and time.time() - start_time >= duration:
                    break

                sct.grab(monitor)
                frame_count += 1
                total_frames_captured += 1
                current_time = time.time()

                if current_time - last_log_time >= 1.0:
                    elapsed_time = current_time - last_log_time
                    fps = frame_count / elapsed_time if elapsed_time > 0 else 0
                    active_window = get_active_window_title()
                    timestamp = datetime.now().isoformat()

                    with open(output_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, f"{fps:.2f}", active_window])

                    if duration != 'infinite':
                        print(
                            f"Time: {int(current_time - start_time)}s / {duration}s | Avg FPS (1s): {fps:<8.2f} | Active Window: {active_window}")
                    else:
                        print(
                            f"Time: {int(current_time - start_time)}s | Avg FPS (1s): {fps:<8.2f} | Active Window: {active_window}")

                    frame_count = 0
                    last_log_time = current_time

    except KeyboardInterrupt:
        print("\nTracker stopped by user.")
    finally:
        end_time = time.time()
        total_time = end_time - start_time
        avg_fps = total_frames_captured / total_time if total_time > 0 else 0
        print("-" * 60)
        print("Tracking finished.")
        print(f"Total duration: {total_time:.2f} seconds")
        print(f"Overall Average FPS: {avg_fps:.2f}")
        print(f"Log file '{output_file}' has been created.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tracks and logs display FPS and the active window title.")
    parser.add_argument('duration',
                        help="Duration to run the tracker in seconds, or '-infinite' to run indefinitely.")
    parser.add_argument('delay', nargs='?', type=int, default=0,
                        help="Delay in seconds before starting the tracker (optional).")

    args = parser.parse_args()

    # Validate and process duration
    if args.duration.lower() == '-infinite':
        run_duration = 'infinite'
    else:
        try:
            # Remove the leading '-' if it exists
            run_duration = int(args.duration.lstrip('-'))
        except ValueError:
            print("Error: Duration must be an integer (e.g., 60) or '-infinite'.")
            exit(1)

    run_tracker(run_duration, args.delay, OUTPUT_CSV_FILE)
