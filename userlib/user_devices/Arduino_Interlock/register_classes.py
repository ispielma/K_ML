# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 11:33:52 2022

@author: rubidium
"""

import labscript_devices

labscript_devices.register_classes(
    'Arduino_Interlock',
    BLACS_tab='user_devices.Arduino_Interlock.blacs_tabs.Arduino_Interlock_Tab',
    runviewer_parser=None
)