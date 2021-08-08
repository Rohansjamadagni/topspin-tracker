import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from functools import partial
from PIL import Image
import os
import pandas as pd

stroke_data = pd.read_csv('result.csv')

prev_index = 1
strokes_x_y = []
strokes = []

for pos, value in enumerate(stroke_data.iterrows()):
    if value[1]['stroke_number'] != prev_index:
        prev_index = value[1]['stroke_number']
        strokes_x_y.append(np.asarray(strokes))
        strokes = []
    x = value[1]['x']
    y = value[1]['y']
    strokes.append(np.asarray([x,y]))
strokes_x_y.append(np.asarray(strokes))


fig, ax = plt.subplots()
ln, = plt.plot([], [], 'r-')
im = Image.open('./pictures/table_image.png')

def init():
   ax.imshow(im)
   return ln,

def update(frame, x, y):
    print(frame)
    x.append(frame[0])
    y.append(frame[1]+200)
    ln.set_data(xdata, ydata)
    return ln,

xdata, ydata = [], []
ani = FuncAnimation(
    fig, partial(update, x=xdata, y=ydata),
    frames=strokes_x_y[0],
    init_func=init, blit=False, interval=1, repeat=False)


plt.show()