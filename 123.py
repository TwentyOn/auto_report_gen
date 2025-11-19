from datetime import time
import math

import numpy as np
import pandas as pd


def time_to_seconds(time: time):
    seconds = 0
    seconds += time.hour * 3600
    seconds += time.minute * 60
    seconds += time.second
    return seconds


def seconds_to_time(seconds):
    seconds = seconds.astype(np.int64)
    hour = seconds // 3600
    minute = seconds % 3600 // 60
    second = seconds % 60
    return time(hour=hour, minute=minute, second=second)


a, b, c = time(17, 0, 0), time(18, 0, 0), time(19, 0, 0)

data = pd.Series((a, b, c))

print(time_to_seconds(a))

print(seconds_to_time(data.apply(time_to_seconds).mean()))
