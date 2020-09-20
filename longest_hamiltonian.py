# find longest hamiltonian cycle for deploying a quasicrystal pattern
import math

# file containing vertices within which we'd like to find a hamiltonian cycle 
# (a twelfth, eighth, fifth, etc. portion of the quasicrystal pattern)
# ith row of vertices file should hold coordinates for the ith tile's vertices, in the form x1 y1 x2 y2 ... 
vertices_file = open("info_files/penrose110_fifth_vertices.txt")

# file containing full "wrap around" constraints for the subset 
constraints_file = open("info_files/penrose110_fifth_constraints_dp.txt")

# read vertices into tile_vertices
tile_vertices = []
for l in (vertices_file.read().splitlines()):
    line = l.split()
    tile_vertices.append([(float(line[i-1]), float(line[i])) 
                          for i in range(len(line)) if i % 2 == 1])
vertices_file.close()

# read constraints from txt file into a list where each row has the form:
# [constraint tile 1, vertex number to pin from this tile, constraint tile 2, vertex to pin from this tile]
# subtracts 1 from everything to move to 0-indexing for python
constraints = []
for l in (constraints_file.read().splitlines()):
    line = l.split()
    constraints.append(((int(line[0]) - 1,int(line[1]) - 1), (int(line[2]) - 1, int(line[3]) - 1)))
constraints_file.close()

# type start and end vertices here!
start_vertex = (1,1)
end_vertex = (1, 3)

# program will convert start and vertices to 0-indexed form
start_vertex = (start_vertex[0] - 1, start_vertex[1] - 1)
end_vertex = (end_vertex[0] - 1, end_vertex[1] - 1)

# return list of constraints including possible next connection vertices from the given v, as in vertices in the same position as another vertex of v's tile
# this version returns the whole constraint (so the two vertices in the same location)
def possible_next_vertices_constraints(v, constraints):
    result = []
    for c in constraints:
        if c[0][0] == v[0] and c[0][1] != v[1]:
            result.append(c)
        elif c[1][0] == v[0] and c[1][1] != v[1]:
            result.append(c)
    return result

# return list of just the possible next vertices (so just the vertex that's not in the current tile)
def possible_next_vertices(v, constraints):
    result = []
    for c in constraints:
        if c[0][0] == v[0] and c[0][1] != v[1]:
            result.append(c[1])
        elif c[1][0] == v[0] and c[1][1] != v[1]:
            result.append(c[0])
    return result

# return euclidian distance between two vertex of the form (tilenum, vertex num)
def dist(pp,qq):
    p = tile_vertices[pp[0]][pp[1]]
    q = tile_vertices[qq[0]][qq[1]]
    return math.sqrt((p[0] - q[0])**2 + (p[1] - q[1])**2)

# dicts will be a list of dictionaries where the ith index holds results for all eligible subsets of size i
dicts = [0,0]

# h(set, i) stores (l, v)
# l: length the longest hamiltonian path going through the vertices of set and ending at vertex i; 
# v: the the second to last vertex you should go through to get to i and attain that path
# so that if you then went and looked up, like, h(set - i, v) the result would help you trace back the actual optimal path
h = {}
# for i in possible_next_vertices_constraints(start_vertex, constraints):
#     print(i)
for c in possible_next_vertices_constraints(start_vertex, constraints):
    if (c[0][0] == start_vertex[0]):
        in_current_tile = c[0]
        in_next_tile = c[1]
    else:
        in_current_tile = c[1]
        in_next_tile = c[0]
    h[(frozenset([start_vertex[0], in_next_tile[0]]), in_next_tile)] = (-1 * dist(start_vertex, in_current_tile), start_vertex)
    # print((frozenset([start_vertex[0], in_next_tile[0]]), in_next_tile))
    # print(h[(frozenset([start_vertex[0], in_next_tile[0]]), in_next_tile)])
dicts.append(h)


