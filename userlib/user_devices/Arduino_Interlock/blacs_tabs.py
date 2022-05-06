# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 12:10:25 2022

@author: rubidium

Defines the blacs tab class and GUI for the Arduino_Interlock device
"""

from labscript_devices import BLACS_tab#, runviewer_parser
from blacs.device_base_class import DeviceTab
from blacs.tab_base_classes import define_state
from blacs.tab_base_classes import MODE_MANUAL, MODE_TRANSITION_TO_BUFFERED, MODE_TRANSITION_TO_MANUAL, MODE_BUFFERED  

import os
import sys
import numpy as np
import threading, time
from qtutils import UiLoader#, inmain_decorator
import qtutils.icons
from qtutils.qt import QtWidgets, QtGui, QtCore
from labscript_utils.qtwidgets.toolpalette import ToolPaletteGroup
import pyqtgraph as pg

#@BLACS_tab
class Arduino_Interlock_Tab(DeviceTab):

    def initialise_GUI(self):
         layout = self.get_tab_layout()
         
         # # dds_prop = {}
         # # for i in range(2): # 2 is the number of DDS outputs on this device
         # #     dds_prop['dds %d'%i] = {}
         # #     for subchnl in ['freq', 'amp', 'phase']:
         # #         dds_prop['dds %d'%i][subchnl] = {'base_unit':self.base_units[subchnl],
         # #                                          'min':self.base_min[subchnl],
         # #                                          'max':self.base_max[subchnl],
         # #                                          'step':self.base_step[subchnl],
         # #                                          'decimals':self.base_decimals[subchnl]
         # #                                         }
         # #     dds_prop['dds %d'%i]['gate'] = {}
         
         # interlock_channels = {}
         # for i in range(16): # 12 is the maximum number of flags on this device (some only have 4 though)
         #      interlock_channels['channel %d'%i] = {}
         
         # # Create the output objects    
         # #self.create_dds_outputs(dds_prop)        
         # self.create_digital_outputs(interlock_channels)        
         # # # Create widgets for output objects
         # dds_widgets,ao_widgets,interlock_widgets = self.auto_create_widgets()
         
         # # # Define the sort function for the digital outputs
         # def sort(channel):
         #      flag = channel.replace('channel ','')
         #      flag = int(flag)
         #      return '%02d'%(flag)
         
         # # and auto place the widgets in the UI
         # self.auto_place_widgets(("Channels",interlock_widgets,sort),("Interlock",self.ui))
         
          # Load monitor UI
         ui_filepath = os.path.join(
             os.path.dirname(os.path.realpath(__file__)), 'interlock_chan_buts.ui'
         )
         self.ui = UiLoader().load(ui_filepath)
         
         
        #  ui_control = os.path.join(
        #      os.path.dirname(os.path.realpath(__file__)), 'int_controls_widget.ui'
        #  )
        #  self.ui_con = UiLoader().load(ui_control)

        #  ui_monitor = os.path.join(
        #      os.path.dirname(os.path.realpath(__file__)), 'chan_monitor_widget.ui'
        #  )
        #  self.ui_mon = UiLoader().load(ui_monitor)
     
        #  ui_graph = os.path.join(
        #      os.path.dirname(os.path.realpath(__file__)), 'temp_graph_widget.ui'
        #  )
        #  self.ui_graph = UiLoader().load(ui_graph)

        # # #   and auto place the widgets in the UI
        # #  self.auto_place_widgets(("Interlock Controls",self.ui_con),("Channel Monitor",self.ui_mon),
        # #                          ("Temperature Graph",self.ui_graph))
        #  self.get_tab_layout().addWidget(self.ui_con)
        #  self.get_tab_layout().addWidget(self.ui_mon)
        #  self.get_tab_layout().addWidget(self.ui_graph)
         # layout.addWidget(self.ui)
         
         #self.get_tab_layout().addItem(QSpacerItem(0,0,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding))
         
         scrollArea = QtWidgets.QScrollArea()
         scrollArea.setWidget(self.ui)

         self.numSensors = 16
         self.contin_on = False
         self.shot_read = False
         self.temp_check_flag = False
         self.con_toggle = True
         self.mon_toggle = True
         self.gra_toggle = True
         self.loop_time = 0
         self.set_setpoint_vals = []
         self.adjust = []
         self.setpoint = []
         self.chanBut = []
         self.chanText = []
         self.chanCol = []
         self.chanDisCol = []
         self.chan_tog = [True, True, True, True, True, True, True, True, 
                          True, True, True, True, True, True, True, True]
         
         self.iter_count = 0
         self.max_graph_points = 1440           #maximum points to be saved for temp graphing
         self.plot_temp = np.zeros([17, 1])             #creates an arry of 17 rows with 0s as the entries
         self.plot_start = 0                #begins the plotting time at zero seconds
         
         layout.addWidget(scrollArea)
         self.graph_widget = self.ui.graph_widget

         # define the data
         title = "Temperature Graph"
         # create plot window object
         plt = self.graph_widget 
         plt.showGrid(x = True, y = True)
         plt.addLegend()
         plt.setLabel('left', 'Temperature', units ='degC')
         plt.setLabel('bottom', 'Time', units ='sec')
         plt.setTitle(title)
         self.ch_1_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[0], pen ='r',
                                name ='Ch_1')
         self.ch_2_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[1], pen ='y',
                                name ='Ch_2')
         self.ch_3_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[2], pen ='g',
                                name ='Ch_3')
         self.ch_4_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[3], pen ='c',
                                name ='Ch_4')
         self.ch_5_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[4], pen =[20, 141, 255],
                                name ='Ch_5')
         self.ch_9_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[8], pen =[248, 187, 208],
                                name ='Ch_9')
         self.ch_10_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[9], pen =[184, 104, 200],
                                name ='Ch_10')
         self.ch_11_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[10], pen =[255, 136, 0],
                                name ='Ch_11')
         self.ch_12_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[11], pen =[204, 255, 144],
                                name ='Ch_12')
         self.ch_13_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[12], pen =[215, 204, 200],
                                name ='Ch_13')
         self.ch_16_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[15], pen =[250, 250, 250],
                                name ='Ch_16')
         
         
         chan1Text = ("\u0332".join(" Chan 1 "))
         self.ui.channel_1_button.setText("%s \n 0.00 C" %(chan1Text))
         #self.Chan1Col = "red"
         self.Chan1Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 0, 0, 255), stop:1 rgba(255, 0, 0, 255))"
         self.ui.channel_1_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan1Col))
         chan2Text = ("\u0332".join(" Chan 2 "))
         self.ui.channel_2_button.setText("%s \n 0.00 C" %(chan2Text))
         #self.Chan2Col = "yellow"
         self.Chan2Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 220, 0, 255), stop:1 rgba(255, 255, 0, 255))"
         self.ui.channel_2_button.setStyleSheet("background-color : %s;"
                                                "bacjground-style: gradient;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan2Col))
         chan3Text = ("\u0332".join(" Chan 3 "))
         self.ui.channel_3_button.setText("%s \n 0.00 C" %(chan3Text))
         #self.Chan3Col = "lime"
         self.Chan3Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(0, 220, 0, 255), stop:1 rgba(0, 255, 0, 255))"
         self.ui.channel_3_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan3Col))
         chan4Text = ("\u0332".join(" Chan 4 "))
         self.ui.channel_4_button.setText("%s \n 0.00 C" %(chan4Text))
         #self.Chan4Col = "cyan"
         self.Chan4Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(0, 220, 220, 255), stop:1 rgba(0, 255, 255, 255))"
         self.ui.channel_4_button.setStyleSheet("background-color : %s;" 
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan4Col))
         chan5Text = ("\u0332".join(" Chan 5 "))
         self.ui.channel_5_button.setText("%s \n 0.00 C" %(chan5Text))
         #self.Chan5Col = "#148dff" #blue
         self.Chan5Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(17, 122, 220, 255), stop:1 rgba(20, 141, 255, 255))"
         self.ui.channel_5_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan5Col))
         chan9Text = ("\u0332".join(" Chan 9 "))
         self.ui.channel_9_button.setText("%s \n 0.00 C" %(chan9Text))
         #self.Chan9Col = "#f8bbd0" #pink
         self.Chan9Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(218, 165, 184, 255), stop:1 rgba(248, 187, 208, 255))"
         self.ui.channel_9_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan9Col))
         chan10Text = ("\u0332".join(" Chan 10 "))
         self.ui.channel_10_button.setText("%s \n 0.00 C" %(chan10Text))
         #self.Chan10Col = "#b868c8" #violet
         self.Chan10Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(163, 92, 177, 255), stop:1 rgba(184, 104, 200, 255))"
         self.ui.channel_10_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan10Col))
         chan11Text = ("\u0332".join(" Chan 11 "))
         self.ui.channel_11_button.setText("%s \n 0.00 C" %(chan11Text))
         #self.Chan11Col = "#ff8800" #orange
         self.Chan11Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 117, 0, 255), stop:1 rgba(255, 136, 0, 255))"
         self.ui.channel_11_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan11Col))
         chan12Text = ("\u0332".join(" Chan 12 "))
         self.ui.channel_12_button.setText("%s \n 0.00 C" %(chan12Text))
         #self.Chan12Col = "#b3ffcb" #mint-green
         self.Chan12Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(155, 220, 174, 255), stop:1 rgba(179, 255, 203, 255))"
         self.ui.channel_12_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan12Col))
         chan13Text = ("\u0332".join(" Chan 13 "))
         self.ui.channel_13_button.setText("%s \n 0.00 C" %(chan13Text))
         #self.Chan13Col = "#d7ccc8" #tan
         self.Chan13Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(189, 180, 177, 255), stop:1 rgba(215, 204, 200, 255))"
         self.ui.channel_13_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan13Col))
         chan16Text = ("\u0332".join(" Chan 16 "))
         self.ui.channel_16_button.setText("%s \n 0.00 C" %(chan16Text))
         #self.Chan16Col = "#fafafa" #white
         self.Chan16Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(216, 216, 216, 255), stop:1 rgba(250, 250, 250, 255))"
         self.ui.channel_16_button.setStyleSheet("background-color : %s;"
                                                "border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: gray;"
                                                "border-radius: 3px"
                                                %(self.Chan16Col))
         
         
         # # Connect signals for buttons
         self.ui.interlock_controls.clicked.connect(self.interlock_controls_clicked)
         self.ui.channel_monitor.clicked.connect(self.channel_monitor_clicked)
         self.ui.temp_graph.clicked.connect(self.temp_graph_clicked)
         
         self.ui.digital_lock.clicked.connect(self.lock_clicked)    
         self.ui.digital_reset.clicked.connect(self.reset_clicked)
         
         self.ui.call_temps.clicked.connect(self.temp_callout)
         self.ui.update_temps.clicked.connect(self.temp_update_clicked)
         self.ui.zero_temps.clicked.connect(self.temp_zero)
         
         self.ui.start_continuous.clicked.connect(self.on_const_temps)
         self.ui.stop_continuous.clicked.connect(self.off_const_temps)
         
         self.ui.show_setpoints.clicked.connect(self.show_setpoints_clicked)
         self.ui.hide_setpoints.clicked.connect(self.hide_setpoints_clicked)
        
         self.ui.set_setpoints.clicked.connect(self.set_setpoints_clicked)
         #self.ui.send_setpoints.clicked.connect(self.send_setpoints_clicked)
         self.ui.default_setpoints.clicked.connect(self.default_setpoints_clicked)
         self.ui.release_setpoints.clicked.connect(self.release_setpoints_clicked)
         
         self.ui.status_update.clicked.connect(self.status_update_clicked)
         
         self.ui.channel_1_button.clicked.connect(self.channel_1_clicked)
         self.ui.channel_2_button.clicked.connect(self.channel_2_clicked)
         self.ui.channel_3_button.clicked.connect(self.channel_3_clicked)
         self.ui.channel_4_button.clicked.connect(self.channel_4_clicked)
         self.ui.channel_5_button.clicked.connect(self.channel_5_clicked)
         self.ui.channel_9_button.clicked.connect(self.channel_9_clicked)
         self.ui.channel_10_button.clicked.connect(self.channel_10_clicked)
         self.ui.channel_11_button.clicked.connect(self.channel_11_clicked)
         self.ui.channel_12_button.clicked.connect(self.channel_12_clicked)
         self.ui.channel_13_button.clicked.connect(self.channel_13_clicked)
         self.ui.channel_16_button.clicked.connect(self.channel_16_clicked)
         
         self.ui.chan_1_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_2_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_3_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_4_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_5_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_6_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_7_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_8_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_9_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_10_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_11_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_12_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_13_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_14_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_15_adjust.editingFinished.connect(self.send_setpoint_set)
         self.ui.chan_16_adjust.editingFinished.connect(self.send_setpoint_set)
         
         #Sets icons for start and stop continuous
         self.ui.start_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control'))
         self.ui.start_continuous.setToolTip('Starts Automatic Updating of Temperatures, Graph, and Status')
         self.ui.stop_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control-stop-square'))
         self.ui.stop_continuous.setToolTip('Ends Automatic Updating of Temperatures, Graph, and Status')
         self.ui.interlock_controls.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.interlock_controls.setToolTip('Click to hide')
         self.ui.channel_monitor.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.channel_monitor.setToolTip('Click to hide')
         self.ui.temp_graph.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.temp_graph.setToolTip('Click to hide')
    
         #Adds the channel buttons as items in a list for convenient calling
         self.chanBut.append(self.ui.channel_1_button)
         self.chanBut.append(self.ui.channel_2_button)
         self.chanBut.append(self.ui.channel_3_button)
         self.chanBut.append(self.ui.channel_4_button)
         self.chanBut.append(self.ui.channel_5_button)
         self.chanBut.append(self.ui.channel_6_marker)
         self.chanBut.append(self.ui.channel_7_marker)
         self.chanBut.append(self.ui.channel_8_marker)
         self.chanBut.append(self.ui.channel_9_button)
         self.chanBut.append(self.ui.channel_10_button)
         self.chanBut.append(self.ui.channel_11_button)
         self.chanBut.append(self.ui.channel_12_button)
         self.chanBut.append(self.ui.channel_13_button)
         self.chanBut.append(self.ui.channel_14_marker)
         self.chanBut.append(self.ui.channel_15_marker)
         self.chanBut.append(self.ui.channel_16_button)
         
         #Adds the channel colors as items in a list for convenient calling
         self.chanCol.append(self.Chan1Col)
         self.chanCol.append(self.Chan2Col)
         self.chanCol.append(self.Chan3Col)
         self.chanCol.append(self.Chan4Col)
         self.chanCol.append(self.Chan5Col)
         self.chanCol.append("")
         self.chanCol.append("")
         self.chanCol.append("")
         self.chanCol.append(self.Chan9Col)
         self.chanCol.append(self.Chan10Col)
         self.chanCol.append(self.Chan11Col)
         self.chanCol.append(self.Chan12Col)
         self.chanCol.append(self.Chan13Col)
         self.chanCol.append("")
         self.chanCol.append("")
         self.chanCol.append(self.Chan16Col)
         
         #Adds the channel disabled colors as items in a list for convenient calling
         self.chanDisCol.append("#8c0000")
         self.chanDisCol.append("#9a9a00")
         self.chanDisCol.append("#008800")
         self.chanDisCol.append("#009999")
         self.chanDisCol.append("#094175")
         self.chanDisCol.append("")
         self.chanDisCol.append("")
         self.chanDisCol.append("")
         self.chanDisCol.append("#987380")
         self.chanDisCol.append("#673a70")
         self.chanDisCol.append("#a35700")
         self.chanDisCol.append("#6ba66f")
         self.chanDisCol.append("#746e6c")
         self.chanDisCol.append("")
         self.chanDisCol.append("")
         self.chanDisCol.append("#adadad")
         
         #Adds the channel names as items in a list for convenient calling
         self.chanText.append(chan1Text)
         self.chanText.append(chan2Text)
         self.chanText.append(chan3Text)
         self.chanText.append(chan4Text)
         self.chanText.append(chan5Text)
         self.chanText.append("\u0332".join(" Chan 6 "))
         self.chanText.append("\u0332".join(" Chan 7 "))
         self.chanText.append("\u0332".join(" Chan 8 "))
         self.chanText.append(chan9Text)
         self.chanText.append(chan10Text)
         self.chanText.append(chan11Text)
         self.chanText.append(chan12Text)
         self.chanText.append(chan13Text)
         self.chanText.append("\u0332".join(" Chan 14 "))
         self.chanText.append("\u0332".join(" Chan 15 "))
         self.chanText.append(chan16Text)    
         
         self.chanBut[5].setText("%s \n 0.00 C" %(self.chanText[5]))
         self.chanBut[6].setText("%s \n 0.00 C" %(self.chanText[6]))
         self.chanBut[7].setText("%s \n 0.00 C" %(self.chanText[7]))
         self.chanBut[13].setText("%s \n 0.00 C" %(self.chanText[13]))
         self.chanBut[14].setText("%s \n 0.00 C" %(self.chanText[14]))
         
         #Adds the temperature setpoint labels as items in a list for convenient calling
         # self.setpoint.append(self.ui.chan_1_setpoint)
         # self.setpoint.append(self.ui.chan_2_setpoint)
         # self.setpoint.append(self.ui.chan_3_setpoint)
         # self.setpoint.append(self.ui.chan_4_setpoint)
         # self.setpoint.append(self.ui.chan_5_setpoint)
         # self.setpoint.append(self.ui.chan_6_setpoint)
         # self.setpoint.append(self.ui.chan_7_setpoint)
         # self.setpoint.append(self.ui.chan_8_setpoint)
         # self.setpoint.append(self.ui.chan_9_setpoint)
         # self.setpoint.append(self.ui.chan_10_setpoint)
         # self.setpoint.append(self.ui.chan_11_setpoint)
         # self.setpoint.append(self.ui.chan_12_setpoint)
         # self.setpoint.append(self.ui.chan_13_setpoint)
         # self.setpoint.append(self.ui.chan_14_setpoint)
         # self.setpoint.append(self.ui.chan_15_setpoint)
         # self.setpoint.append(self.ui.chan_16_setpoint)
         
         # #Sets initial setpoint values in the ui to -
         # for ch in range(self.numSensors):
         #     self.setpoint[ch].setText(' - ') 
         
         #Adds the setpoint spinboxes as items to the list self.adjust
         self.adjust.append(self.ui.chan_1_adjust)
         self.adjust.append(self.ui.chan_2_adjust)
         self.adjust.append(self.ui.chan_3_adjust)
         self.adjust.append(self.ui.chan_4_adjust)
         self.adjust.append(self.ui.chan_5_adjust)
         self.adjust.append(self.ui.chan_6_adjust)
         self.adjust.append(self.ui.chan_7_adjust)
         self.adjust.append(self.ui.chan_8_adjust)
         self.adjust.append(self.ui.chan_9_adjust)
         self.adjust.append(self.ui.chan_10_adjust)
         self.adjust.append(self.ui.chan_11_adjust)
         self.adjust.append(self.ui.chan_12_adjust)
         self.adjust.append(self.ui.chan_13_adjust)
         self.adjust.append(self.ui.chan_14_adjust)
         self.adjust.append(self.ui.chan_15_adjust)
         self.adjust.append(self.ui.chan_16_adjust)
         
         #Sets the range of the interlock setpoint spinboxes
         for ch in range(self.numSensors):
             self.adjust[ch].setRange(0,150)             

         #Sets the range of the interlock setpoint spinboxes
         for ch in range(self.numSensors):
             self.set_setpoint_vals.append(0) 

         #hides the setpoints initially
         self.ui.hide_setpoints.hide()
         self.ui.setpoints_label_1.hide()
         self.ui.setpoints_label_2.hide()
         for ch in range(self.numSensors):
             self.adjust[ch].hide()
         
         #hides the setpoint adjust spinboxes and buttons initially
         #self.ui.send_setpoints.hide()
         self.ui.default_setpoints.hide()
         self.ui.release_setpoints.hide()
         for ch in range(self.numSensors):
             self.adjust[ch].hide()
         
         self.ui.status_symbol.hide()
         self.ui.status_message.hide()
         self.ui.stop_continuous.hide()
         self.ui.push_widg.hide()
         
         #since labels have no attribute "label.setIcon", create a pixelmap of the desired icon and set pixelmap 
         icon = QtGui.QIcon(':/qtutils/fugue/question')
         pixmap = icon.pixmap(QtCore.QSize(16, 16))
         self.ui.status_icon.setPixmap(pixmap)


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def interlock_controls_clicked(self, button):
        if self.con_toggle:
            self.ui.control_box.hide()
            self.con_toggle = False
            self.ui.interlock_controls.setToolTip('Click to show')
        else:
            self.ui.control_box.show()
            self.con_toggle = True
            self.ui.interlock_controls.setToolTip('Click to hide')


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_monitor_clicked(self, button):
        if self.mon_toggle:
            self.ui.monitor_box.hide()
            self.mon_toggle = False
            self.ui.channel_monitor.setToolTip('Click to show')
        else:
            self.ui.monitor_box.show()
            self.mon_toggle = True
            self.ui.channel_monitor.setToolTip('Click to hide')
       

    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def temp_graph_clicked(self, button):
        if self.gra_toggle:
            self.ui.graph_widget.hide()
            self.ui.push_widg.show()
            self.gra_toggle = False
            self.ui.temp_graph.setToolTip('Click to show')
        else:
            self.ui.graph_widget.show()
            self.ui.push_widg.hide()
            self.gra_toggle = True
            self.ui.temp_graph.setToolTip('Click to hide')      
         
         #self.supports_smart_programming(self.use_smart_programming) 

    #grabs the initial packet from the arduino (grabs all channel temperatures, setpoints, and the interlock status)
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)
    def initial_grab(self):
        temp_init, set_init, stat_init = yield(self.queue_work(self._primary_worker,'initial_packet'))
        for ch in range(self.numSensors):
             chName = ch+1
             self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_init[str(chName)]))
             self.adjust[ch].setValue(set_init[str(chName)])
            

    def initialise_workers(self):
        worker_initialisation_kwargs = self.connection_table.find_by_name(self.device_name).properties
        worker_initialisation_kwargs['addr'] = self.BLACS_connection
        self.create_worker(
            'main_worker',
            'user_devices.Arduino_Interlock.blacs_workers.Arduino_Interlock_Worker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'

        self.on_const_temps()

    def plot(self, time, temp):    
        self.graph_widget.plot(time, temp)


    # @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    # def interlock_controls_clicked(self, button):
    #     if self.con_toggle:
    #         self.ui.control_box.hide()
    #         self.con_toggle = False
    #         self.ui.interlock_controls.setToolTip('Click to show')
    #     else:
    #         self.ui.control_box.show()
    #         self.con_toggle = True
    #         self.ui.interlock_controls.setToolTip('Click to hide')


    # @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    # def channel_monitor_clicked(self, button):
    #     if self.mon_toggle:
    #         self.ui.monitor_box.hide()
    #         self.mon_toggle = False
    #         self.ui.channel_monitor.setToolTip('Click to show')
    #     else:
    #         self.ui.monitor_box.show()
    #         self.mon_toggle = True
    #         self.ui.channel_monitor.setToolTip('Click to hide')
       

    # @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    # def temp_graph_clicked(self, button):
    #     if self.gra_toggle:
    #         self.ui.graph_widget.hide()
    #         self.ui.push_widg.show()
    #         self.gra_toggle = False
    #         self.ui.temp_graph.setToolTip('Click to show')
    #     else:
    #         self.ui.graph_widget.show()
    #         self.ui.push_widg.hide()
    #         self.gra_toggle = True
    #         self.ui.temp_graph.setToolTip('Click to hide')
             
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def lock_clicked(self, button):
        #self.ui.digital_lock.setEnabled(False)
        print('Attempting to lock...')
        lock_stat = yield(self.queue_work(self._primary_worker,'toggle_lock'))
        print(lock_stat)
        if lock_stat == "Digital Interlock Trigger... Stopping system!" or lock_stat == "System is already triggered... Digital Lock activated!":
            self.ui.digital_lock.setText('Unlock')
            # # self.ui.digital_lock.setStyleSheet("border-style: solid;"
            # #                                    "border-width: 2px;"
            # #                                    "border-color: red;"
            # #                                    "border-radius: 3px"
            # #                                    )
            # self.ui.digital_lock.setStyleSheet("* {background: qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 0, 0, 255), stop:1 rgba(255, 0, 0, 255));"
            #                                     "border-style: solid;"
            #                                     "border-width: 1px;"
            #                                     "border-color: gray;"
            #                                     "border-radius: 5px;}"
            #                                     )
            # #self.ui.digital_lock.setStyleSheet("* {color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));"
            # #           "background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 cyan, stop:1 blue);}")
        else:
            self.ui.digital_lock.setText('Lock')
            self.ui.digital_lock.setStyleSheet("")
            # self.ui.digital_reset.setStyleSheet("* {background: qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(230, 0, 0, 255), stop:1 rgba(255, 0, 0, 255));"
            #                                     "border-style: solid;"
            #                                     "border-width: 1px;"
            #                                     "border-color: gray;"
            #                                     "border-radius: 5px;}"
            #                                     )
        
            
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def reset_clicked(self, button):
        print('Attempting to Reset...')
        yield(self.queue_work(self._primary_worker,'push_reset'))
        
        self.ui.digital_reset.setStyleSheet("")                                     
    
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def temp_update_clicked(self, button):
        self.grab_temp_update()


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def status_update_clicked(self, button):
        self.grab_status_update()


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def show_setpoints_clicked(self, button):
        self.ui.show_setpoints.hide()
        self.ui.hide_setpoints.show()
        self.ui.setpoints_label_1.show()
        self.ui.setpoints_label_2.show()
        self.grab_setpoints()
        for ch in range(self.numSensors):
            self.adjust[ch].show()
        
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def hide_setpoints_clicked(self, button):
        self.ui.show_setpoints.show()
        self.ui.hide_setpoints.hide()
        self.ui.setpoints_label_1.hide()
        self.ui.setpoints_label_2.hide()
        for ch in range(self.numSensors):
            self.adjust[ch].hide()


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def set_setpoints_clicked(self, button):
        self.ui.show_setpoints.hide()
        self.ui.hide_setpoints.hide()
        self.ui.set_setpoints.hide()
        #self.ui.send_setpoints.show()
        self.ui.default_setpoints.show()
        self.ui.release_setpoints.show()
        self.grab_setpoints()
        
        self.ui.setpoints_label_1.show()
        self.ui.setpoints_label_2.show()
        
        for ch in range(self.numSensors):
            # self.setpoint[ch].hide()
            self.adjust[ch].show()


    # @define_state(MODE_MANUAL, True)      
    # def send_setpoints_clicked(self, button):
    #     self.ui.show_setpoints.hide()
    #     self.ui.hide_setpoints.show()
    #     self.ui.set_setpoints.show()
    #     self.ui.send_setpoints.hide()
    #     self.ui.default_setpoints.hide()
    #     self.ui.release_setpoints.hide()
    #     self.ui.setpoints_label_1.show()
    #     self.ui.setpoints_label_2.show()
        
    #     self.grab_new_setpoints()
    #     self.send_new_setpoints()
    #     self.grab_setpoints()

    #     for ch in range(self.numSensors):
    #         self.adjust[ch].hide() 
    #         self.setpoint[ch].show()


    @define_state(MODE_MANUAL, True)      
    def send_setpoint_set(self, button=0):
        self.grab_new_setpoints()
        self.send_new_setpoints()



    @define_state(MODE_MANUAL, True)      
    def default_setpoints_clicked(self, button):
        self.ui.show_setpoints.hide()
        self.ui.hide_setpoints.show()
        self.ui.set_setpoints.show()
        #self.ui.send_setpoints.hide()
        self.ui.default_setpoints.hide()
        self.ui.release_setpoints.hide()
        self.ui.setpoints_label_1.show()
        self.ui.setpoints_label_2.show()
        
        self.send_default_setpoints()
        self.grab_setpoints()

        for ch in range(self.numSensors):
            self.adjust[ch].show() 
            #self.setpoint[ch].show()        
        
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def release_setpoints_clicked(self, button):
        self.ui.show_setpoints.hide()
        self.ui.hide_setpoints.show()
        self.ui.set_setpoints.show()
        #self.ui.send_setpoints.hide()
        self.ui.default_setpoints.hide()
        self.ui.release_setpoints.hide()
        self.ui.setpoints_label_1.hide()
        self.ui.setpoints_label_2.hide()
        self.grab_setpoints()

        for ch in range(self.numSensors):
            self.adjust[ch].hide() 
            #self.setpoint[ch].show()


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_1_clicked(self, button):
        if self.chan_tog[0]:
            self.chan_tog[0] = False
            self.ch_1_ref.setData([],[])
            self.ui.channel_1_button.setStyleSheet("background-color : #8c0000;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_1_button.setToolTip('Click to Show on Graph')                                                   
        else:
            self.chan_tog[0] = True
            self.ch_1_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[0, 0:self.iter_count-1])
            self.ui.channel_1_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan1Col))
            self.ui.channel_1_button.setToolTip('Click to Hide from Graph')
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_2_clicked(self, button):
        if self.chan_tog[1]:
            self.chan_tog[1] = False
            self.ch_2_ref.setData([],[])
            self.ui.channel_2_button.setStyleSheet("background-color : #9a9a00;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_2_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[1] = True
            self.ch_2_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[1, 0:self.iter_count-1])    
            self.ui.channel_2_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan2Col))
            self.ui.channel_2_button.setToolTip('Click to Hide from Graph')
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_3_clicked(self, button):
        if self.chan_tog[2]:
            self.chan_tog[2] = False
            self.ch_3_ref.setData([],[])
            self.ui.channel_3_button.setStyleSheet("background-color : #008800;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_3_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[2] = True
            self.ch_3_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[2, 0:self.iter_count-1])    
            self.ui.channel_3_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan3Col))
            self.ui.channel_3_button.setToolTip('Click to Hide from Graph')
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_4_clicked(self, button):
        if self.chan_tog[3]:
            self.chan_tog[3] = False
            self.ch_4_ref.setData([],[])
            self.ui.channel_4_button.setStyleSheet("background-color : #009999;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_4_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[3] = True
            self.ch_4_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[3, 0:self.iter_count-1]) 
            self.ui.channel_4_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan4Col))
            self.ui.channel_4_button.setToolTip('Click to Hide from Graph')
    
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_5_clicked(self, button):
        if self.chan_tog[4]:
            self.chan_tog[4] = False
            self.ch_5_ref.setData([],[])
            self.ui.channel_5_button.setStyleSheet("background-color : #094175;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_5_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[4] = True
            self.ch_5_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[4, 0:self.iter_count-1])    
            self.ui.channel_5_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan5Col))
            self.ui.channel_5_button.setToolTip('Click to Hide from Graph')
            
            
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_9_clicked(self, button):
        if self.chan_tog[8]:
            self.chan_tog[8] = False
            self.ch_9_ref.setData([],[])
            self.ui.channel_9_button.setStyleSheet("background-color : #987380;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_9_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[8] = True
            self.ch_9_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[8, 0:self.iter_count-1])  
            self.ui.channel_9_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan9Col))
            self.ui.channel_9_button.setToolTip('Click to Hide from Graph')


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_10_clicked(self, button):
        if self.chan_tog[9]:
            self.chan_tog[9] = False
            self.ch_10_ref.setData([],[])
            self.ui.channel_10_button.setStyleSheet("background-color : #673a70;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_10_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[9] = True
            self.ch_10_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[9, 0:self.iter_count-1])  
            self.ui.channel_10_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan10Col))
            self.ui.channel_10_button.setToolTip('Click to Hide from Graph')


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_11_clicked(self, button):
        if self.chan_tog[10]:
            self.chan_tog[10] = False
            self.ch_11_ref.setData([],[])
            self.ui.channel_11_button.setStyleSheet("background-color : #a35700;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_11_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[10] = True
            self.ch_11_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[10, 0:self.iter_count-1])  
            self.ui.channel_11_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan11Col))
            self.ui.channel_11_button.setToolTip('Click to Hide from Graph')

            
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_12_clicked(self, button):
        if self.chan_tog[11]:
            self.chan_tog[11] = False
            self.ch_12_ref.setData([],[])
            self.ui.channel_12_button.setStyleSheet("background-color : #6ba66f;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_12_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[11] = True
            self.ch_12_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[11, 0:self.iter_count-1])  
            self.ui.channel_12_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan12Col))
            self.ui.channel_12_button.setToolTip('Click to Hide from Graph')
            
            
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_13_clicked(self, button):
        if self.chan_tog[12]:
            self.chan_tog[12] = False
            self.ch_13_ref.setData([],[])
            self.ui.channel_13_button.setStyleSheet("background-color : #746e6c;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_13_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[12] = True
            self.ch_13_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[12, 0:self.iter_count-1])  
            self.ui.channel_13_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan13Col))
            self.ui.channel_13_button.setToolTip('Click to Hide from Graph')


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_16_clicked(self, button):
        if self.chan_tog[15]:
            self.chan_tog[15] = False
            self.ch_16_ref.setData([],[])
            self.ui.channel_16_button.setStyleSheet("background-color : #adadad;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            self.ui.channel_16_button.setToolTip('Click to Show on Graph')
        else:
            self.chan_tog[15] = True
            self.ch_16_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[15, 0:self.iter_count-1])  
            self.ui.channel_16_button.setStyleSheet("background-color : %s;" "border-style: solid;"
                            "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(self.Chan16Col))
            self.ui.channel_16_button.setToolTip('Click to Hide from Graph')            

    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_temp_update(self):
        print('Attempting to Grab Temperatures...')
        temp_up = yield(self.queue_work(self._primary_worker,'new_temps'))
        for ch in range(self.numSensors):
            chName = ch+1
            self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_up[str(chName)]))
        
    
    @define_state(MODE_TRANSITION_TO_MANUAL,True)      
    def temp_shot_update(self):
        print('Attempting to Grab Temperatures...')
        temp_up = yield(self.queue_work(self._primary_worker,'temp_return'))
        for ch in range(self.numSensors):
            chName = ch+1
            self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_up[str(chName)]))
    
    # @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    # def status_update_clicked(self, button):
    #     #self.ui.digital_reset.setEnabled(False)
    #     self.grab_status_update()
        
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_status_update(self):
        print('Updating Interlock Status...')
        stat_up = yield(self.queue_work(self._primary_worker,'new_stat'))
        intlock_trigger = str(stat_up[0])[0:4]
        if intlock_trigger == "Fals":
            icon = QtGui.QIcon(':/qtutils/fugue/tick-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
        elif intlock_trigger == "True":
            icon = QtGui.QIcon(':/qtutils/fugue/cross-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            stat_mess = str(stat_up[1])
            if stat_mess == "flow1":
                self.ui.status_message.setText("Check Flowmeter 1")
            elif stat_mess == "flow2":
                self.ui.status_message.setText("Check Flowmeter 2")
            elif stat_mess == "DigiL":
                self.ui.status_message.setText("Check Digital Lock")
                self.ui.digital_lock.setStyleSheet("background-color : red;" "border-style: solid;"
                                                       "border-width: 1px;" "border-color: gray;" "border-radius: 3px")
            elif stat_mess == "HighT":
                self.ui.status_message.setText("Check Temperatures")
            elif stat_mess == "React":
                self.ui.status_message.setText("Push Reset")
                self.ui.digital_reset.setText("RESET!")
            mess_icon = QtGui.QIcon(':/qtutils/fugue/exclamation')
            mess_pixmap = mess_icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_symbol.setPixmap(mess_pixmap)
            self.ui.status_symbol.show()
            self.ui.status_message.show()
        else:
            icon = QtGui.QIcon(':/qtutils/fugue/question')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_update.setText('%s' %(intlock_trigger))
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
    
    @define_state(MODE_TRANSITION_TO_MANUAL,True)      
    def stat_shot_update(self):
        print('Updating Interlock Status...')
        stat_up = yield(self.queue_work(self._primary_worker,'stat_return'))
        intlock_trigger = str(stat_up[0])[0:4]
        if intlock_trigger == "Fals":
            icon = QtGui.QIcon(':/qtutils/fugue/tick-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
        elif intlock_trigger == "True":
            icon = QtGui.QIcon(':/qtutils/fugue/cross-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            stat_mess = str(stat_up[1])
            if stat_mess == "flow1":
                self.ui.status_message.setText("Check Flowmeter 1")
            elif stat_mess == "flow2":
                self.ui.status_message.setText("Check Flowmeter 2")
            elif stat_mess == "DigiL":
                self.ui.status_message.setText("Check Digital Lock")
            elif stat_mess == "HighT":
                self.ui.status_message.setText("Check Temperatures")
            elif stat_mess == "React":
                self.ui.status_message.setText("Press Reset")
            mess_icon = QtGui.QIcon(':/qtutils/fugue/exclamation')
            mess_pixmap = mess_icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_symbol.setPixmap(mess_pixmap)
            self.ui.status_symbol.show()
            self.ui.status_message.show()
        else:
            icon = QtGui.QIcon(':/qtutils/fugue/question')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_update.setText('%s' %(intlock_trigger))
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
 
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_setpoints(self):
        print('Attempting to Grab Setpoints...')
        set_update = yield(self.queue_work(self._primary_worker,'new_setpoints'))
        for ch in range(self.numSensors):
            chName = ch+1
            #self.setpoint[ch].setText('%s C' %(set_update[str(chName)]))
        
        for ch in range(self.numSensors):
            chName = ch+1
            self.adjust[ch].setValue(set_update[str(chName)])

        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_new_setpoints(self):
        print('Compiling New Setpoints...')
        
        #set_update = yield(self.queue_work(self._primary_worker,'new_setpoints'))
        for ch in range(self.numSensors):
            # chName = ch+1
            # set_value = self.adjust[ch].value()
            # self.set_setpoint_vals[str(chName)] = set_value
            # return self.set_setpoint_vals
            set_value = self.adjust[ch].value()
            self.set_setpoint_vals[ch]=set_value
        
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_new_setpoints(self):
        print('Sending New Setpoints...')
        set_send = yield(self.queue_work(self._primary_worker,'set_setpoints', self.set_setpoint_vals))
           

    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_default_setpoints(self):
        print('Sending New Setpoints...')
        yield(self.queue_work(self._primary_worker,'set_default_setpoints'))


    # @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)
    # def initial_grab(self):
    #     yield(self.queue_work(self._primary_worker,'initial_packet'))

    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_packet_update(self):
        print('Attempting to Grab Temperatures and Status...')
        temp_up, sets_up, stat_up = yield(self.queue_work(self._primary_worker,'new_packet', verbose = False))
        for ch in range(self.numSensors):
            chName = ch+1
            self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_up[str(chName)]))
            #self.setpoint[ch].setText('%s C' %(sets_up[str(chName)]))
        intlock_trigger = str(stat_up[0])[0:4]
        if intlock_trigger == "Fals":
            icon = QtGui.QIcon(':/qtutils/fugue/tick-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            # for ch in range(self.numSensors):
            #     chName = ch+1
                
            self.ui.digital_reset.setStyleSheet("")
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
        elif intlock_trigger == "True":
            self.chanBut[7].setText(stat_up[1])
            icon = QtGui.QIcon(':/qtutils/fugue/cross-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            stat_mess = str(stat_up[1])
            if stat_mess == "flow1":
                self.ui.status_message.setText("Check Flowmeter 1")
            elif stat_mess == "flow2":
                self.ui.status_message.setText("Check Flowmeter 2")
            elif stat_mess == "DigiL":
                self.ui.status_message.setText("Check Digital Lock")
                self.ui.digital_lock.setStyleSheet("color: red;"
                                                   "border-style: solid;"
                                                   "border-width: 2px;"
                                                   "border-color: red;"
                                                   "border-radius: 3px"
                                                   )
            elif stat_mess == "HighT":
                self.ui.status_message.setText("Check Temperatures")
                for ch in range(self.numSensors):
                    chName = ch+1
                    if temp_up[str(chName)] > sets_up[str(chName)]:
                        self.adjust[ch].show()
                        self.adjust[ch].setStyleSheet("color: red;"
                                                       #"background-color: red;"
                                                        "border-style: solid;"
                                                        "border-width: 1px;"
                                                        "border-color: red;"
                                                        "border-radius: 3px")
                        if self.chan_tog[ch]:
                            self.chanBut[ch].setStyleSheet("color: #950000;"
                                                           "background-color: %s;"
                                                            "border-style: solid;"
                                                            "border-width: 2px;"
                                                            "border-color: red;"
                                                            "border-radius: 3px"
                                                            %(self.chanCol[ch]))
                        else:
                            self.chanBut[ch].setStyleSheet("color: #950000;"
                                                           "background-color: %s;"
                                                            "border-style: solid;"
                                                            "border-width: 2px;"
                                                            "border-color: red;"
                                                            "border-radius: 3px"
                                                            %(self.chanDisCol[ch]))
                    else:
                        self.adjust[ch].setStyleSheet("")
                        if self.chan_tog[ch]:
                            self.chanBut[ch].setStyleSheet("background-color: %s;"
                                                            "border-style: solid;"
                                                            "border-width: 1px;"
                                                            "border-color: gray;"
                                                            "border-radius: 3px"
                                                            %(self.chanCol[ch]))
                        else:
                            self.chanBut[ch].setStyleSheet("background-color: %s;"
                                                            "border-style: solid;"
                                                            "border-width: 1px;"
                                                            "border-color: gray;"
                                                            "border-radius: 3px"
                                                            %(self.chanDisCol[ch]))
                    #self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_up[str(chName)]))
            elif stat_mess == "React":
                self.ui.status_message.setText("Press Reset")
                self.ui.digital_reset.setStyleSheet("color: red;"
                                                    "border-style: solid;"
                                                    "border-width: 2px;"
                                                    "border-color: red;"
                                                    "border-radius: 3px"
                                                    )
                for ch in range(self.numSensors):
                    self.adjust[ch].setStyleSheet("")
                    if self.chan_tog[ch]:
                        self.chanBut[ch].setStyleSheet("background-color: %s;"
                                                        "border-style: solid;"
                                                        "border-width: 1px;"
                                                        "border-color: gray;"
                                                        "border-radius: 3px"
                                                        %(self.chanCol[ch]))
                    else:
                        self.chanBut[ch].setStyleSheet("background-color: %s;"
                                                        "border-style: solid;"
                                                        "border-width: 1px;"
                                                        "border-color: gray;"
                                                        "border-radius: 3px"
                                                        %(self.chanDisCol[ch]))
            mess_icon = QtGui.QIcon(':/qtutils/fugue/exclamation')
            mess_pixmap = mess_icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_symbol.setPixmap(mess_pixmap)
            self.ui.status_symbol.show()
            self.ui.status_message.show()
        else:
            icon = QtGui.QIcon(':/qtutils/fugue/question')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_update.setText('%s' %(intlock_trigger))
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
            
        if self.iter_count > (self.max_graph_points):
            self.iter_count = self.max_graph_points
            self.plot_temp = np.delete(self.plot_temp, [0], axis = 1)
            
        self.plot_temp = np.insert(self.plot_temp, self.iter_count, [temp_up["1"],
                                                                     temp_up["2"],
                                                                     temp_up["3"],
                                                                     temp_up["4"], 
                                                                     temp_up["5"],
                                                                     temp_up["6"], 
                                                                     temp_up["7"], 
                                                                     temp_up["8"], 
                                                                     temp_up["9"], 
                                                                     temp_up["10"], 
                                                                     temp_up["11"], 
                                                                     temp_up["12"],
                                                                     temp_up["13"], 
                                                                     temp_up["14"], 
                                                                     temp_up["15"], 
                                                                     temp_up["16"], 
                                                                     int(time.time()-self.plot_start)], axis=1)
        if self.chan_tog[0]:
            self.ch_1_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[0, 0:self.iter_count])
        if self.chan_tog[1]:
            self.ch_2_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[1, 0:self.iter_count])
        if self.chan_tog[2]:
            self.ch_3_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[2, 0:self.iter_count])
        if self.chan_tog[3]:
            self.ch_4_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[3, 0:self.iter_count])
        if self.chan_tog[4]:
            self.ch_5_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[4, 0:self.iter_count])
        
        if self.chan_tog[8]:
            self.ch_9_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[8, 0:self.iter_count])
        if self.chan_tog[9]:
            self.ch_10_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[9, 0:self.iter_count])
        if self.chan_tog[10]:
            self.ch_11_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[10, 0:self.iter_count])
        if self.chan_tog[11]:
            self.ch_12_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[11, 0:self.iter_count])
        if self.chan_tog[12]:
            self.ch_13_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[12, 0:self.iter_count])
        
        if self.chan_tog[15]:
            self.ch_16_ref.setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[15, 0:self.iter_count])
        self.iter_count += 1

    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)
    def temp_callout(self, button):
        print('Calling for New Temperatures...')
        yield(self.queue_work(self._primary_worker,'new_temps'))
    
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)    
    def temp_zero(self, button):
        print('Returning Temperatures to Zero...')
        for ch in range(self.numSensors):
            self.chanBut[ch].setText("%s \n 0.00 C" %(self.chanText[ch]))
    
    
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL,True)    
    def shot_read_check(self):
        #print('Checking for shots...')
        self.shot_read = yield(self.queue_work(self._primary_worker,'shot_check'))
   
        
    @define_state(MODE_MANUAL,True)
    def on_const_temps(self, button=0):
        print('Constant Temperature Acquisition Strarting...')  
        self.ui.start_continuous.hide()
        self.ui.stop_continuous.show()
        self.start_continuous()
        self.contin_on = True
        if self.temp_check_flag == False:
            self.initial_grab()
            self.check_thread = threading.Thread(
                target=self.continuous_loop, args=(), daemon=True
                )
            self.check_thread.start()
            self.temp_check_flag = True
        else:
            self.contin_on = True
    
    
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL, True)
    def off_const_temps(self, button, verbose = False):
        #self.ui.start_continuous.setEnabled(False)
        if verbose:
            print('Stopping Constant Temperature Acquisition...')
        self.ui.stop_continuous.hide()
        self.ui.start_continuous.show()
        self.stop_continuous()
        self.contin_on = False

        
    @define_state(MODE_MANUAL, True)
    def start_continuous(self):
        yield(self.queue_work(self._primary_worker,'start_continuous'))
    
    
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL, True)
    def stop_continuous(self):
        yield(self.queue_work(self._primary_worker,'stop_continuous'))
   
    
    def continuous_loop(self):
        interval=5
        self.plot_start = time.time()
        while True:
            self.shot_read_check()
            if self.shot_read:
                #self.packet_update
                self.temp_shot_update()
                self.stat_shot_update()
            elif self.contin_on:
                self.grab_packet_update()
            time.sleep(interval)

            

