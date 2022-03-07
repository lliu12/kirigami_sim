# handle user events

import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util

# have simulation file call this
class EventHandler():
    def __init__(self, simulation, screen):
        self.sim = simulation
        self.running = True
        self.screen = screen
        _, self.height = screen.get_size()

    def handle_event(self, event):
        LEFT = 1
        RIGHT = 3

        mpos = pygame.mouse.get_pos()
        p = self.from_pygame(Vec2d(mpos))
        self.sim.mouse.position = p

        if event.type == QUIT:
            self.running = False

        # press p to save a screenshot of the simulation screen
        elif event.type == KEYDOWN and event.key == K_p:
            temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))
            print("Saved a screenshot to " + "kirigami_simulation_" + temp_time + ".png")
            pygame.image.save(self.screen, str("kirigami_simulation_" + temp_time + ".png"))
        
        if event.type == pygame.USEREVENT+1:
            r = random.randint(1,4)
            for body in self.sim.space.bodies[:]:
                body.apply_impulse_at_local_point((-6000,0))
        if event.type == pygame.USEREVENT+2:
            self.sim.reset()
            
        # press r to reset the pattern to contracted state
        elif event.type == KEYDOWN and event.key == K_r and self.sim.params["is_interactive"]:
            self.sim.reset()

        # press v to save a file of current vertex locations
        # vertices are saved with the offset/multiplier transformations done earlier for display purposes undone

        # note: currently can only save one per second
        elif event.type == KEYDOWN and event.key == K_v and self.sim.params["is_interactive"]:
            temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))
            save_vertices_file = open("kirigami_simulation_vertices" + temp_time + ".txt", "x")
            print("Saved file of current vertices to " + "kirigami_simulation_vertices" + temp_time + ".txt")
            current_vertices = []
            for center in self.sim.center_shapes:
                vertices = map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                        (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                center.get_vertices())
                v_list = list(vertices)
                for v in range(len(v_list)):
                    pos = v_list[-v]
                    save_vertices_file.write(str(round((pos[0] - self.sim.params["x_offset"]) / self.sim.params["vertex_multiplier"], 3)) + " " + str(round((pos[1] - self.sim.params["y_offset"]) / self.sim.params["vertex_multiplier"], 3)) + " ")
                save_vertices_file.write("\n")
            save_vertices_file.close()

        # press c to save a file of current locations of tile centers
        elif event.type == KEYDOWN and event.key == K_c and self.sim.params["is_interactive"]:
            temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))
            save_centers_file = open("kirigami_simulation_centers" + temp_time + ".txt", "x")
            print("Saved file of current tile centers to " + "kirigami_simulation_centers" + temp_time + ".txt")
            current_centers = []
            for center in self.sim.center_shapes:
                save_centers_file.write(str(round((center.body.position[0] - self.sim.params["x_offset"]) / self.sim.params["vertex_multiplier"], 3)) + " " + str(round((center.body.position[1] - self.sim.params["y_offset"]) / self.sim.params["vertex_multiplier"], 3)) + "\n")
            save_centers_file.close()

        # left click to drag tiles
        elif event.type == MOUSEBUTTONDOWN and self.sim.params["is_interactive"] and event.button == LEFT:
            if self.sim.selected != None:
                self.sim.space.remove(self.sim.selected)
            p = self.from_pygame(Vec2d(event.pos))
            hit = self.sim.space.point_query(p, 0, pm.ShapeFilter())
            if len(hit) > 0:
                shape = hit[-1].shape
                rest_length = self.sim.mouse.position.get_distance(shape.body.position)
                ds = pm.DampedSpring(self.sim.mouse, shape.body, (0,0), (0,0), rest_length, 1000, 10)
                self.sim.space.add(ds)
                self.sim.selected = ds

        elif event.type == MOUSEBUTTONUP and self.sim.params['is_interactive']:
            if self.sim.selected != None:
                self.sim.space.remove(self.sim.selected)
                self.sim.selected = None

        # right click to pin a tile in place
        elif event.type == MOUSEBUTTONDOWN and self.sim.params["is_interactive"] and event.button == RIGHT:
            if self.sim.selected != None:
                self.sim.space.remove(self.sim.selected)
            p = self.from_pygame(Vec2d(event.pos))
            hit = self.sim.space.point_query(p, 0, pm.ShapeFilter())
            if len(hit) > 0:
                q = hit[0].shape.body
                pinned_already = False
                existing_pin = None
                for a in self.sim.static_pins:
                    if a.b == q:
                        pinned_already = True
                        existing_pin = a
                if pinned_already:
                    self.sim.static_pins.remove(existing_pin)
                    self.sim.space.remove(existing_pin)
                else:
                    pj = pm.PinJoint(self.sim.space.static_body, q, (q.position.x, q.position.y), (0,0))
                    self.sim.space.add(pj)
                    self.sim.static_pins.append(pj)

        # press e to clear placed pins
        elif event.type == KEYDOWN and event.key == K_e and self.sim.params["is_interactive"]:
            if self.sim.selected != None:
                self.sim.space.remove(self.sim.selected)

            for existing_pin in self.sim.static_pins:
                self.sim.static_pins.remove(existing_pin)
                self.sim.space.remove(existing_pin)

    def to_pygame(self, p):
        return int(p.x), int(self.height - p.y)

    def from_pygame(self, p): 
        return self.to_pygame(p)
