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
The vertices file specifies the coordinates of each tile's vertices. 
Row i contains the vertex coordinates for tile i and should be formatted (with vertices v in clockwise order)
as [v1-x-coord | v1-y-coord | v2-x-coord | v2-y-coord | v3-x-coord .... 
"""

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
    
def write_hull_file(hull_tiles, file_name):
    f = open(file_name, "x")
    for h in hull_tiles:
        f.write(str(h) + " ")
        f.write("\n")
    f.close()
    
    print("New hull tiles file with " + str(len(hull_tiles)) + " hull tiles saved to " + file_name)
    
        