import math
import os
import json
import pandas as pd
import numpy as np
import json

stroke_data = {
    "data" : []
}
speed_for_each_stroke = {}


def read_coordinates():
    f = open("coordinates.txt", 'r')
    data_ = f.read()
    data = data_.strip()
    str_table_coordinates = data.split(' ')
    table_coordinates = []
    for i in str_table_coordinates:
        table_coordinates.append(list(map(int, (i.split(',')))))
    return table_coordinates
    
    
def find_net(table_coordinates):
    """
    Finding net coordinates, taking avg of x1 and x4 (mid points of table)
    """
    top_x = table_coordinates[1][0]
    bottom_x = table_coordinates[4][0]
    avg = int((top_x+bottom_x)/2)

    return avg


def get_coordinate_of_net_cross(x_coords, midpoint_x=270):
    print(list(x_coords), midpoint_x)
    for pos, x_coordinate in enumerate(list(x_coords)):
        if x_coordinate >= midpoint_x:
            print('pos', pos)
            return pos
    
    # 1 2 3 4 5 6 7 8 9 9 10


def euclidian_distance(x1, y1, x2, y2):
    distance = math.sqrt(((x1 - x2)**2) + ((y1 - y2)**2))
    return distance


def get_speed(buffer=3, fps = 20):
    speed_for_each_stroke = {}
    table_coordinates = read_coordinates()
    midpoint_x = find_net(table_coordinates)
    coordinates_df = pd.read_csv('result.csv')
    stroke_number = coordinates_df['stroke_number']
    x_coords = coordinates_df['x']
    y_coords = coordinates_df['y']
    x_coords = list(x_coords)
    y_coords = list(y_coords)

    strokes_x_y = []
    prev_stroke_number = list(stroke_number)[0]
    stroke = []
    # separate strokes into array
    for i in coordinates_df.iterrows():
        # print(i[1]['stroke_number'])
        if prev_stroke_number != i[1]['stroke_number']:
            prev_stroke_number = i[1]['stroke_number']
            strokes_x_y.append(np.asarray(stroke))
            stroke = []
        stroke.append([i[1]['x'], i[1]['y']])

    # import sys
    # sys.exit(1)

    left_midpoint_coordinate = [
    ((table_coordinates[0][0] + table_coordinates[5][0]) / 2),
    ((table_coordinates[0][1] + table_coordinates[5][1]) / 2)]
    right_midpoint_coordinate = [
    ((table_coordinates[2][0] + table_coordinates[3][0]) / 2),
    ((table_coordinates[2][1] + table_coordinates[3][1]) / 2)]

    strokes_x_y = np.asarray(strokes_x_y)
    table_distance = euclidian_distance(
                    left_midpoint_coordinate[0],
                    left_midpoint_coordinate[1],
                    right_midpoint_coordinate[0],
                    right_midpoint_coordinate[1])

    # print(stroke)
    import sys
    for pos, stroke in enumerate(strokes_x_y):
        x_coords = stroke[:, 0]
        y_coords = stroke[:, 1]
        speed_list = []
        position_of_net_cross = get_coordinate_of_net_cross(x_coords)
        distances = []

        print(position_of_net_cross, 'pos')
        # sys.exit(1)

        for point in range(position_of_net_cross-buffer, position_of_net_cross+buffer+1):
            speed_list.append([x_coords[point], y_coords[point]])
        
        for i in range(len(speed_list)-1):
            distance.append(euclidian_distance(
                speed_list[i][0], speed_list[i][1], speed_list[i+1][0], speed_list[i+1][1]
                ))
        speed = sum(distances) / (1 / fps * ((len(distances)+1)))
        speed = (speed * 2.74) / table_distance
        # find speed for each stroke
        speed *= 18 / 5

        speed_for_each_stroke[pos] = speed

    return speed_for_each_stroke


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


def caluclate_speed_and_placements():
    global stroke_data
    # do speed tomorrow
    result = pd.read_csv('result.csv')
    left_bounces = result.groupby("stroke_number").first().reset_index()
    right_bounces = result.groupby("stroke_number").last().reset_index()
    speed_for_each_stroke = get_speed()
    for bounces in zip(left_bounces.iterrows(), right_bounces.iterrows()):
        left, right = bounces[0][1], bounces[1][1]
        data_ = {
            "stroke_number" : left['stroke_number'],
            "left" : get_transposed_coordinates(left['x'], left['y']),
            "right" : get_transposed_coordinates(right['x'], right['y']),
            "speed" : speed_for_each_stroke[left['stroke_number']]
        }
        stroke_data['data'].append(data_)
    
    file_ = open('stroke_speed_result.json', 'w')
    json.dump(stroke_data, file_)


if __name__ == "__main__":
    get_speed()
    caluclate_speed_and_placements()