for n in range(3, 12):
    hh = {}
    # generate all possible path sets of length n by traversing the sets we found of length n-1 and exploring the possible next vertices for them
    for (tiles, last_vertex) in dicts[-1]:
        for v in possible_next_vertices_constraints(last_vertex, constraints):
            if (v[0][0] == last_vertex[0]):
                in_current_tile = v[0]
                in_next_tile = v[1]
            else:
                in_current_tile = v[1]
                in_next_tile = v[0]
            if in_next_tile[0] not in tiles or in_next_tile[0] == start_vertex[0]:
                key = (tiles.union(frozenset([in_next_tile[0]])), in_next_tile)
                if key not in hh:
                    # store in hh
                    hh[key] = (dicts[-1][(tiles, last_vertex)][0] - dist(last_vertex, in_current_tile), last_vertex)
                    # print("new distance added: ", str(-1 * dist(last_vertex, in_current_tile)))
                    # print(last_vertex)
                    # print(v)
                else:
                    # compare this path to the existing min in hh
                    existing_min = hh[key][0]
                    current_vertex_min = dicts[-1][(tiles, last_vertex)][0] - dist(last_vertex, in_current_tile)
                    if current_vertex_min < existing_min:
                        hh[key] = (dicts[-1][(tiles, last_vertex)][0] - dist(last_vertex, cd .in_current_tile), last_vertex)
    dicts.append(hh)
    # print(n)
    # for i in dicts[-1]:
    #     print(i)
    #     print(dicts[-1][i])




# print(dicts[-1][(frozenset([i for i in range(4)]), end_vertex)])
# for i in dicts[-1]:
#     print(i)

# fullset = frozenset(range(len(tile_vertices)))
# return the frozen set with n elements: 0, 1, ..., n-1
def fullset(n):
    return frozenset(range(n))

# print(dicts[5][(fullset(4), end_vertex)])
# print(dicts[4][(frozenset([0,1,2,3]), (1,1))])
# print(dicts[3][(frozenset([0,2,3]), (3,0))])
# print(dicts[2][(frozenset([0,2]), (2,3))])

# given a vertex (x,y), return the vertex (x+1, y+1)
def one_index(vertex):
    return (vertex[0] + 1, vertex[1] + 1)

# start_goal_vertex should be start vertex, t is the set of tiles the path goes through, v is the vertex the path ends at
def follow_path_through(start_goal_vertex, t, v, dicts):
    tiles = frozenset(t) 
    end_vertex = v
    while end_vertex != start_goal_vertex:
        lookup = dicts[len(tiles)][(tiles, end_vertex)]
        # print(tiles, end_vertex)
        # print(lookup)
        print("Vertex: ", str(one_index(end_vertex)))
        print("Distance from start: ", str(lookup[0]))
        tiles = tiles.difference(frozenset([end_vertex[0]]))
        end_vertex = lookup[1]
    print("Vertex: ", str(one_index(end_vertex)))
    print("Distance from start: ", str(lookup[0]))

# follow_path_through(start_vertex, fullset(4), (1,1), dicts)

# print(dicts[6][(frozenset([0,1,2,3,4]), (end_vertex))])
# print(dicts[5][(frozenset([0,1,2,3,4]), ((1,0)))])
# print(dicts[3][(frozenset([0, 4, 7]), (7,3))])
# print(dicts[2][(frozenset([0,4]), (4,3))])
def search_hamiltonian(start_vertex, end_vertex, numtiles, dicts):
    lookup = dicts[numtiles+1][(fullset(numtiles), end_vertex)](1,3)
    # print(lookup)
    print("Vertex: ", str(one_index(end_vertex)))
    print("Distance from start: ", str(lookup[0]))
    follow_path_through(start_vertex, fullset(numtiles), lookup[1], dicts)

# print('6')
# search_hamiltonian(start_vertex, end_vertex, 6, dicts)
# print('7')
# search_hamiltonian(start_vertex, end_vertex, 7, dicts)

print('9')
search_hamiltonian(start_vertex, end_vertex, 9, dicts)
print('10')
search_hamiltonian(start_vertex, end_vertex, 10, dicts)



