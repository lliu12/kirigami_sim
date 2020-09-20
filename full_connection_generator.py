# Given a text file where each line contains the vertices for one tile in clockwise order around that tile,
# Generate a constraints file where there is a constraint between any two vertices sharing a position

# file containing vertices
# ith row of vertices file should hold coordinates for the ith tile's vertices, in the form x1 y1 x2 y2 ... 
vertices_file = open("info_files/penrose110_fifth_vertices.txt")

# files to output the constraints and hull info to: to prevent accidental overwriting, only works if the file does not already exist
out_constraints_file = "info_files/penrose110_fifth_constraints_dp.txt"

# read vertices into tile_vertices
tile_vertices = []
for l in (vertices_file.read().splitlines()):
    line = l.split()
    tile_vertices.append([(float(line[i-1]), float(line[i])) 
                          for i in range(len(line)) if i % 2 == 1])
vertices_file.close()

constraints = []

# check all possible matches between vertex positions; if a new match is found create a constraint
for t in range(len(tile_vertices)):
    tile = tile_vertices[t]
    tilenum = t + 1
    for i in range(len(tile)):
        vertex = tile[i]
        for tt in range(t, len(tile_vertices)):
            temptile = tile_vertices[tt]
            temptilenum = tt + 1
            for j in range(len(temptile)):
                tempvertex = temptile[j]
                if(tempvertex == vertex 
                   and (tilenum != temptilenum or i != j)):
                #    and ([temptilenum, j + 1, tilenum, i + 1] not in constraints)):
                    constraint = [tilenum, i + 1, temptilenum, j + 1]
                    constraints.append(constraint)


# # vertices will be a dictionary where the keys are coordinates for the vertex
# # and the value is which tile/vertex number the vertex is at
# vertices = {}

# for t in range(len(tile_vertices)):
#     tile = tile_vertices[t]
#     tilenum = t + 1
#     for i in range(len(tile)):
#         vertex = tile[i]
#         # if a matching vertex is already in the dict, remove it and add a constraint between the two matching vertices
#         match = vertices.pop(vertex, None)
#         if match is not None:
#             constraint = [tilenum, i + 1, match[0], match[1] + 1]
#             constraints.append(constraint)
#         # otherwise if no matching vertex in the dict, add vertex to the dict
#         # by storing its coordinates as a key with value (tilenum, i) 
#         else:
#             vertices[vertex] = (tilenum, i)

f = open(out_constraints_file, "x")
for c in constraints:
    for i in c:
        f.write(str(i) + " ")
    f.write("\n")
f.close()

print("Full connection constraints file saved to " + out_constraints_file)
