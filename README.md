# Profiler_Plotter

A ready-to-use Python script for generating depth and gradient profile charts from offshore route surveys, typical in oil&gas, offshore wind and renewable energy projects.

The script plots charts of Kilometer-Point (KP) vs depth, along with the changes in gradient (slope) along the depth profile. The charts are exported as PNG files.

## How to use

- **Install python** (version 3 minimum required)
Simply download and install from https://www.python.org/downloads/
Ensure to check on "Add Python to environment variables" during installation.
If you already have Python installed, then just skip this step.
	
- **Run the profile_plotter.py file**
Double-click on the file to run.

The script implements a Tkinter dialog box that requests user to select an input file containing the KP and depth data. This should be a CSV or TXT input file, containing just the 2 columns of data, with no headers (KP data in `column_0` and depth data in `column_1`.

Two (2) charts are produced. The first chart plots the depth profile and the gradients seperately, while the second plots both on the same chart.

The charts are exported as PNG files using the original input file with "_plot1" or "_plot2" as file names.
