#!/usr/bin/env python
# coding: utf-8

from typing import NamedTuple
import array

class Bloc(NamedTuple):
    opcode: str
    parent : str
    next: str
    inputs: array
    fields: array