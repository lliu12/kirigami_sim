# Given text files containing the constraints and vertices for a full expansion tile deployment of a kirigami pattern,
# Generate a hull file for all vertices that are not constrained to another tile (and are therefore on the outer hull)
# file containing vertices
# ith row of vertices file should hold coordinates for the ith tile's vertices, in the form x1 y1 x2 y2 ... 
vertices_file = open("stampfli132_vertices.txt")
constraints_file = open("stampfli132_constraints1.txt")

# file to output the constraints info to: to prevent accidental overwriting, only works if this file does not already exist
# out_file = "stampfli132_constraints1.txt"

tile_vertices = []
for l in (vertices_file.read().splitlines()):
    line = l.split()
    tile_vertices.append([(float(line[i-1]), float(line[i])) 
                          for i in range(len(line)) if i % 2 == 1])
vertices_file.close()

constraints = []
for l in (constraints_file.read().splitlines()):
    line = l.split()
    constraints.append([int(line[0]),int(line[1]), int(line[2]), int(line[3])])
constraints_file.close()

num_tiles = len(tile_vertices)
# list all the vertices in the form (t+1, i+1) where t+1 is the tile number and i+1 is the vertex number
unconnected_vertices = [[(t+1, i+1) for i in range(len(t))] for t in range(num_tiles)]

# go through the constraints file and remove all vertices that appear in it
