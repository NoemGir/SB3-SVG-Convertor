#!/usr/bin/env python
# coding: utf-8

from typing import NamedTuple
import array

class Bloc(NamedTuple):
    """A structure capable of stocking all the informations related to a bloc"""
    opcode: str
    parent : str
    next: str
    inputs: array
    fields: array


    