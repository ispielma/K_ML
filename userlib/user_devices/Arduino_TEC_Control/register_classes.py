# -*- coding: utf-8 -*-
"""
Created on Wed May 18 12:58:26 2022

@author: rubidium
"""

import labscript_devices

labscript_devices.register_classes(
    'Arduino_TEC_Control',
    BLACS_tab='user_devices.Arduino_TEC_Control.blacs_tabs.Arduino_TEC_Control_Tab',
    runviewer_parser=None
)