# profile_plotter.py - 2024.09.01
# (c) Kingsley Ezenwaka (kezenwaka@gmail.com)

from numpy import array, degrees, arctan
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator as mloc

        
def get_data():
    # Tkinter GUI to set dialogbox always on top
    root = tk.Tk()
    root.wm_attributes('-topmost', 1)
    root.withdraw()   # supress the tk window

    # Select file dialog
    filepath = filedialog.askopenfilename(parent=root,
                                  initialdir="",
                                  title="Select A File",
                                  filetypes = (("Text files", "*.txt"),
                                               ("CSV files", "*.csv"),
                                               ("All files", "*")))

    # Read the profile data into a dataframe
    df = pd.read_csv(filepath, names=['kp','depth'])

    # Compute the gradient and moving average
    df['kp_diff'] = df.kp - df.kp.shift(1)
    df['depth_diff'] = df.depth - df.depth.shift(1)
    df['grad'] = abs(degrees(arctan(df.depth_diff / df.kp_diff / 1000))) # absolute value of gradient in degrees
    df['mov30'] = array(movmean(df.grad.tolist(), 30)) # 30-points moving average

    return df, filepath

def plot1(df, fpath, diff, interval):
    # Create plots and axes
    fig,axs = plt.subplots(2, 1, figsize=[8,4])

    # Seabed Depth plot formatting
    axs[0].plot(df.kp,df.depth, linewidth= 1, color = 'c', label = "Seabed Depth")
    axs[0].set_title(f"Seabed Profile KP {df.kp.iloc[0]:.2f} - KP {df.kp.iloc[-1]:.2f}",pad=20)
    axs[0].set_ylabel("Seabed Depth", color = 'c')
    axs[0].grid(True,color= '#dfdfdf')
    axs[0].legend(loc = 'upper right')
    axs[0].set_ylim(df.depth.max()+10, df.depth.min()-10)
    axs[0].xaxis.set_major_formatter('{x:.1f}')
    axs[0].xaxis.set_major_locator(mloc(interval))

    # Seabed Gradient plot formatting
    axs[1].plot(df.kp, df.grad, linewidth= 1, color = 'r', label = "Seabed Gradient")
    axs[1].plot(df.kp, df.mov30, linewidth= 1, color ='k', label = "Moving Average (30)")
    axs[1].set_ylabel("Seabed Gradient", color = 'r')
    axs[1].legend(loc = 'upper right')
    axs[1].set_xlabel("Kilometer Post (KP)")
    axs[1].grid(True,color='#dfdfdf')
    axs[1].set_ylim(0,65)
    axs[1].xaxis.set_major_formatter('{x:.1f}')
    axs[1].xaxis.set_major_locator(mloc(interval))

    fig.savefig(f"{fpath[:-4]}_plot1.png")

def plot2(df, fpath, diff, interval):
    # Create plots and axes
    fig, ax1 = plt.subplots(figsize=[7,3])

    # Seabed Depth plot
    ax1.plot(df.kp,df.depth, linewidth= 1, color = '#0006b1', label = "Seabed Depth")
    ax1.set_title(f"Seabed Profile KP {df.kp.iloc[0]:.2f} - KP {df.kp.iloc[-1]:.2f}",pad=20)
    ax1.set_ylabel("Seabed Depth", color = '#0006b1')
    ax1.grid(True,color= '#dfdfdf')
    ax1.legend(loc = 'upper left')
    ax1.set_ylim(df.depth.max()+120, df.depth.min()-150)
    ax1.xaxis.set_major_formatter('{x:.1f}')
    ax1.xaxis.set_major_locator(mloc(interval))

    ax2 = ax1.twinx()  # instantiate a second axes

    # Seabed Gradient plot
    ax2.plot(df.kp, df.grad, linewidth= 1, color = 'r', label = "Seabed Gradient")
    ax2.plot(df.kp, df.mov30, linewidth= 1, color ='k', label = "Moving Average (30)")
    ax2.set_ylabel("Seabed Gradient", color = 'r', rotation=270)
    ax2.legend(loc = 'upper right')
    ax2.grid(True,color='#dfdfdf')
    ax2.set_xlabel("Kilometer Post (KP)")
    ax2.set_ylim(0,90)
    ax2.yaxis.set_label_coords(1.1,0.5)

    fig.tight_layout()
    fig.savefig(f"{fpath[:-4]}_plot2.png")

def calc(df):
    # Compute x-axis labels interval
    diff = df.kp.max() - df.kp.min() 
    interval = 0.2 if (diff <= 2.0) else 1.0 if (diff > 3) & (diff <= 15) else 2.0
    return diff, interval

# Moving average function
def movmean(alist,num):
    mlist = []
    for i in range(len(alist)):
        if i < num:
            mlist.append(None)
        else:
            mlist.append(round(sum(alist[i-num:i])/num, 2))
    return mlist

def main():
    data, fpath = get_data()

    diff, interval = calc(data)

    plot1(data, fpath, diff, interval)
    plot2(data, fpath, diff, interval)

if __name__ == "__main__":
    main()
