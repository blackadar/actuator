import re

import matplotlib.pyplot as plt
import pandas as pd


def parse(filepath: str):
    iter_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) Iteration (\d+) -> (\w+)")
    time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) Elapsed (\d+.\d+)")
    text = None

    with open(filepath, 'r') as file:
        text = file.read()

    data = []
    for iteration, time in zip(iter_pattern.finditer(text), time_pattern.finditer(text)):
        row = {'start': iteration.group(1),
               'end': time.group(1),
               'iteration': int(iteration.group(2)),
               'direction': iteration.group(3),
               'elapsed': float(time.group(2)),
               }
        data.append(row)

    df = pd.DataFrame(data)
    return df


def plot_home_elapsed(df):
    home_df = df.loc[df['direction'].str.contains('Home')]
    ax = plt.gca()
    home_df.plot(kind='line', x='iteration', y='elapsed', ax=ax)

    plt.show()


def plot_extend_elapsed(df):
    extend_df = df.loc[df['direction'].str.contains('Extend')]
    ax = plt.gca()
    extend_df.plot(kind='line', x='iteration', y='elapsed', ax=ax)

    plt.show()
