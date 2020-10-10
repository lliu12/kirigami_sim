# Given a vertices file, constraints file, and one vertex on the outer hull of the deployable pattern,
# Generate a hull file for the pattern's outer hull
# Important: script assumes each vertex is only constrained to one other one
# Also, script is written to search around the hull in a clockwise direction.
# If the starting vertex is constrained to another vertex, moving to that second vertex must be going in the clockwise direction.

# file containing vertices and constraints
# ith row of vertices file should hold coordinates for the ith tile's vertices, in the form x1 y1 x2 y2 ... 
vertices_file = open("info_files/stampfli132_nothinrhombs_vertices.txt")
constraints_file = open("info_files/stampfli132_nothinrhombs_constraints1.txt")

# provide info for a vertex to start at in 1-indexed (TileNum, VertexNum) form
# the script is programmed to move clockwise around the hull
startingpoint_tile = 64
startingpoint_vertex = 3

# provide name of file to write the generated hull to
# to prevent accidental overwriting, this will only work if no file with this path currently exists
out_hull_file = "info_files/stampfli132_nothinrhombs_hull1.txt"

# put info into 0-indexed form and set it as the starting point
current = (startingpoint_tile - 1,startingpoint_vertex - 1)

# read vertices into tile_vertices
tile_vertices = []
for l in (vertices_file.read().splitlines()):
    line = l.split()
    tile_vertices.append([(float(line[i-1]), float(line[i])) 
                          for i in range(len(line)) if i % 2 == 1])
vertices_file.close()

# make a list that stores how many sides each tile has
tile_sides = [len(tile) for tile in tile_vertices]

# read constraints in as tuples of vertices
constraints = []
for l in (constraints_file.read().splitlines()):
    line = l.split()
    constraints.append(((int(line[0]) - 1,int(line[1]) - 1), (int(line[2]) - 1, int(line[3]) - 1)))

constraints_file.close()

hull = [current]

done = False
while not done:
    # check if current vertex is constrained to any other vertex in constraints
    # assumes one vertex can only be constrained to one other one
    next = None
    for c in constraints:
        # if a match is found, get the adjacent vertex on the edge
        if current in c:
            next = c[1 - c.index(current)]
            constraints.remove(c)
            break
    if next is not None:
        current = next
     # if no match is found, move clockwise one vertex around the current tile
    else:
        tile = current[0]
        current = (tile, (current[1] + 1) % tile_sides[tile])
        
    # add new current tile to hull until we are back at the starting vertexe
    if current == (startingpoint_tile - 1, startingpoint_vertex - 1):
        done = True
    else:
        hull.append(current)

# write hull to hull file
f = open(out_hull_file, "x")
for h in hull:
    for i in h:
        f.write(str(i + 1) + " ")
    f.write("\n")
f.close()

print("Hull file saved to " + out_hull_file)