import sys
import threading
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


import random
import cv2 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from functools import partial
from PIL import Image
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
sns.set()

matplotlib.use("TkAgg")

tt_table = np.zeros((3, 6), np.int32)

stroke_row_col = []

def warp_coordinates(x, y, matrix):
    print('warping')
    print(x, y, 'pints')
    p = (x, y)

    px = (matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]) / \
        ((matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
    
    py = (matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]) / \
        ((matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
    print(px, py, ' warped pints')
    return [int(px), int(py)]


def visualize_strokes():
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
    

    path = './pictures/table_image.png'
    image = cv2.imread(path) 

    center_coordinates = (120, 50)

    for x, strokes in enumerate(strokes_x_y):
        colors = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        for i in range(0, len(strokes)-1):
            start_point = strokes[i]
            end_point = strokes[i+1]
            start_point = start_point.astype('int32')
            end_point = end_point.astype('int32')
            start_x, start_y = start_point
            end_x, end_y = end_point
            start_x = int(start_x*960/1920)
            start_y = int(start_y*540/1080)
            end_x = int(end_x*960/1920)
            end_y = int(end_y*540/1080)
            offset_ = int(150*540/1080)
            image = cv2.line(image, (start_x, start_y+offset_), (end_x, end_y+offset_), colors, thickness=10)
            image = cv2.resize(image, (960, 540))
            cv2.imshow("result", image)
            cv2.waitKey(100)

    cv2.destroyAllWindows()

def read_coordinates():
    f = open("coordinates.txt", 'r')
    data_ = f.read()
    data = data_.strip()
    str_table_coordinates = data.split(' ')
    table_coordinates = []
    for i in str_table_coordinates:
        table_coordinates.append(list(map(int, (i.split(',')))))
    return table_coordinates


def get_transposed_coordinates(x, y):
    table_coordinates = read_coordinates()
    table_coordinates_corners = np.array([
        table_coordinates[0],
        table_coordinates[2],
        table_coordinates[3],
        table_coordinates[5]
        ], np.float32)
    
    print(table_coordinates, 'table coords')

    warped_dimensions = np.array([[0, 0], [1920, 0], [0, 1080], [1920, 1080]], np.float32)


    matrix = cv2.getPerspectiveTransform(table_coordinates_corners,
                                         warped_dimensions)

    x, y = warp_coordinates(x, y, matrix)
    return get_zone([x,y])


def get_zone(ball_coordinates, no_columns=6, no_rows=3):
    global tt_table
    col_seg = 1920 / no_columns
    row_seg = 1080 / no_rows
    bounce_col = 0
    bounce_row = 0

    for i in range(1, no_columns+1):
        if ball_coordinates[0] < col_seg * i:
            bounce_col = i
            break

    for i in range(1, no_rows+1):
        if ball_coordinates[1] < row_seg * i:
            bounce_row = i
            break

    tt_table[bounce_row-1][bounce_col-1] += 1

    return [bounce_row, bounce_col]


def visualize_warped_table():
    global stroke_row_col
    result = pd.read_csv('result.csv')
    left_bounces = result.groupby("stroke_number").first().reset_index()
    right_bounces = result.groupby("stroke_number").last().reset_index()

    bc = 0
    for bounces in zip(left_bounces.iterrows(), right_bounces.iterrows()):
        left, right = bounces[0][1], bounces[1][1]
        left_ = get_transposed_coordinates(left['x'], left['y'])
        right_ = get_transposed_coordinates(right['x'], right['y'])
        stroke_row_col.append(left_)
        stroke_row_col.append(right_)

        if bc == 3:
            break
        bc += 1
    
    file_ = open('stroke_speed_result.json', 'w')
    # json.dump(stroke_data, file_)

    
def display_plot():
    global tt_table
    ax = sns.heatmap(tt_table, cbar=False, annot=True, fmt="d")
    plt.savefig('plot.jpg')
    plt.close()


visualize_warped_table()
print(stroke_row_col, 'wtf')
# display_plot()

def animate_heat_map():
    global stroke_row_col
    fig = plt.figure()
    tt = np.zeros((3, 6), np.int32)
    nx = 3
    ny = 6
    data = np.random.rand(nx, ny)
    ax = sns.heatmap(data, vmin=0, vmax=1)

    def init():
        plt.clf()
        ax = sns.heatmap(tt, cbar=False, annot=True, fmt="d")

    def animate(i):
        if i >= len(stroke_row_col):
            sys.exit(0)
        plt.clf()
        x, y = stroke_row_col[i]
        tt[x-1, y-1] += 1
        ax = sns.heatmap(tt, cbar=False, annot=True, fmt="d")

    anim = animation.FuncAnimation(fig, animate, init_func=init, blit=False, interval=800)

    plt.show()

t1 = threading.Thread(target=animate_heat_map, )
t2 = threading.Thread(target=visualize_strokes, )

t1.start()
    # starting thread 2
t2.start()

t1.join()
t2.join()