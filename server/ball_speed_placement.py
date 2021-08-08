import sys
import cv2
import math
import os
import json
import pandas as pd
import numpy as np
import json

stroke_data = {
    "data" : []
}

stroke_data_ = open('result.json', 'r')
stroke_data = json.loads(stroke_data_.read())
print(stroke_data['data'])
stroke_data_.close()

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
    strokes_x_y.append(np.asarray(stroke))
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
    print(len(strokes_x_y))
    for pos, stroke in enumerate(strokes_x_y):
        print('ffs', pos)
        x_coords = stroke[:, 0]
        y_coords = stroke[:, 1]
        speed_list = []
        position_of_net_cross = get_coordinate_of_net_cross(x_coords, midpoint_x)
        distances = []

        print(position_of_net_cross, 'pos', midpoint_x)
        # sys.exit(1)
        print(len(x_coords), len(y_coords))
        try:
            for point in range(position_of_net_cross-buffer, position_of_net_cross+buffer+1):
                speed_list.append([x_coords[point], y_coords[point]])
        except:
            pass
        
        for i in range(len(speed_list)-1):
            distances.append(euclidian_distance(
                speed_list[i][0], speed_list[i][1], speed_list[i+1][0], speed_list[i+1][1]
                ))
        speed = sum(distances) / (1 / fps * ((len(distances)+1)))
        speed = (speed * 2.74) / table_distance
        # find speed for each stroke
        speed *= 18 / 5

        speed_for_each_stroke[pos+1] = speed

    return speed_for_each_stroke


def get_zone(ball_coordinates, no_columns=6, no_rows=3):
    tt_table = np.zeros((3, 6), np.int32)
    table_map = {
        "03" : 1,
        "04" : 2,
        "05" : 3,
        "13" : 4,
        "14" : 5,
        "15" : 6,
        "23" : 7,
        "24" : 8,
        "25" : 9
    }

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

    # tt_table[bounce_row-1][bounce_col-1] += 1
    valid_check = str(bounce_row) + str(bounce_col)
    if valid_check in table_map:
        return str(table_map[valid_check])
    else:
        print('wrong coords')
        return str(3)


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
    position = get_zone([x,y])
    return position


def caluclate_speed_and_placements():
    global stroke_data
    # do speed tomorrow
    result = pd.read_csv('result.csv')
    left_bounces = result.groupby("stroke_number").first().reset_index()
    right_bounces = result.groupby("stroke_number").last().reset_index()
    speed_for_each_stroke = get_speed()

    print(speed_for_each_stroke, 'speed', len(left_bounces))
    bc = 0
    for bounces in zip(left_bounces.iterrows(), right_bounces.iterrows()):
        print(bc, 'bc')
        left, right = bounces[0][1], bounces[1][1]
        print(left['x'], right['x'], 'lr')
        data_ = {
            "stroke_name" : stroke_data['data'][bc]['stroke_name'],
            "stroke_number" : left['stroke_number'],
            "position" : get_transposed_coordinates(right['x'], right['y']),
            "speed" : speed_for_each_stroke[left['stroke_number']]
        }
        stroke_data['data'][bc] = data_
        if bc == 3:
            break
        bc += 1
    
    file_ = open('stroke_speed_result.json', 'w')
    json.dump(stroke_data, file_)


if __name__ == "__main__":
    caluclate_speed_and_placements()