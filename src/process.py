import os
from os import path
from os.path import join
import re
from numpy import array
from numpy.linalg import norm
from copy import deepcopy

GCODE = []
PREV_G0 = True
COORDS = []
prev_x = -.35643
prev_y = 12.78465
prev_z = 0.645
last_u = 0

prev_coordinates = [prev_x, prev_y, prev_z]


def euclidean_distance(current, prev):
    current_cord = array(current)
    prev_cord = array(prev)
    return norm(current_cord - prev_cord)


def calc_u(eucledian_dist):
    layer_height = 0.7
    nozzle_dia = 0.8
    pi = 22/7
    filament_dia = 1.75
    u = layer_height * eucledian_dist * nozzle_dia/ (pi * filament_dia)
    return u


def get_coordinates(line):
    global prev_coordinates
    prev_cord_copy = deepcopy(prev_coordinates)

    x = re.findall(r'X[\-]?[0-9]*[\.]*[0-9]*', line)

    y = re.findall(r'Y[\-]?[0-9]*[\.]*[0-9]*', line)
    z = re.findall(r'Z[\-]?[0-9]*[\.]*[0-9]*', line)
    if len(x) != 0:
        x = float(x[0][1:])
        prev_coordinates[0] = x
    else:
        x = prev_coordinates[0]
    if len(y) != 0:
        y = float(y[0][1:])
        prev_coordinates[1] = y
    else:
        y = prev_coordinates[1]
    if len(z) != 0:
        z = float(z[0][1:])
        prev_coordinates[2] = z
    else:
        z = prev_coordinates[2]
    coordinates = [x, y, z]
    result = coordinates, prev_cord_copy
    return result


def extrude(line):
    global PREV_G0
    x = int(line.count('X'))
    y = int(line.count('Y'))
    z = int(line.count('Z'))
    g0 = int(line.count('G0'))
    g1 = int(line.count('G1'))
    condition1 = True if(x+y+z > 0) else False
    condition2 = (False if(g0 > 0) else True)
    condition3 = True if(g1 > 0) else False

    result = (condition1 and ((condition2 and not PREV_G0) or condition3), PREV_G0)

    # update PREV_G0
    if g1 > 0:
        PREV_G0 = False
    return result


def get_gcode_file_descriptor(file_path):
    global PREV_G0
    flag = ["No Prev G0"]
    lextrude = ["No Extrude"]
    f_out = open('gcode_u_0_6and0_7.txt', 'w')
    str_line = ""
    global last_u
    with open(file_path, 'r') as f:
        for line in f:
            # COORDS.append(get_coordinates(line))
            if extrude(line)[0]:
                lextrude = ["Extrude"]
                cur, prev = get_coordinates(line)
                dist = euclidean_distance(cur, prev)
                u = round(calc_u(dist) + last_u, 4)
                last_u = u
                str_line = deepcopy(line).strip('\n')
                f_out.write(str_line + ' U' + str(u) + '\n')
            else:
                f_out.write(line)
            # if extrude(line)[1]:
            #     flag = ["Prev G0"]
            # else:
            #     flag = ["No Prev G0"]
            # GCODE.append((line.split()) + flag + lextrude)


get_gcode_file_descriptor('PIPE-0DEGREE-0-4.txt')
counter = 0
for i in COORDS:
    print(i, euclidean_distance(i[0], i[1]))
    counter+=1
    if counter == 20:
        break


