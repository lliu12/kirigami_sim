import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util
import numpy as np
from simulation import Simulation
import os

spring_stiffness = 80
spring_damping = 1000

secs_to_simulate = 30 # number of seconds to simulate

# files - data collection script assumes auto expand is always on
vertices_file = open("info_files/penrose110_nothinrhombs_vertices.txt")
constraints_file = open("info_files/penrose110_nothinrhombs_constraints1.txt")
hull_file = open("info_files/penrose110_nothinrhombs_hull1.txt")

# folder to save data to
out_folder_name = "penrose_removal"
if not os.path.exists(out_folder_name):
    os.makedirs(out_folder_name)
os.makedirs(out_folder_name + "/centers")
os.makedirs(out_folder_name + "/vertices")

# should probably save to this folder a log file describing the parameters of this run
temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))

params = {
"X_OFFSET": 0,
"Y_OFFSET": 0,
"VERTEX_MULTIPLIER": 1,
"IS_INTERACTIVE": True,
"CALCULATE_AREA_PERIM": True,
"FOURIER": False,
"AUTO_EXPAND": True,
"SPRING_STIFFNESS": spring_stiffness,
"SPRING_DAMPING": spring_damping,
}

tile_vertices = [] # read in tile vertices
for l in (vertices_file.read().splitlines()):
    line = l.split()
    tile_vertices.append([(float(line[i-1]) * params["VERTEX_MULTIPLIER"] + params["X_OFFSET"], float(line[i]) * params["VERTEX_MULTIPLIER"] + params["Y_OFFSET"]) 
                          for i in range(len(line)) if i % 2 == 1])

def get_center(t): # use to get tile and pattern center
    tt = np.array(t)
    x_av = np.mean(tt[:,0])
    y_av = np.mean(tt[:,1])
    return (x_av, y_av)
tile_centers = [get_center(t) for t in tile_vertices]

pattern_center = get_center(tile_centers)

constraints = [] # read in pattern constraints
for l in (constraints_file.read().splitlines()):
    line = l.split()
    constraints.append([int(line[0]) - 1,int(line[1]) - 1, int(line[2]) - 1, int(line[3]) - 1])

# close files
vertices_file.close()
constraints_file.close()

# use the shoelace formula to find the area of a polygon, given its vertices in clockwise order
def segments(v):
    return zip(v, v[1:] + [v[0]])

def area(v):
    return 0.5 * abs(np.sum([x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(v)]))

hull_vertices = [] # read in hull file
for l in (hull_file.read().splitlines()):
    line = l.split()
    hull_vertices.append([int(line[0]) - 1, int(line[1]) - 1])
hull_file.close()
initial_hull_area = area([tile_vertices[(v[0])][(v[1])] for v in hull_vertices])

def main():

    pygame.init()
    screen = pygame.display.set_mode((800,800), 0) 
    _, height = screen.get_size()

    sim = Simulation(tile_centers, tile_vertices, constraints, pattern_center, params, hull_vertices, screen)

    # dt = 1./25. # time in seconds between simulation steps
    # steps_per_sample = 10 # record a data sample every __ steps of the simulation

    samples_per_second = 10 # number of data samples to take per second
    steps_per_sample = 25 # number of simulation steps to take for each sample
    dt = 1. / (samples_per_second * steps_per_sample) # step size to take in simulation

    steps_taken = 0
    for i in range(secs_to_simulate * samples_per_second):
        if i % 100 == 0:
            print("Working on sample " + str(i) + " of " + str(secs_to_simulate * samples_per_second))

        cur_string = "0" + str(i) if i < 10 else str(i)
        # collect data...

        # collect vertices.txt in its own folder (still need to set up the folder and naming)
        save_vertices_file = open(out_folder_name + "/vertices/kirigami_simulation_vertices" + cur_string + ".txt", "x")
        current_vertices = []
        for center in sim.center_shapes:
            vertices = map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                    (x.rotated(center.body.angle) + center.body.position)[1]),
                                                            center.get_vertices())
            v_list = list(vertices)
            for v in range(len(v_list)):
                pos = v_list[-v]
                save_vertices_file.write(str(round((pos[0] - sim.params["X_OFFSET"]) / sim.params["VERTEX_MULTIPLIER"], 3)) + " " + str(round((pos[1] - sim.params["Y_OFFSET"]) / sim.params["VERTEX_MULTIPLIER"], 3)) + " ")
            save_vertices_file.write("\n")
        save_vertices_file.close()

        # collect centers.txt in its own folder
        save_centers_file = open(out_folder_name + "/centers/kirigami_simulation_centers" + cur_string + ".txt", "x")
        current_centers = []
        for center in sim.center_shapes:
            save_centers_file.write(str(round((center.body.position[0] - sim.params["X_OFFSET"]) / sim.params["VERTEX_MULTIPLIER"], 3)) + " " + str(round((center.body.position[1] - sim.params["Y_OFFSET"]) / sim.params["VERTEX_MULTIPLIER"], 3)) + "\n")
        save_centers_file.close()

        # collect area in a single list/1D numpy array

        # collect hull springs impulses in a 2D array (cols = springs, rows = impulse at sample point)

        # collect angular spring impulses in a 2D array


        for _ in range(steps_per_sample):
            sim.space.step(dt)

if __name__ == '__main__':
    sys.exit(main())


