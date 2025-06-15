# Profile Plotter GUI Application
# This script loads survey profile data from a CSV, computes gradient and moving average,
# and allows the user to visualize and export plots via a Tkinter-based GUI.

import pandas as pd
import numpy as np
from tkinter import *
from tkinter import filedialog
from matplotlib.ticker import MultipleLocator as mloc
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotData:
    """Holds file path, data frame, calculated KP difference, and plot interval."""
    def __init__(self, fpath=None, dataf=None, difference=None, interval=1):
        self.fpath = fpath
        self.dataf = dataf
        self.difference = difference
        self.interval = interval

    def process(self):
        """Prompts user to select a file, loads and processes the data into a DataFrame."""
        try:
            filepath = filedialog.askopenfilename(
                initialdir="", title="Select A File",
                filetypes=(("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*"))
            )

            # Read KP and depth from file
            df = pd.read_csv(filepath, names=['kp', 'depth'])

            # Compute differences and gradient
            df['kp_diff'] = df.kp - df.kp.shift(1)
            df['depth_diff'] = df.depth - df.depth.shift(1)
            df['grad'] = abs(np.degrees(np.arctan(df.depth_diff / df.kp_diff / 1000)))

            # Compute 30-point moving average of gradient
            df['mov30'] = np.array(movmean(df.grad.tolist(), 30))

            diff, inter = calc(df)

            # Save results into instance
            self.fpath = filepath
            self.dataf = df
            self.difference = diff
            self.interval = inter

        except Exception as e:
            return

def calc(df):
    """Calculates the x-axis range and determines a suitable interval for plotting."""
    diff = df.kp.max() - df.kp.min()
    interval = 0.2 if (diff <= 2.0) else 1.0 if (diff > 3) & (diff <= 15) else 2.0
    return diff, interval

def movmean(alist, num):
    """Calculates a simple moving average over a fixed window."""
    mlist = []
    for i in range(len(alist)):
        if i < num:
            mlist.append(None)
        else:
            mlist.append(round(sum(alist[i - num:i]) / num, 2))
    return mlist

def build_plot(df, diff, interval):
    """Builds and returns a matplotlib Figure with two subplots: Depth and Gradient."""
    fig = Figure(figsize=[8, 4], dpi=100)
    axs = fig.subplots(2, 1)

    # --- Seabed Depth Plot ---
    axs[0].plot(df.kp, df.depth, linewidth=1, color='c', label="Seabed Depth")
    axs[0].set_title(f"Seabed Profile KP {df.kp.iloc[0]:.2f} - KP {df.kp.iloc[-1]:.2f}", pad=20)
    axs[0].set_ylabel("Seabed Depth", color='c')
    axs[0].grid(True, color='#dfdfdf')
    axs[0].legend(loc='upper right')
    axs[0].set_ylim(df.depth.max() + 10, df.depth.min() - 10)
    axs[0].xaxis.set_major_formatter('{x:.1f}')
    axs[0].xaxis.set_major_locator(mloc(interval))

    # --- Seabed Gradient Plot ---
    axs[1].plot(df.kp, df.grad, linewidth=1, color='r', label="Seabed Gradient")
    axs[1].plot(df.kp, df.mov30, linewidth=1, color='k', label="Moving Average (30)")
    axs[1].set_ylabel("Seabed Gradient (°)", color='r')
    axs[1].legend(loc='upper right')
    axs[1].set_xlabel("Kilometer Post (KP)")
    axs[1].grid(True, color='#dfdfdf')
    axs[1].set_ylim(0, 65)
    axs[1].xaxis.set_major_formatter('{x:.1f}')
    axs[1].xaxis.set_major_locator(mloc(interval))

    return fig

def plot_gui(plot_data):
    """Creates and launches the Tkinter GUI for file selection, plotting, and export."""
    root = Tk()
    root.title("Ezenwaka Profile Plotter")
    root.geometry('800x460')

    # --- File Open Row ---
    topframe = Frame(root)
    topframe.grid(column=0, row=0, sticky='w', padx=10, pady=10)

    read_btn = Button(topframe, text='Open File',
                      command=lambda: [controller(1, read_ent, plot_data),
                                       controller(2, inter_sbox, plot_data)])
    read_btn.grid(column=0, row=0, padx=(0, 10))

    read_ent = Entry(topframe, state='disabled', relief='sunken', width=80, borderwidth=1)
    read_ent.grid(column=1, row=0)

    # --- Plot Display Area ---
    canvas_frame = Frame(root, width=780, height=280, relief='sunken', borderwidth=1)
    canvas_frame.grid(column=0, row=1, padx=10, pady=10)

    # --- Bottom Controls ---
    bottomframe = Frame(root)
    bottomframe.grid(column=0, row=2, padx=50, pady=(5, 10))

    inter_lbl = Label(bottomframe, text='KP Plot Interval')
    inter_lbl.grid(column=0, row=0)

    inter_sbox = Spinbox(bottomframe, from_=1.0, to=100000.0, width=8)
    inter_sbox.grid(column=1, row=0)

    auto_interval = Button(bottomframe, text='Auto Interval',
                           command=lambda: controller(2, inter_sbox, plot_data))
    auto_interval.grid(column=2, row=0)

    view_plot = Button(bottomframe, text='View Profile Plot',
                       command=lambda: controller(3, inter_sbox, plot_data, canvas_frame))
    view_plot.grid(column=0, row=1, padx=10, pady=(20, 1))

    export_plot = Button(bottomframe, text='Export Profile Plot',
                         command=lambda: controller(4, inter_sbox, plot_data, canvas_frame))
    export_plot.grid(column=1, row=1, pady=(20, 1), sticky='e')

    root.mainloop()

def draw_fig(frame, figure):
    """Embeds a Matplotlib figure into a given Tkinter frame."""
    for wdg in frame.winfo_children():
        wdg.destroy()

    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Resize root window to fit content
    root = frame.winfo_toplevel()
    root.geometry('')

def save_fig(fig, filepath):
    """Opens a save dialog and writes the figure to disk."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialdir=filepath.rsplit('/', 1)[0],
        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"),
                   ("SVG Vector", "*.svg"), ("PDF Document", "*.pdf"),
                   ("All Files", "*.*")],
        title="Save Profile Plot")

    if file_path:
        fig.savefig(file_path)

def update_wdg(wdg, ww, ver):
    """Updates a widget (Entry or Spinbox) with a new value."""
    try:
        wdg.configure(state='normal')
        wdg.delete(0, 'end')
        wdg.insert('end', ww)
        if ver == 1:
            wdg.configure(state='disabled')
    except:
        if ver == 1:
            wdg.configure(state='disabled')
        return

def controller(ver, wdg, obj, tkframe=None):
    """Controls GUI-to-backend interaction using version flags."""
    if ver == 1:
        obj.process()
        update_wdg(wdg, obj.fpath, ver)

    elif ver == 2:
        update_wdg(wdg, obj.interval, ver)

    elif ver in (3, 4):
        if obj.dataf is not None and tkframe:
            try:
                inter = float(wdg.get())
            except Exception:
                inter = obj.interval

            fig = build_plot(obj.dataf, obj.difference, inter)

            if ver == 3:
                draw_fig(tkframe, fig)
            elif ver == 4:
                save_fig(fig, obj.fpath)

def main():
    """Launches the GUI application."""
    new_plot_data = PlotData()
    plot_gui(new_plot_data)

# Entry point
main()
