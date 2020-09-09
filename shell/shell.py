#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 14:26:42 2020

@author: calvar13
"""

#! /usr/bin/env python3
import os, sys, re, time

run = True
print("Please enter a command. 'help' returns command formatting help. 'quit' exits the program.") 

while run:
    cmd = input("$ ")
    if cmd == "quit":
        print("Quitting. Thank you!")
        sys.exit(1)
    elif cmd == "help":
        print("\tFormat: [cmd][arg]\n\tquit: 'quit'")
    