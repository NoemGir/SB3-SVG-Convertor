#!/usr/bin/env python
# coding: utf-8

from ivy.std_api import *
import convertor as c

stop = False

IvyInit("agent_convertisseur")
IvyStart()

def on_tabgo(agent):
    print("Agent %r sent tabgo"%agent)
    c.on_tabgo()

def on_sb3(agent):
    print("Agent %r sent sb3"%agent)
    c.on_sb3()

def on_json(agent):
    print("Agent %r sent json"%agent)
    c.on_json()

IvyBindMsg(on_tabgo, "^tabgo: .*")
IvyBindMsg(on_sb3, "^sb3: .*")
IvyBindMsg(on_tabgo, "^json: .*")

IvyMainLoop()









