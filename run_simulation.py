# read inputs, run simulation

import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util
import numpy as np
from simulation import Simulation
import matplotlib.pyplot as plt

# constants
# offsets + scaling constant to help get vertices centered in the display screen
X_OFFSET = 350
Y_OFFSET = 350
VERTEX_MULTIPLIER = .5
DISPLAY_SIZE = (800,800)
IS_INTERACTIVE = True
# use a given hull file to calculate and display the area of the pattern
CALCULATE_AREA_PERIM = True
# only display the vertices of shapes (so screenshots can be used for fourier transform)
FOURIER = False
# automatically apply force with this magnitude outwards on pattern
AUTO_EXPAND = True
spring_stiffness = 80
spring_damping = 1000

ADD_ROTARY_SPRINGS = False


# files
vertices_file = open("info_files/penrose110_vertices.txt")
constraints_file = open("info_files/penrose110_constraints2.txt")

if CALCULATE_AREA_PERIM or AUTO_EXPAND:
    hull_file = open("info_files/penrose110_hull2.txt")


# read vertices into tile_vertices
# ith row of vertices file should hold coordinates for the ith tile's vertices, in the form x1 y1 x2 y2 ... 
tile_vertices = []
for l in (vertices_file.read().splitlines()):
    line = l.split()
    tile_vertices.append([(float(line[i-1]) * VERTEX_MULTIPLIER + X_OFFSET, float(line[i]) * VERTEX_MULTIPLIER + Y_OFFSET) 
                          for i in range(len(line)) if i % 2 == 1])

# calculate tile centers by averaging x and y coords of vertices
# return the center of a single tile given a list of its vertices
def get_center(t):
    tt = np.array(t)
    x_av = np.mean(tt[:,0])
    y_av = np.mean(tt[:,1])
    return (x_av, y_av)
tile_centers = [get_center(t) for t in tile_vertices]

# calculate the center of the whole pattern by averaging x and y coords of tile centers
pattern_center = get_center(tile_centers)

# read constraints from txt file into a list where each row has the form:
# [constraint tile 1, vertex number to pin from this tile, constraint tile 2, vertex to pin from this tile]
# subtracts 1 from everything to move to 0-indexing for python
constraints = []
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

if CALCULATE_AREA_PERIM or AUTO_EXPAND:
    hull_vertices = []
    for l in (hull_file.read().splitlines()):
        line = l.split()
        hull_vertices.append([int(line[0]) - 1, int(line[1]) - 1])
    hull_file.close()
    initial_hull_area = area([tile_vertices[(v[0])][(v[1])] for v in hull_vertices])

    perimeter = 0
    for i in range(len(hull_vertices)):
        v1 = hull_vertices[i]
        v2 = hull_vertices[(i + 1) % len(hull_vertices)]
        pos1 = tile_vertices[(v1[0])][(v1[1])]
        pos2 = tile_vertices[(v2[0])][(v2[1])]
        perimeter += np.linalg.norm(np.array(pos1) - np.array(pos2))

    
    # for i in range(len(hull_vertices)):
    #     perimeter += np.linalg.norm(np.array(hull_vertices[i]) - np.array(hull_vertices[(i + 1) % len(hull_vertices)]))
else:
    hull_vertices = None

# run game
def main():
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY_SIZE, 0) 
    _, height = screen.get_size()
    # max_scr = 1
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 16)

    params = {
        "X_OFFSET": X_OFFSET,
        "Y_OFFSET": Y_OFFSET,
        "VERTEX_MULTIPLIER": VERTEX_MULTIPLIER,
        "IS_INTERACTIVE": IS_INTERACTIVE,
        "CALCULATE_AREA_PERIM": CALCULATE_AREA_PERIM,
        "FOURIER": FOURIER,
        "AUTO_EXPAND": AUTO_EXPAND,
        "SPRING_STIFFNESS": spring_stiffness,
        "SPRING_DAMPING": spring_damping
    }

    sim = Simulation(tile_centers, tile_vertices, constraints, pattern_center, params, hull_vertices, screen, add_rotary_springs= ADD_ROTARY_SPRINGS)

    while running:
        for event in pygame.event.get():
            # returns false if the event is one that tells the simulation to quit
            sim.handler.handle_event(event)
            running = sim.handler.running
        
        screen.fill(THECOLORS["white"]) # clear the screen
        sim.draw_shapes()

        # Update physics
        fps = 25
        iterations = 10
        dt = 1.0/float(fps)/float(iterations)
        for _ in range(iterations):
            sim.space.step(dt)
        
        # Flip screen
        if IS_INTERACTIVE:
            screen.blit(font.render("fps: " + str(round(clock.get_fps(), 4)), 1, THECOLORS["darkgrey"]), (5,0))
            screen.blit(font.render("Left click and drag to interact", 1, THECOLORS["darkgrey"]), (5,height - 65))
            screen.blit(font.render("Right click to pin/unpin a tile's position", 1, THECOLORS["darkgrey"]), (5,height - 50))
            screen.blit(font.render("Press R to reset", 1, THECOLORS["darkgrey"]), (5,height - 35))
            screen.blit(font.render("Press P to save screen image", 1, THECOLORS["darkgrey"]), (5,height - 20))
        
        if CALCULATE_AREA_PERIM: 
            current_hull_area = area([sim.vertex_bodies[(v[0])][(v[1])].position for v in sim.hull_vertices])
            current_scr = (round(current_hull_area / initial_hull_area, 4))
            screen.blit(font.render("SCR (Current Area / Contracted Area) : " + str(current_scr), 1, THECOLORS["darkgrey"]), (5,15))
            if current_scr > sim.max_scr:
                sim.max_scr = current_scr
            screen.blit(font.render("Max SCR Observed: " + str(sim.max_scr), 1, THECOLORS["darkgrey"]), (5,30))
            screen.blit(font.render("Hull Perimeter: " + str(perimeter), 1, THECOLORS["darkgrey"]), (5,45))

            # # number spring index
            # for i, spring in enumerate(sim.expansion_springs):
            #     coords = (sim.center_shapes[sim.hull_tiles[i]].body.position[0], height - sim.center_shapes[sim.hull_tiles[i]].body.position[1])
            #     screen.blit(font.render(str(i), 1, THECOLORS["darkgrey"]), coords)

        pygame.display.flip()
        clock.tick(fps)
        
if __name__ == '__main__':
    sys.exit(main())