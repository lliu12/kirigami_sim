# Given a text file where each line contains the vertices for one tile in clockwise order around that tile,
# Generate a constraints file for the fully connected, full expansion tile version of the tiles (constraints going CCW)

# file containing vertices
# ith row of vertices file should hold coordinates for the ith tile's vertices, in the form x1 y1 x2 y2 ... 
vertices_file = open("info_files/penrose_star2224_vertices.txt")

# files to output the constraints info to: to prevent accidental overwriting, only works if the file does not already exist
out_constraints_file = "info_files/penrose_star2224_constraints1.txt"

# read vertices into tile_vertices
tile_vertices = []
for l in (vertices_file.read().splitlines()):
    line = l.split()
    tile_vertices.append([(float(line[i-1]), float(line[i])) 
                          for i in range(len(line)) if i % 2 == 1])
vertices_file.close()

constraints = []
# edges will be a dictionary where the keys are coordinates for the vertices of an edge
# and the values say which tile/vertex number is associated w said edge
edges = {}

for t in range(len(tile_vertices)):
    tile = tile_vertices[t]
    tilenum = t + 1
    for i in range(len(tile)):
        # search for a match for the edge between the vertex (a1, a2) and the vertex (b1, b2)
        a = tile[i]
        b = tile[(i + 1) % len(tile)]
        #  order the two vertices of the edge by comparing tuples
        if a <= b:
            edge = (a, b)
        else:
            edge = (b, a)
        # if a matching edge is already in the edges dict, remove it and add a constraint between the two edges
        match = edges.pop(edge, None)
        if match is not None:
            constraint = [match[0], match[1] + 1, tilenum, (i + 1) % (len(tile)) + 1]
            # print(constraint)
            constraints.append(constraint)
        # otherwise if no matching edge in the dict, add edge to the dict
        # by storing edge as a key with value (tilenum, (i + 1) % (len(tile))) 
        # # (i being the lower vertex number adjacent to the edge)
        else:
            edges[edge] = (tilenum, (i + 1) % (len(tile)))

# # the remaining edges that haven't been matched comprise the vertices of the contracted hull (possibly in wrong order though)
# unmatched_edge_vertices = [vertex for vertex in edges.values()]

f = open(out_constraints_file, "x")
for c in constraints:
    for i in c:
        f.write(str(i) + " ")
    f.write("\n")
f.close()

print("Full expansion constraints file saved to " + out_constraints_file)

# this code was meant to save hull info, but it does not work
# f_hull = open(out_hull_file, "x")
# for v in unmatched_edge_vertices:
#     for i in v:
#         f_hull.write(str(i) + " ")
#     f_hull.write("\n")
# f_hull.close()