#!/usr/bin/env python
# coding: utf-8

from ivy.std_api import *
import convertor as c
import patternMatching as pm

IvyInit("agent_convertisseur")
IvyStart()

def on_tabgo(agent):
    """respond to 'tabgo:' messages : start the convertor and search the tabgo sb3"""
    print("Agent %r sent tabgo"%agent)
    c.convert("tabgo", False, 0, 0, 0)

def on_tabgo_printable(agent, text):
    """respond to 'tabgo:' messages : start the convertor and search the tabgo sb3 and give printable svg"""
    print("Agent %r sent on_tabgo_printable"%agent)
    scale = pm.get_scale(text)
    x = pm.get_x(text)
    y = pm.get_y(text)
    c.convert("tabgo", True, scale, x, y)

def print_given(agent, text):
    """respond to 'convert: location= scale= x= y=' messages : start the convertor on the given sb3 and give printable svg"""
    print("Agent %r sent json"%agent)
    location = pm.get_location(text)
    scale = pm.get_scale(text)
    x = pm.get_x(text)
    y = pm.get_y(text)
    c.convert(location, True, scale, x, y)


def on_given(agent, text):
    """respond to 'convert: location=' messages : start the convertor on the given sb3"""
    print("Agent %r sent json"%agent)
    location = pm.get_location(text)
    c.convert(location, False, 0, 0, 0)

IvyBindMsg(on_tabgo, "^tabgo: .*")
IvyBindMsg(on_tabgo_printable, "^print tabgo: .*")
IvyBindMsg(on_given, "^convert:(.*?)location=.*")
IvyBindMsg(print_given, "^print .* convert:(.*?)location=.*")

IvyMainLoop()