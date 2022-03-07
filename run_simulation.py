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
from event_handler import EventHandler
import matplotlib.pyplot as plt
from utils import *

args = parse_args() # read in command line args
check_args(args) # check that they satisfy our constraints
params = vars(args) # create dictionary version

tile_vertices = read_vertices_file(args.vertices_file, params)
constraints = read_constraints_file(args.constraints_file)

hull_vertices = None
hull_tiles = None
if args.hull_vertices_file is not None:
    hull_vertices = read_hull_vertices_file(args.hull_vertices_file)
    hull_tiles = list(set(list(zip(*(hull_vertices)))[0]))
elif args.hull_tiles_file is not None:
    hull_tiles = read_hull_tiles_file(args.hull_tiles_file)
    
# use the shoelace formula to find the area of a polygon, given its vertices in clockwise order
def segments(v):
    return zip(v, v[1:] + [v[0]])

def area(v):
    return 0.5 * abs(np.sum([x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(v)]))

if args.calculate_area_perim:
    initial_hull_area = area([tile_vertices[(v[0])][(v[1])] for v in hull_vertices])
    perimeter = 0
    for i in range(len(hull_vertices)):
        v1 = hull_vertices[i]
        v2 = hull_vertices[(i + 1) % len(hull_vertices)]
        pos1 = tile_vertices[(v1[0])][(v1[1])]
        pos2 = tile_vertices[(v2[0])][(v2[1])]
        perimeter += np.linalg.norm(np.array(pos1) - np.array(pos2))


# run game
def main():
    pygame.init()
    screen = pygame.display.set_mode(args.display_size, 0) 
    _, height = screen.get_size()
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 16)

    sim = Simulation(tile_vertices, constraints, params, hull_vertices, hull_tiles)
    handler = EventHandler(sim, screen)

    while running:
        for event in pygame.event.get():
            # returns false if the event is one that tells the simulation to quit
            handler.handle_event(event)
            running = handler.running
        
        screen.fill(THECOLORS["white"]) # clear the screen
        draw_shapes(sim, screen)

        # Update physics
        fps = 25
        iterations = 10
        dt = 1.0/float(fps)/float(iterations)
        for _ in range(iterations):
            sim.space.step(dt)
        
        # Flip screen
        if args.is_interactive:
            screen.blit(font.render("fps: " + str(round(clock.get_fps(), 4)), 1, THECOLORS["darkgrey"]), (5,0))
            screen.blit(font.render("Left click and drag to interact", 1, THECOLORS["darkgrey"]), (5,height - 65))
            screen.blit(font.render("Right click to pin/unpin a tile's position", 1, THECOLORS["darkgrey"]), (5,height - 50))
            screen.blit(font.render("Press R to reset", 1, THECOLORS["darkgrey"]), (5,height - 35))
            screen.blit(font.render("Press P to save screen image", 1, THECOLORS["darkgrey"]), (5,height - 20))
        
        if args.calculate_area_perim: 
            current_hull_area = area([sim.vertex_bodies[(v[0])][(v[1])].position for v in sim.hull_vertices])
            current_scr = (round(current_hull_area / initial_hull_area, 4))
            screen.blit(font.render("SCR (Current Area / Contracted Area) : " + str(current_scr), 1, THECOLORS["darkgrey"]), (5,15))
            if current_scr > sim.max_scr:
                sim.max_scr = current_scr
            screen.blit(font.render("Max SCR Observed: " + str(sim.max_scr), 1, THECOLORS["darkgrey"]), (5,30))
            screen.blit(font.render("Hull Perimeter: " + str(perimeter), 1, THECOLORS["darkgrey"]), (5,45))

        pygame.display.flip()
        clock.tick(fps)
        
if __name__ == '__main__':
    sys.exit(main())