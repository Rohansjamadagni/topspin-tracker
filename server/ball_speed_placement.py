import os
import json
import pandas as pd
import numpy as np
import json

stroke_data = {
    "data" : []
}

def caluclate_speed():
    pass


def read_coordinates():
    f = open("coordinates.txt", 'r')
    data_ = f.read()
    data = data_.strip()
    str_table_coordinates = data.split(' ')
    table_coordinates = []
    for i in str_table_coordinates:
    table_coordinates.append(list(map(int, (i.split(',')))))
    return table_coordinates


def warp_coordinates(x, y, matrix):
    p = (x, y)

    px = (matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]) / \
        ((matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
    
    py = (matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]) / \
        ((matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))

    return [int(px), int(py)]


def get_transposed_coordinates(x, y):
    table_coordinates = read_coordinates()
    table_coordinates_corners = np.array([
        table_coordinates[0],
        table_coordinates[2],
        table_coordinates[5],
        table_coordinates[3]
        ], np.float32)
    
    warped_dimensions = np.array([[0, 0], [1920, 0], [0, 1080], [1920, 1080]], np.float32)

    matrix = cv2.getPerspectiveTransform(table_coordinates_corners,
                                         warped_dimensions)

    x, y = warp_coordinates(x, y, matrix)
    return [x, y]



def caluclate_placements():
    # do speed tomorrow
    result = pd.read_csv('result.csv')
    left_bounces = result.groupby("stroke_number").first().reset_index()
    right_bounces = result.groupby("stroke_number").last().reset_index()

    for bounces in zip(left_bounces.iterrows(), right_bounces.iterrows()):
        left, right = bounces[0][1], bounces[1][1]
        data_ = 
        {
            "stroke_number" : left['stroke_number']
            "left" : get_transposed_coordinates(left['x'], left['y'])
            "right" : get_transposed_coordinates(right['x'], right['y'])
            "speed" : caluclate_speed()
        }
        


