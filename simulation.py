# simulate tile locations

import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util
import numpy as np
import matplotlib.pyplot as plt
from utils import *

class Simulation(object):
    def __init__(self, tile_vertices, constraints, params, hull_vertices, hull_tiles, damping = .6, iterations = 20, spring_circle_radius = 500):
        self.params = params
        self.space = pm.Space()
        self.space.damping = damping
        self.space.iterations = iterations
        self.mouse = pm.Body(body_type=pm.Body.KINEMATIC)
        self.tile_vertices = tile_vertices 
        self.constraints = constraints
        self.hull_tiles = hull_tiles
        self.hull_vertices = hull_vertices
        self.tile_centers = [get_center(t) for t in tile_vertices]
        self.pattern_center = get_center(self.tile_centers) # calculate center of the whole pattern
        self.selected = None
        self.static_pins = []
        self.max_scr = 1
        self.center_bodies = []
        self.center_shapes = []
        self.tile_pinjoints = []
        self.expansion_springs = []
        self.spring_circle_radius = spring_circle_radius

        self.reset()

        # add bodies and shapes to centers of tiles
        for i in range(len(self.tile_centers)):
            (node_x, node_y) = self.tile_centers[i]
            mass = 10
            moment = pm.moment_for_poly(mass, self.tile_vertices[i])
            body = pm.Body(mass, moment)
            body.position = (node_x, node_y)
            body.start_position = Vec2d(body.position)
            shape = pm.Poly(body, list(map(lambda x:  ((x[0] - node_x) * 1, (x[1] - node_y) * 1), self.tile_vertices[i])))
            shape.elasticity = 0
            self.space.add(body, shape)
            self.center_bodies.append(body)
            self.center_shapes.append(shape)


        # add shapes at vertices that do not generate collisions
        self.vertex_bodies = []
        self.vertex_shapes = []
        for i in range(len(self.tile_vertices)):
            self.vertex_bodies.append([])
            self.vertex_shapes.append([])
            for (node_x, node_y) in self.tile_vertices[i]:
                mass = 1
                radius = 5
                moment = pm.moment_for_circle(mass, 0, radius, (0,0))
                body = pm.Body(mass, moment)
                body.position = (node_x, node_y)
                body.start_position = Vec2d(body.position)
                self.vertex_bodies[-1].append(body)
                shape = pm.Circle(body, 5)
                shape.sensor = True
                self.vertex_shapes[-1].append(shape)
                self.space.add(body, shape)
                pj = pm.PinJoint(self.center_bodies[i], body, (node_x - self.tile_centers[i][0], node_y - self.tile_centers[i][1]), (0,0))
                self.space.add(pj)

        # add kirigami connection pins to link tiles together as specified in constraints
        for c in self.constraints:
            a = self.center_bodies[(c[0])]
            b = self.center_bodies[(c[2])]
            pin = pm.PinJoint(a, b, (self.tile_vertices[(c[0])][(c[1])][0] - a.position.x, self.tile_vertices[(c[0])][(c[1])][1] - a.position.y), (self.tile_vertices[(c[2])][(c[3])][0] - b.position.x, self.tile_vertices[(c[2])][(c[3])][1] - b .position.y))
            self.space.add(pin)
            self.tile_pinjoints.append(pin)

        # if AUTO_EXPAND, add springs pulling hull tiles outward      
        # if self.params['auto_expand'] or self.params['calculate_area_perim']:
        #     if self.hull_info_type == "VERTICES":
        #         self.hull_tiles = list(set(list(zip(*(self.hull_info)))[0]))
        #     elif self.hull_info_type == "TILES":
        #         self.hull_tiles = self.hull_info
        #     else:
        #         assert(False, "invalid hull file type")


        if self.params['auto_expand']:
            for t in self.hull_tiles:
                body = self.center_bodies[t]
                if body.position != self.pattern_center:
                    if not self.params['auto_expand_oblong']:
                        self.spring_anchor_coords = (Vec2d.normalized(body.position - Vec2d(self.pattern_center)) * self.spring_circle_radius) + Vec2d(self.pattern_center) 

                    else: 
                        diff = Vec2d.normalized(body.position - Vec2d(self.pattern_center))
                        if diff.x * diff.y >= 0:
                            stretch_radius = self.spring_circle_radius / 4
                        else:
                            stretch_radius = self.spring_circle_radius / 3
                        self.spring_anchor_coords = (Vec2d.normalized(body.position - Vec2d(self.pattern_center)) * stretch_radius) + Vec2d(self.pattern_center)

                    ds = pm.DampedSpring(body, self.space.static_body, (0,0), self.spring_anchor_coords, 0, self.params['spring_stiffness'], self.params['spring_damping'])
                    self.space.add(ds)
                    self.expansion_springs.append(ds)
                else:
                    print("Auto-Expansion Note: There was a tile center point lying on the pattern center, which the simulation did not attach an expanding spring to.")
        self.reset()

    def reset(self):
        for body in self.space.bodies:
            body.position = Vec2d(body.start_position)
            body.force = 0,0
            body.torque = 0
            body.velocity = 0,0
            body.angular_velocity = 0
            body.angle = 0
        for s in self.static_pins:
            self.space.remove(s)
        self.static_pins.clear()
        color = THECOLORS["lightskyblue1"]
        for shape in self.space.shapes:
            shape.color = color
        self.max_scr = 1

    # def draw_shapes(self):
        # if not self.params['vertices_only']:
        #     for i in range(len(self.center_shapes)):
        #         center = self.center_shapes[i]
        #         (node_x, node_y) = center.body.position
        #         pygame.draw.polygon(self.screen, 
        #                             center.color, 
        #                             list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
        #                                                 self.height - (x.rotated(center.body.angle) + center.body.position)[1]),
        #                                                         center.get_vertices())))
        #         pygame.draw.polygon(self.screen, 
        #                             THECOLORS["lightskyblue2"], 
        #                             list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
        #                                                 self.height - (x.rotated(center.body.angle) + center.body.position)[1]),
        #                                                         center.get_vertices())), 1)

        #         font = pygame.font.Font(None, 16)

        #         # draw in current position (badly)
        #         # self.screen.blit(font.render(str(i + 1), 1, THECOLORS["darkgrey"]), list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
        #         #                                         self.height - (x.rotated(center.body.angle) + center.body.position)[1]),
        #         #                                                 center.get_vertices()))[0])

        #         # draw in initial position
        #         # self.screen.blit(font.render(str(i + 1), 1, THECOLORS["darkgrey"]), [self.tile_centers[i][0], self.height - self.tile_centers[i][1]])


        #         if self.params["calculate_area_perim"]:
        #             pygame.draw.polygon(self.screen, 
        #                                 THECOLORS["lightskyblue3"], 
        #                                 list(map(lambda x: self.to_pygame(x),
        #                                 [self.vertex_bodies[(v[0])][(v[1])].position for v in self.hull_vertices])), 1)

        #     for c in self.space.constraints:
        #         if c in self.expansion_springs:
        #             if self.params["display_expansion_springs"]:
        #                 pv1 = c.a.position + (c.anchor_a).rotated(c.a.angle)
        #                 pv2 = c.b.position + (c.anchor_b).rotated(c.b.angle)
        #                 p1 = self.to_pygame(pv1)
        #                 p2 = self.to_pygame(pv2)
        #                 pygame.draw.aalines(self.screen, THECOLORS["skyblue"], False, [p1,p2]) # remove this line to hide the springs

        #         else:
        #             pv1 = c.a.position + (c.anchor_a).rotated(c.a.angle)
        #             pv2 = c.b.position + (c.anchor_b).rotated(c.b.angle)
        #             p1 = self.to_pygame(pv1)
        #             p2 = self.to_pygame(pv2)
        #             pygame.draw.aalines(self.screen, THECOLORS["skyblue"], False, [p1,p2])
                
        #     for s in self.static_pins:
        #        pygame.draw.circle(self.screen, THECOLORS["royalblue1"], self.to_pygame(s.b.position), 5)

        # if self.params['vertices_only']:
        #     for center in self.center_shapes:
        #         vertices = map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
        #                                                     self.height - (x.rotated(center.body.angle) + center.body.position)[1]),
        #                                                             center.get_vertices())
        #         for pos in vertices:
        #             pygame.draw.circle(self.screen, THECOLORS["black"], pos, 1)

        

    # def to_pygame(self, p):
    #     return int(p.x), int(self.height - p.y)

    # def from_pygame(self, p): 
    #     return self.to_pygame(p)
