import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util

# have simulation file call this
class EventHandler():
    def __init__(self, simulation):
        self.sim = simulation
        self.running = True

    def handle_event(self, event):
        LEFT = 1
        RIGHT = 3

        mpos = pygame.mouse.get_pos()
        p = self.sim.from_pygame(Vec2d(mpos))
        self.sim.mouse.position = p

        if event.type == QUIT:
            self.running = False

        # press p to save a screenshot of the simulation screen
        elif event.type == KEYDOWN and event.key == K_p:
            temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))
            print("Saved a screenshot to " + "kirigami_simulation_" + temp_time + ".png")
            pygame.image.save(self.sim.screen, str("kirigami_simulation_" + temp_time + ".png"))
        
        if event.type == pygame.USEREVENT+1:
            r = random.randint(1,4)
            for body in self.sim.space.bodies[:]:
                body.apply_impulse_at_local_point((-6000,0))
        if event.type == pygame.USEREVENT+2:
            # max_scr = 0
            self.sim.reset()
            
        # press r to reset the pattern to contracted state
        elif event.type == KEYDOWN and event.key == K_r and self.sim.params["IS_INTERACTIVE"]:
            # max_scr = 0
            self.sim.reset()

        # press v to save a file of current vertex locations
        # vertices are saved with the offset/multiplier transformations done earlier for display purposes undone
        elif event.type == KEYDOWN and event.key == K_v and self.sim.params["IS_INTERACTIVE"]:
            temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))
            save_vertices_file = open("kirigami_simulation_vertices" + temp_time + ".txt", "x")
            print("Saved file of current vertices to " + "kirigami_simulation_vertices" + temp_time + ".txt")
            current_vertices = []
            for center in self.sim.center_shapes:
                vertices = map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                        self.sim.height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                center.get_vertices())
                for pos in vertices:
                    save_vertices_file.write(str(round((pos[0] - self.sim.params["X_OFFSET"]) / self.sim.params["VERTEX_MULTIPLIER"], 3)) + " " + str(round(((pos[1] - self.sim.params["Y_OFFSET"]) / self.sim.params["VERTEX_MULTIPLIER"]), 3)) + " ")
                save_vertices_file.write("\n")
            save_vertices_file.close()
            
        elif event.type == MOUSEBUTTONDOWN and self.sim.params["IS_INTERACTIVE"] and event.button == LEFT:
            if self.sim.selected != None:
                self.sim.space.remove(self.sim.selected)
            p = self.sim.from_pygame(Vec2d(event.pos))
            hit = self.sim.space.point_query(p, 0, pm.ShapeFilter())
            if len(hit) > 0:
                shape = hit[-1].shape
                rest_length = self.sim.mouse.position.get_distance(shape.body.position)
                ds = pm.DampedSpring(self.sim.mouse, shape.body, (0,0), (0,0), rest_length, 1000, 10)
                self.sim.space.add(ds)
                self.sim.selected = ds
        
        elif event.type == MOUSEBUTTONDOWN and self.sim.params["IS_INTERACTIVE"] and event.button == RIGHT:
            if self.sim.selected != None:
                self.sim.space.remove(self.sim.selected)
            p = self.sim.from_pygame(Vec2d(event.pos))
            hit = self.sim.space.point_query_nearest(p, 0, pm.ShapeFilter())
            if hit != None:
                q = hit.shape.body
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

        elif event.type == MOUSEBUTTONUP and self.sim.params['IS_INTERACTIVE']:
            if self.sim.selected != None:
                self.sim.space.remove(self.sim.selected)
                self.sim.selected = None