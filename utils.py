import argparse
import numpy as np
import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util


"""
parse command-line arguments
"""
def parse_args():
    parser = argparse.ArgumentParser()

    # input files
    parser.add_argument("--vertices_file", type=str, required=True)
    parser.add_argument("--constraints_file", type=str, required=True)
    parser.add_argument("--hull_vertices_file", type=str)
    parser.add_argument("--hull_tiles_file", type=str)

    # offsets & scaling to apply to input coordinates
    parser.add_argument("--x_offset", type=int, default=350)
    parser.add_argument("--y_offset", type=int, default=350)
    parser.add_argument("--vertex_multiplier", type=float, default=.5)

    # screen dimension
    parser.add_argument("--display_size", type=tuple, default=(800, 800))

    # interactive features
    parser.add_argument("--is_interactive", default=False, type=lambda s: s.lower() == 'true') # respond to user clicks
    parser.add_argument("--calculate_area_perim", default=False, type=lambda s: s.lower() == 'true')
    parser.add_argument("--vertices_only", default=False, type=lambda s: s.lower() == 'true') # display tile vertices only
    parser.add_argument("--auto_expand", default=False, type=lambda s: s.lower() == 'true') # automatically use springs to pull outward
    parser.add_argument("--auto_expand_oblong", default=False, type=lambda s: s.lower() == 'true')
    parser.add_argument("--display_expansion_springs", default=True, type=lambda s: s.lower() == 'true')
    parser.add_argument("--spring_stiffness", type=int, default=80)
    parser.add_argument("--spring_damping", type=int, default=1000)

    return parser.parse_args()

def check_args(args):
    if args.calculate_area_perim or args.auto_expand:
        assert args.hull_vertices_file is not None or args.hull_tiles_file is not None, "Hull information file required for auto-expansion"
    if args.calculate_area_perim:
        assert args.hull_vertices_file is not None, "Hull vertices file required for area calculation"


"""
The vertices file specifies the coordinates of each tile's vertices. 
Row i contains the vertex coordinates for tile i and should be formatted (with vertices v in clockwise order)
as [v1-x-coord | v1-y-coord | v2-x-coord | v2-y-coord | v3-x-coord .... 
"""

def read_vertices_file(file_name, params):
    vertices_file = open(file_name)
    tile_vertices = []
    for l in (vertices_file.read().splitlines()):
        line = l.split()
        tile_vertices.append([(float(line[i-1]) * params["vertex_multiplier"] + params["x_offset"], float(line[i]) * params["vertex_multiplier"] + params["y_offset"]) 
                            for i in range(len(line)) if i % 2 == 1])
    vertices_file.close()
    return tile_vertices


def write_vertices_file(tile_vertices, file_name):
    f = open(file_name, "x")
    for t in tile_vertices:
        for i in t:
            for j in i:
                f.write(str(j) + " ")
        f.write("\n")
    f.close()

    print("New vertex file with " + str(len(tile_vertices)) + " vertices saved to: " + file_name)
    

"""
In the constraints file, order of rows doesn't matter and each row takes the form
[Tile i | Vertex Number p in Tile i | Tile j | Vertex Number q in Tile j]
(tile numbers are 1-indexed)
"""

def read_constraints_file(file_name):
    constraints_file = open(file_name)
    constraints = []
    for l in (constraints_file.read().splitlines()):
        line = l.split()
        # subtracts 1 from everything to move to 0-indexing for python
        constraints.append([int(line[0]) - 1,int(line[1]) - 1, int(line[2]) - 1, int(line[3]) - 1])
    constraints_file.close()
    return constraints
    
def write_constraints_file(constraints, file_name):
    f = open(file_name, "x")
    for c in constraints:
        for i in c:
            f.write(str(i) + " ")
        f.write("\n")
    f.close()

    print("New constraints file with " + str(len(constraints)) + " constraints saved to: " + file_name)
    

"""
List (any order) of tiles in the outer hull of the pattern, so that springs can be added to these tiles.
(tile numbers are 1-indexed)
"""
    
def write_hull_tiles_file(hull_tiles, file_name):
    f = open(file_name, "x")
    for h in hull_tiles:
        f.write(str(h) + " ")
        f.write("\n")
    f.close()
    print("New hull tiles file with " + str(len(hull_tiles)) + " hull tiles saved to " + file_name)

def read_hull_vertices_file(file_name):
    hull_vertices_file = open(file_name)
    hull_vertices = []
    for l in (hull_vertices_file.read().splitlines()):
        line = l.split()
        hull_vertices.append([int(line[0]) - 1, int(line[1]) - 1])
    hull_vertices_file.close()
    return hull_vertices

def read_hull_tiles_file(file_name):
    hull_tiles_file = open(file_name)
    hull_tiles = []
    for t in (hull_tiles_file.read().split()):
        hull_tiles.append(int(t) - 1)
    hull_tiles_file.close()
    return hull_tiles

# return the center of a single tile given a list of its vertices
def get_center(t):
    tt = np.array(t)
    x_av = np.mean(tt[:,0])
    y_av = np.mean(tt[:,1])
    return (x_av, y_av)

def to_pygame(p, height):
    return int(p.x), int(height - p.y)

def from_pygame(p, height): 
    return to_pygame(p, height)


# draw a simulation state on a provided pygame screen
def draw_shapes(sim, screen):
    _, height = screen.get_size()

    if not sim.params['vertices_only']:
        for i in range(len(sim.center_shapes)):
            center = sim.center_shapes[i]
            (node_x, node_y) = center.body.position
            pygame.draw.polygon(screen, 
                                center.color, 
                                list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                    height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                            center.get_vertices())))
            pygame.draw.polygon(screen, 
                                THECOLORS["lightskyblue2"], 
                                list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                    height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                            center.get_vertices())), 1)

            font = pygame.font.Font(None, 16)

            if sim.params["calculate_area_perim"]:
                pygame.draw.polygon(screen, 
                                    THECOLORS["lightskyblue3"], 
                                    list(map(lambda x: to_pygame(x, height),
                                    [sim.vertex_bodies[(v[0])][(v[1])].position for v in sim.hull_vertices])), 1)

        for c in sim.space.constraints:
            if c in sim.expansion_springs:
                if sim.params["display_expansion_springs"]:
                    pv1 = c.a.position + (c.anchor_a).rotated(c.a.angle)
                    pv2 = c.b.position + (c.anchor_b).rotated(c.b.angle)
                    p1 = to_pygame(pv1, height)
                    p2 = to_pygame(pv2, height)
                    pygame.draw.aalines(sim.screen, THECOLORS["skyblue"], False, [p1,p2]) # remove this line to hide the springs

            else:
                pv1 = c.a.position + (c.anchor_a).rotated(c.a.angle)
                pv2 = c.b.position + (c.anchor_b).rotated(c.b.angle)
                p1 = to_pygame(pv1, height)
                p2 = to_pygame(pv2, height)
                pygame.draw.aalines(screen, THECOLORS["skyblue"], False, [p1,p2])
            
        for s in sim.static_pins:
            pygame.draw.circle(screen, THECOLORS["royalblue1"], to_pygame(s.b.position, height), 5)

    if sim.params['vertices_only']:
        for center in sim.center_shapes:
            vertices = map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                        height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                center.get_vertices())
            for pos in vertices:
                pygame.draw.circle(screen, THECOLORS["black"], pos, 1)
