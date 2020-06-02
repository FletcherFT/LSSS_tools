from pathlib import Path
from echopype.convert import Convert
from echopype.model import EchoData
import argparse
from skimage import io
import numpy as np
import warnings
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script for parsing in Greenland 2019 survey .raw files.")
    parser.add_argument("data_dir", nargs="?", default=r".\data",
                        type=str, help="Location of the .raw files.")
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    data_files = data_dir.glob("*.raw")
    for file in data_files:
        if file.exists():
            nc_file = file.parent.joinpath(file.stem+".nc")
            tmp = Convert(str(file), model="EK80")
            tmp.raw2nc()
            # Read .nc file into an EchoData object and calibrate
            e_data = EchoData(tmp.nc_path)
            e_data.calibrate(save=False, mode="Sv")
            # Just the first file for now
            break
        else:
            warnings.warn("No such file: {}".format(str(file)))
    #del tmp
    # Data is indexed according to a range bin which isn't evenly spaced across each frequency
    # Interpolation must therefore be done according to the range variable
    R = np.linspace(1, 200, 4281)
    # Sv is stored in e_data.Sv
    Sv = e_data.Sv
    # Get the 38 kHz and 200 kHz data separately
    Sv38 = Sv.sel(frequency=38000).set_coords("ranges")
    Sv200 = Sv.sel(frequency=200000).set_coords("ranges")
    # Select the unique range values
    _, idx = np.unique(Sv38['ranges'], return_index=True)
    Sv38 = Sv38.isel(range_bin=idx)
    _, idx = np.unique(Sv200['ranges'], return_index=True)
    Sv200 = Sv200.isel(range_bin=idx)
    # Fill in the nan values and any infinite values with a very strong dB (0)
    Sv38 = Sv38.fillna(0)
    Sv38 = Sv38.where(Sv38 > -np.inf, 0)
    Sv200 = Sv200.fillna(0)
    Sv200 = Sv200.where(Sv200 > -np.inf, 0)
    # Zero the ranges
    Sv38['ranges'] = Sv38.ranges - 1.1
    Sv200['ranges'] = Sv200.ranges - 0.295
    # Interpolate along the ranges
    Sv38 = Sv38.swap_dims({"range_bin": "ranges"})
    Sv38 = Sv38.Sv.interp(ranges=R)
    Sv200 = Sv200.swap_dims({"range_bin": "ranges"})
    Sv200 = Sv200.Sv.interp(ranges=R)
    # Clip color ranges to [-75, -5] dB
    Sv38 = Sv38.where(Sv38 < -5, np.nan)
    Sv38 = Sv38.where(Sv38 > -75, np.nan)
    Sv200 = Sv200.where(Sv200 < -5, np.nan)
    Sv200 = Sv200.where(Sv200 > -75, np.nan)
    # Plot the echograms separately
    plt.figure()
    ax = Sv38.T.plot(cmap="jet")
    ax.axes.invert_yaxis()
    plt.figure()
    ax1 = Sv200.T.plot(cmap="jet")
    ax1.axes.invert_yaxis()
    # Plot as a combined normalized image.
    plt.figure()
    IMAGE = np.stack((Sv38.data, Sv200.data)).transpose((2, 1, 0))
    IMAGE[np.isnan(IMAGE)] = -75
    IMAGE = (IMAGE - IMAGE.min()) / (IMAGE.max() - IMAGE.min())
    IMAGE = np.concatenate((IMAGE, np.zeros((*IMAGE.shape[:2], 1))), axis=-1)
    io.imshow(IMAGE)

    # phase angle is stored in e_data.phang
    phang = e_data.phang
    # Get the 38 kHz and 200 kHz data separately
    phang38 = phang.sel(frequency=38000).set_coords("ranges")
    phang200 = phang.sel(frequency=200000).set_coords("ranges")
    # Select the unique range values
    _, idx = np.unique(phang38['ranges'], return_index=True)
    phang38 = phang38.isel(range_bin=idx)
    _, idx = np.unique(phang200['ranges'], return_index=True)
    phang200 = phang200.isel(range_bin=idx)
    # Fill in the nan values and any infinite values with a very strong dB (0)
    phang38 = phang38.fillna(0)
    phang38 = phang38.where(phang38 > -np.inf, 0)
    phang200 = phang200.fillna(0)
    phang200 = phang200.where(phang200 > -np.inf, 0)
    # Zero the ranges
    phang38['ranges'] = phang38.ranges - 1.1
    phang200['ranges'] = phang200.ranges - 0.295
    # Interpolate along the ranges
    phang38 = phang38.swap_dims({"range_bin": "ranges"})
    phang38 = phang38.phang.interp(ranges=R)
    phang200 = phang200.swap_dims({"range_bin": "ranges"})
    phang200 = phang200.phang.interp(ranges=R)
    # Clip color ranges to [-75, -5] dB
    # phang38 = phang38.where(phang38 < -5, np.nan)
    # phang38 = phang38.where(phang38 > -75, np.nan)
    # phang200 = phang200.where(phang200 < -5, np.nan)
    # phang200 = phang200.where(phang200 > -75, np.nan)
    # Plot the echograms separately
    plt.figure()
    ax = phang38.T.plot(cmap="jet")
    ax.axes.invert_yaxis()
    plt.figure()
    ax1 = phang200.T.plot(cmap="jet")
    ax1.axes.invert_yaxis()
    # # Plot as a combined normalized image.
    # plt.figure()
    # IMAGE = np.stack((phang38.data, phang200.data)).transpose((2, 1, 0))
    # IMAGE[np.isnan(IMAGE)] = -75
    # IMAGE = (IMAGE - IMAGE.min()) / (IMAGE.max() - IMAGE.min())
    # IMAGE = np.concatenate((IMAGE, np.zeros((*IMAGE.shape[:2], 1))), axis=-1)
    # io.imshow(IMAGE)
