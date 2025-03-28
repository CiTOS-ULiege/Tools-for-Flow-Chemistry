# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:42:47 2024
@author: Hubert
This file is required to allow shared event through all other subprograms.
For example "stop_event" allows gentle termination of all parts of the program.
"""
#events.py

import threading

stop_event = threading.Event()