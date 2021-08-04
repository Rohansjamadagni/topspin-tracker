import os
import cv2
import math
import numpy as np
from scipy.spatial import distance
import argparse


def parser():
    parser = argparse.ArgumentParser(description="Coordinate extraction")
    parser.add_argument("--input", type=str, default="pictures/table_image.png")
    return parser.parse_args()


def draw_circle(event, x, y, flags, param):
    global coordinates
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(img, (x, y), 10, (255, 0, 255), -1)
        mouseX, mouseY = x, y

        coordinates.append([x, y])

def take_picture():
    os.system('ansible-playbook -i ../ansible/hosts.yml ../ansible/picture.yml')

if __name__ == '__main__':
    if not os.isdir('pictures'):
        os.system("mkdir pictures")
    args = parser()
    
    take_picture()

    coordinates = []
    img = cv2.imread(args.input)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_circle)
    warped_coordinates = np.array(
        [[0, 0], [1920, 0], [0, 1080], [1920, 1080]], np.float32)

    while(1):
        cv2.imshow('image', img)
        k = cv2.waitKey(20) & 0xFF

        if k == 27:
            break
        elif k == ord('a'):
            print(coordinates)

        elif len(coordinates) == 6:
            init_cooridantes = np.array([
                coordinates[0], coordinates[2], coordinates[5], coordinates[3]], np.float32)

            print(coordinates)
            matrix = cv2.getPerspectiveTransform(
                init_cooridantes, warped_coordinates)
            result = cv2.warpPerspective(img, matrix, (1280, 720))

            pts = np.asarray(coordinates).reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, (255, 0, 255),
                          thickness=3)  # coordinates in cw manner
            break
    cv2.imshow("res", result)
    cv2.imwrite("pictures/warped.jpg", result)
    files = open('coordinates.txt', 'w')
    for i, j in coordinates:
        files.write(str(i) + ',' + str(j) + ' ')
    print("Coordinates successfully written to coordinates.txt! \n Note: Warped image available to view at warped.jpg")
    files.close()
