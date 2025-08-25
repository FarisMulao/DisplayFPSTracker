# Display FPS Tracker and Plotter

## Setup and Installation

1.  **Clone the repository (or download the files):**

    ```bash
    git clone https://github.com/FarisMulao/DisplayFPSTracker.git
    cd DisplayFPSTracker
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## How to Use

### Part 1: Tracking FPS

1.  Open your terminal or command prompt and navigate to the project directory.
2.  Run the tracker script with a specified duration. For example, to run it for 120 seconds:
    ```bash
    python fps_tracker.py -120
    ```
3.  To run the tracker for 60 seconds with a 5-second delay before starting:
    ```bash
    python fps_tracker.py -60 -5
    ```
4.  To run the tracker indefinitely until you manually stop it (with Ctrl+C):
    ```bash
    python fps_tracker.py -infinite
    ```
5.  The script will log FPS and active window data to `fps_log.csv`. While it's running, use your computer or play a game as you normally would.

### Part 2: Plotting Results

1.  After the tracker has generated the `fps_log.csv` file, run the plotter script from the same terminal, providing the path to the CSV file as an argument:
    ```bash
    python csv_plotter.py fps_log.csv
    ```
2.  The script will analyze the data, generate a plot for each numeric column, and save them as `.png` images inside a new `plots/` directory.

---

When you use this tool, you might notice that the measured FPS is capped at your monitor's refresh rate (e.g., 60, 144, or 240 Hz). This is expected.

- **Display FPS (What this tool measures):** This is the rate at which frames are actually shown on your monitor. It's a measure of the final visual output and is critical for understanding user-facing issues like stutter.
- **Render FPS (What tools like NVIDIA Overlay measure):** This is the raw number of frames your GPU produces, regardless of whether they are ever displayed. It's a measure of maximum hardware throughput.

This tool correctly measures **Display FPS**, which is a vital metric for analyzing the smoothness of the end-user experience.
