import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_bottom_data(filename):
    with open(filename, "r") as f:
        bb_bottom_data = json.load(f)
    channels = bb_bottom_data.pop('channels')
    frequencies = [channel.pop("nominalFrequency") for channel in channels]
    blocks = [channel.pop("blocks")[0] for channel in channels]
    times = [block.pop("times") for block in blocks]
    depths = [block.pop("depths") for block in blocks]
    return pd.DataFrame(zip(times[0], depths[0]), columns=["timestamps", "ranges"])

bottom_dir = Path(r"C:\Users\fletho\Documents\LSSS_DATA\S1_PTESTSHIP[42]\Export\BroadbandBottomData").resolve()
bottom_paths = bottom_dir.glob("*.json")
for bottom_path in bottom_paths:
    data = get_bottom_data(bottom_path)
    data["ranges"] = data["ranges"].where(data["ranges"] > 0, np.nan)
    ax = data.plot()
    ax.invert_yaxis()