# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 12:10:25 2022

@author: rubidium

Defines the blacs tab class and GUI for the Arduino_Interlock device
"""

from labscript_devices import BLACS_tab#, runviewer_parser
from blacs.device_base_class import DeviceTab
from blacs.tab_base_classes import define_state, Tab
from blacs.tab_base_classes import MODE_MANUAL, MODE_TRANSITION_TO_BUFFERED, MODE_TRANSITION_TO_MANUAL, MODE_BUFFERED  

import os
import sys
import numpy as np
import threading, time
from qtutils import UiLoader, inmain_decorator
import qtutils.icons
from qtutils.qt import QtWidgets, QtGui, QtCore
from labscript_utils.qtwidgets.toolpalette import ToolPaletteGroup
import pyqtgraph as pg

#@BLACS_tab
class Arduino_Interlock_Tab(DeviceTab):

#Big function that sets the GUI on blacs and prepares any necessary variables, lists, dictionaries, etc. - called on start-up
    def initialise_GUI(self):
        #sets layout to blacs tab layout
         layout = self.get_tab_layout()
         
         # Loads GUI for interlock from ui document made in QT Designer
         ui_filepath = os.path.join(
             os.path.dirname(os.path.realpath(__file__)), 'interlock_GUI.ui'
         )
         self.ui = UiLoader().load(ui_filepath)       #loads filepath and sets as variable for convenient calling
         
         #Creates a scrollArea widget and adds the interlock ui inside 
         #      (allows ui window to be viewed  in smaller frame while maintaining size policies)
         scrollArea = QtWidgets.QScrollArea()
         scrollArea.setWidget(self.ui)

         #variables to be used later
         self.numSensors = 16          #Number of channels
         self.contin_on = False           #flag for pausing auto-loop
         self.shot_read = False           #to be used for updating ui during shots - may be broken currently
         self.temp_check_flag = False           #flag to indicate the need to start a new auto-loop thread
         self.con_toggle = True           #toggle flag for interlock controls sub-tab
         self.mon_toggle = True           #toggle flag for channel monitor sub-tab
         self.gra_toggle = True           #toggle flag for temperature graph sub-tab
         self.auto_go = False         #flag for killing auto-loop thread
         
         #lists for storing values, GUI elements, properties, etc.
         self.set_setpoint_vals = []        #stores new setpoints to be sent
         self.adjust = []            #stores spinboxes for convenient and iterative("for" loop) calling
         self.chanBut = []           #stores channel buttons for convenient and iterative calling
         self.chanText = []           #stores button text for convenient and iterative calling
         self.chanName = []           #stores button thermocouple names for convenient and iterative calling
         self.chanCol = []          #stores channel active colors for convenient and iterative calling
         self.chanDisCol = []          #stores channel disable colors for convenient and iterative calling
         self.chanPlotRef = []
         self.chan_tog = [True, True, True, True, True, False, False, False, 
                          True, True, True, True, True, False, False, True]
         
         #integer variables for graphing
         self.loop_time = 0         #starts a time count for the graph
         self.iter_count = 0          #counts the number of iterations (to keep track of points on the graph)
         self.max_graph_points = 1440           #maximum points to be saved for temp graphing
         self.plot_temp = np.zeros([17, 1])             #creates an arry of 17 rows with 0s as the entries
         self.plot_start = 0                #begins the plotting time at zero seconds
         
         #adds the scrollArea widget (containing the interlock GUI) into the layout
         layout.addWidget(scrollArea)
         self.graph_widget = self.ui.graph_widget  #create graph widget and redefine for more convenient calling

         # define the data in the graph widget
         title = "Temperature Graph"
         plt = self.graph_widget        # create plot window object
         plt.showGrid(x = True, y = True) 
         plt.setLabel('left', 'Temperature', units ='degC')         #Note: defining units this way allows for autoscaling
         plt.setLabel('bottom', 'Time', units ='sec')
         plt.setTitle(title)
         
         #create a reference line to plot for each active channel and define attributes
         self.ch_1_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[0], pen ='r', #red
                                name ='Ch_1')
         self.ch_2_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[1], pen ='y', #yellow
                                name ='Ch_2')
         self.ch_3_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[2], pen ='g', #green
                                name ='Ch_3')
         self.ch_4_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[3], pen ='c', #cyan
                                name ='Ch_4')
         self.ch_5_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[4], pen =[20, 141, 255], #blue
                                name ='Ch_5')
         self.ch_9_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[8], pen =[248, 187, 208], #pink
                                name ='Ch_9')
         self.ch_10_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[9], pen =[184, 104, 200], #purple
                                name ='Ch_10')
         self.ch_11_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[10], pen =[255, 136, 0], #orange
                                name ='Ch_11')
         self.ch_12_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[11], pen =[204, 255, 144], #mint-green
                                name ='Ch_12')
         self.ch_13_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[12], pen =[215, 204, 200], #tan
                                name ='Ch_13')
         self.ch_16_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[15], pen =[250, 250, 250], #white
                                name ='Ch_16')
               
         #Adds the channel plots as items in a list for convenient calling
         self.chanPlotRef.append(self.ch_1_ref)
         self.chanPlotRef.append(self.ch_2_ref)
         self.chanPlotRef.append(self.ch_3_ref)
         self.chanPlotRef.append(self.ch_4_ref)
         self.chanPlotRef.append(self.ch_5_ref)
         self.chanPlotRef.append(False)
         self.chanPlotRef.append(False)
         self.chanPlotRef.append(False)
         self.chanPlotRef.append(self.ch_9_ref)
         self.chanPlotRef.append(self.ch_10_ref)
         self.chanPlotRef.append(self.ch_11_ref)
         self.chanPlotRef.append(self.ch_12_ref)
         self.chanPlotRef.append(self.ch_13_ref)
         self.chanPlotRef.append(False)
         self.chanPlotRef.append(False)
         self.chanPlotRef.append(self.ch_16_ref)
         
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
         
         #Adds the setpoint spinboxes as items to the list self.adjust for convenient calling
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
         
         
         # # Connect the appropriate signals for buttons
         #Connect clicked signal to the appropriate function for each respective sub-tab
         self.ui.interlock_controls.clicked.connect(self.interlock_controls_clicked)
         self.ui.channel_monitor.clicked.connect(self.channel_monitor_clicked)
         self.ui.temp_graph.clicked.connect(self.temp_graph_clicked)
         
         #Connect clicked signal to the appropriate function for the digital interlock controls
         self.ui.digital_lock.clicked.connect(self.lock_clicked)    
         self.ui.digital_reset.clicked.connect(self.reset_clicked)
         
         #Connect clicked signal to the appropriate function for the refresh temperature controls
         self.ui.update_temps.clicked.connect(self.update_temps_clicked)
         self.ui.zero_temps.clicked.connect(self.temp_zero)
         
         #Connect clicked signal to the appropriate function for the auto-loop start/stop buttons
         self.ui.start_continuous.clicked.connect(self.on_const_temps)
         self.ui.stop_continuous.clicked.connect(self.off_const_temps)
         
         #Connect clicked signal to the appropriate function for the Interlock Setpoints buttons
         self.ui.hide_setpoints.clicked.connect(self.hide_setpoints_clicked)
         self.ui.set_setpoints.clicked.connect(self.set_setpoints_clicked)
         self.ui.default_setpoints.clicked.connect(self.default_setpoints_clicked)
         
         #Connect clicked signal to the appropriate function for the status update button
         self.ui.status_update.clicked.connect(self.status_update_clicked)
         
         #Connect clicked signal to the appropriate function for each respective channel monitor button
         self.ui.channel_1_button.clicked.connect(lambda: self.channel_clicked(0))
         self.ui.channel_2_button.clicked.connect(lambda: self.channel_clicked(1))
         self.ui.channel_3_button.clicked.connect(lambda: self.channel_clicked(2))
         self.ui.channel_4_button.clicked.connect(lambda: self.channel_clicked(3))
         self.ui.channel_5_button.clicked.connect(lambda: self.channel_clicked(4))
         self.ui.channel_9_button.clicked.connect(lambda: self.channel_clicked(8))
         self.ui.channel_10_button.clicked.connect(lambda: self.channel_clicked(9))
         self.ui.channel_11_button.clicked.connect(lambda: self.channel_clicked(10))
         self.ui.channel_12_button.clicked.connect(lambda: self.channel_clicked(11))
         self.ui.channel_13_button.clicked.connect(lambda: self.channel_clicked(12))
         self.ui.channel_16_button.clicked.connect(lambda: self.channel_clicked(15))
         
         
         #Sets the range of each of the interlock setpoint spinboxes
         for ch in range(self.numSensors):
             self.adjust[ch].setRange(0,150)   #Sets the range of each of the interlock setpoint spinboxes
             self.set_setpoint_vals.append(0)   #creates a placeholder value for each spinbox and stores in self.set_setpoint_vals
             #Connect editingFinished signal to the appropriate function for each respective setpoint adjustment spinbox
             self.adjust[ch].editingFinished.connect(self.send_setpoint_set)

         
         #Sets icons and tool-tip for start / stop continuous buttons
         self.ui.start_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control'))
         self.ui.start_continuous.setToolTip('Starts Automatic Updating of Temperatures, Graph, and Status')
         self.ui.stop_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control-stop-square'))
         self.ui.stop_continuous.setToolTip('Ends Automatic Updating of Temperatures, Graph, and Status')
         
         #Set icons and tool-tip for sub-tab buttons
         self.ui.interlock_controls.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.interlock_controls.setToolTip('Click to hide')
         self.ui.channel_monitor.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.channel_monitor.setToolTip('Click to hide')
         self.ui.temp_graph.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.temp_graph.setToolTip('Click to hide')
    

         #define strings for gradient color background
         self.Chan1Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 0, 0, 255), stop:1 rgba(255, 0, 0, 255))"
         self.Chan2Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 220, 0, 255), stop:1 rgba(255, 255, 0, 255))"
         self.Chan3Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(0, 220, 0, 255), stop:1 rgba(0, 255, 0, 255))"
         self.Chan4Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(0, 220, 220, 255), stop:1 rgba(0, 255, 255, 255))"
         self.Chan5Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(17, 122, 220, 255), stop:1 rgba(20, 141, 255, 255))"
         self.Chan6Col = ""
         self.Chan7Col = ""
         self.Chan8Col = ""
         self.Chan9Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(218, 165, 184, 255), stop:1 rgba(248, 187, 208, 255))"
         self.Chan10Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(163, 92, 177, 255), stop:1 rgba(184, 104, 200, 255))"
         self.Chan11Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 117, 0, 255), stop:1 rgba(255, 136, 0, 255))"
         self.Chan12Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(155, 220, 174, 255), stop:1 rgba(179, 255, 203, 255))"
         self.Chan13Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(189, 180, 177, 255), stop:1 rgba(215, 204, 200, 255))"
         self.Chan14Col = ""
         self.Chan15Col = ""
         self.Chan16Col = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(216, 216, 216, 255), stop:1 rgba(250, 250, 250, 255))"
         
         #Adds the channel colors as items in a list for convenient calling (they are such long strings, so this happens in 2 steps)
         self.chanCol.append(self.Chan1Col)  #Note: each color is in hexcode (currently defined above - will optimize/ rearrange)
         self.chanCol.append(self.Chan2Col)
         self.chanCol.append(self.Chan3Col)
         self.chanCol.append(self.Chan4Col)
         self.chanCol.append(self.Chan5Col)
         self.chanCol.append(self.Chan6Col)
         self.chanCol.append(self.Chan7Col)        
         self.chanCol.append(self.Chan8Col)        
         self.chanCol.append(self.Chan9Col)
         self.chanCol.append(self.Chan10Col)
         self.chanCol.append(self.Chan11Col)
         self.chanCol.append(self.Chan12Col)
         self.chanCol.append(self.Chan13Col)
         self.chanCol.append(self.Chan14Col)        
         self.chanCol.append(self.Chan15Col)        
         self.chanCol.append(self.Chan16Col)
         
         #Adds the channel disabled colors as items in a list for convenient calling
         self.chanDisCol.append("#8c0000")  #Note: each color is in hexcode
         self.chanDisCol.append("#9a9a00")
         self.chanDisCol.append("#008800")
         self.chanDisCol.append("#009999")
         self.chanDisCol.append("#094175")
         self.chanDisCol.append("")         #this channel is inactive, so it has no color
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

         
         #Adds the channel-number names as items in a list for convenient calling
         for ch in range(self.numSensors):
             chanNum = ch+1
             textMess = " Chan "+str(chanNum)+" "
             self.chanText.append("\u0332".join(textMess))      #the "\u0332".join() string adds an underline
 
         
         #Adds the channel thermocouple names as items in a list for convenient calling
         self.chanName.append("\u0332".join(" TC-MOT-I "))      #MOT Coils (interior)        
         self.chanName.append("\u0332".join(" TC-MOTB-I "))         #MOT Bias Coils (exterior)
         self.chanName.append("\u0332".join(" TC-OT-I "))       #Outer Transport Coils 
         self.chanName.append("\u0332".join(" TC-SCI-I "))       #SCI Cell Coils (interior)
         self.chanName.append("\u0332".join(" TC-SCIB-I "))       #SCI Cell Bias Coils (exterior)
         self.chanName.append("\u0332".join(" Chan 6 "))        #channel without a thermocouple, so default to chan number
         self.chanName.append("\u0332".join(" Chan 7 "))
         self.chanName.append("\u0332".join(" Chan 8 "))
         self.chanName.append("\u0332".join(" TC-MOT-II "))         #The "II" designates Coil Holder II
         self.chanName.append("\u0332".join(" TC-MOTB-II "))
         self.chanName.append("\u0332".join(" TC-OT-II "))
         self.chanName.append("\u0332".join(" TC-SCI-II "))
         self.chanName.append("\u0332".join(" TC-SCIB-II "))
         self.chanName.append("\u0332".join(" Chan 14 "))       #the "\u0332" string adds an underline the .join() string
         self.chanName.append("\u0332".join(" Chan 15 "))
         self.chanName.append("\u0332".join(" TC-TRNBNK "))

         
     #define attributes of the channel monitor button corresponding to a particular line on the graph
         for ch in range(self.numSensors):
             self.chanBut[ch].setText("%s \n 0.00 C" %(self.chanName[ch]))
             self.chanBut[ch].setStyleSheet("background-color : %s;border-style: solid;border-width: 1px;"
                                                    "border-color: gray;border-radius: 3px" %(self.chanCol[ch])) 


        #hides the setpoint spinboxes and labels initially
         self.ui.hide_setpoints.hide()
         self.ui.setpoints_label_1.hide()
         self.ui.setpoints_label_2.hide()
         for ch in range(self.numSensors):
             self.adjust[ch].hide()
         
         #hides the setpoint adjust spinboxes and buttons initially
         self.ui.default_setpoints.hide()
         for ch in range(self.numSensors):
             self.adjust[ch].hide()
         
         #hides the interlock trigger warning symbol and message initially   
         self.ui.status_symbol.hide()
         self.ui.status_message.hide()
         self.ui.stop_continuous.hide()
         
         #hides a blank widget used for spacing (the widget pushes the other subtabs when the temp graph is hidden)
         self.ui.push_widg.hide()
         
         #since labels have no attribute "label.setIcon", create a pixelmap of the desired icon and set pixelmap 
         icon = QtGui.QIcon(':/qtutils/fugue/question')
         pixmap = icon.pixmap(QtCore.QSize(16, 16))
         self.ui.status_icon.setPixmap(pixmap)
         
         
#function used by blacs/labscript to load device worker -automatically called upon start-up
    def initialise_workers(self):
        worker_initialisation_kwargs = self.connection_table.find_by_name(self.device_name).properties
        worker_initialisation_kwargs['addr'] = self.BLACS_connection
        self.create_worker(
            'main_worker',
            'user_devices.Arduino_Interlock.blacs_workers.Arduino_Interlock_Worker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'

        #This is most likely not best practice, but gives a way for the blacs start-up to 
        #       set into motion the auto-loop when the device is first loaded
        self.begin_autoloop()       


    #creates a function for the plot of the channel temperatures
    def plot(self, time, temp):    
        self.graph_widget.plot(time, temp)
        

    #grabs the initial packet from the arduino (grabs all channel temperatures, setpoints, and the interlock status)
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)
    def initial_grab(self):
        time.sleep(2)    #necessary to prevent timeout error!
        temp_init, set_init, stat_init = yield(self.queue_work(self._primary_worker,'initial_packet'))
        for ch in range(self.numSensors):
             chName = ch+1
             #self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_init[str(chName)]))
             self.chanBut[ch].setText("%s \n %s C" %(self.chanName[ch], temp_init[str(chName)]))
             self.adjust[ch].setValue(set_init[str(chName)])
        self.on_const_temps()    
     
    #takes a signal from the interlock_controls sub-tab button and toggles the sub-tab between shown and hidden
    def interlock_controls_clicked(self, button):
        if self.con_toggle:
            self.ui.control_box.hide()
            self.con_toggle = False
            self.ui.interlock_controls.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small-expand'))
            self.ui.interlock_controls.setToolTip('Click to show')
        else:
            self.ui.control_box.show()
            self.con_toggle = True
            self.ui.interlock_controls.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
            self.ui.interlock_controls.setToolTip('Click to hide')

    
    #takes a signal from the channel_monitor sub-tab button and toggles the sub-tab between shown and hidden
    def channel_monitor_clicked(self, button):
        if self.mon_toggle:
            self.ui.monitor_box.hide()
            self.mon_toggle = False
            self.ui.channel_monitor.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small-expand'))
            self.ui.channel_monitor.setToolTip('Click to show')
        else:
            self.ui.monitor_box.show()
            self.mon_toggle = True
            self.ui.channel_monitor.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
            self.ui.channel_monitor.setToolTip('Click to hide')
       
    
    #takes a signal from the temperature graph sub-tab button and toggles the sub-tab between shown and hidden    
    def temp_graph_clicked(self, button):
        if self.gra_toggle:
            self.ui.graph_widget.hide()
            self.ui.push_widg.show()
            self.gra_toggle = False
            self.ui.temp_graph.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small-expand'))
            self.ui.temp_graph.setToolTip('Click to show')
        else:
            self.ui.graph_widget.show()
            self.ui.push_widg.hide()
            self.gra_toggle = True
            self.ui.temp_graph.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
            self.ui.temp_graph.setToolTip('Click to hide')              
     
        
    #Takes a signal from the digital_lock button and appropriately toggles the lock (by queueing a worker function) 
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def lock_clicked(self, button):
        print('Attempting to lock...')
        lock_stat = yield(self.queue_work(self._primary_worker,'toggle_lock'))
        print(lock_stat)
        if lock_stat == "Digital Interlock Trigger... Stopping system!" or lock_stat == "System is already triggered... Digital Lock activated!":
            self.ui.digital_lock.setText('Unlock')
        else:
            self.ui.digital_lock.setText('Lock')
            self.ui.digital_lock.setStyleSheet("")
        
    
    #Takes a signal from the digital_reset button and queues a worker function to send the reset to the arduino         
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def reset_clicked(self, button):
        print('Attempting to Reset...')
        yield(self.queue_work(self._primary_worker,'push_reset'))
        
        self.ui.digital_reset.setStyleSheet("")                                     
    
    
    #Takes a signal from the  button and appropriately toggles the lock (by queueing a worker function)     
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def update_temps_clicked(self, button):
        self.grab_temp_update()


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def status_update_clicked(self, button):
        self.grab_status_update()
        
    
    #Takes a signal from the hide_setpoints button and hides the setpoints in the interlock GUI     
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def hide_setpoints_clicked(self, button):
        self.ui.hide_setpoints.hide()
        self.ui.set_setpoints.show()
        self.ui.default_setpoints.hide()
        self.ui.setpoints_label_1.hide()
        self.ui.setpoints_label_2.hide()
        for ch in range(self.numSensors):
            self.adjust[ch].hide()

    #Takes a signal from the set_setpoints button and displays the setpoint spinboxes in the interlock GUI
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def set_setpoints_clicked(self, button):
        self.ui.set_setpoints.hide()
        self.ui.default_setpoints.show()
        self.ui.hide_setpoints.show()
        self.grab_setpoints()
        
        self.ui.setpoints_label_1.show()
        self.ui.setpoints_label_2.show()
        
        for ch in range(self.numSensors):
            self.adjust[ch].show()

    
    #Takes a signal from a spinbox after an edit, adds the new setpoints to a list, and then send the list to a worker function
    @define_state(MODE_MANUAL, True)      
    def send_setpoint_set(self, button=0):
        self.grab_new_setpoints()
        self.send_new_setpoints()


    #Takes a signal from the default_setpoints button, activates the appropriate worker function, and hides the setpoint spinboxes
    @define_state(MODE_MANUAL, True)      
    def default_setpoints_clicked(self, button):
        self.ui.hide_setpoints.hide()
        self.ui.set_setpoints.show()
        self.ui.default_setpoints.hide()
        self.ui.setpoints_label_1.hide()
        self.ui.setpoints_label_2.hide()
        
        self.send_default_setpoints()
        self.grab_setpoints()

        for ch in range(self.numSensors):
            self.adjust[ch].hide() 
        
        
    # Function that toggles a generic channel button (passed to the function when clicked) and the channel's 
    #       temperature line on the graph. It works for all of the channel buttons (and is only defined here, woo!)
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_clicked(self, ch):
        if self.chan_tog[ch]:
            self.chan_tog[ch] = False
            self.chanPlotRef[ch].setData([],[])
            color = self.chanDisCol[ch]
            self.chanBut[ch].setToolTip('Click to Show on Graph')                                                   
        else:
            self.chan_tog[ch] = True
            self.chanPlotRef[ch].setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[ch, 0:self.iter_count-1])
            color = self.chanCol[ch]
            self.chanBut[ch].setToolTip('Click to Hide from Graph')
        self.chanBut[ch].setStyleSheet("background-color : %s;" "border-style: solid;"
                        "border-width: 1px;" "border-color: gray;" "border-radius: 3px" %(color))

    #function for reuqesting only new temperatures from the worker (linked to a button rather than auto-loop)    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_temp_update(self):
        print('Attempting to Grab Temperatures...')
        temp_up = yield(self.queue_work(self._primary_worker,'new_temps'))
        for ch in range(self.numSensors):
            chName = ch+1
            #self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_up[str(chName)]))
            self.chanBut[ch].setText("%s \n %s C" %(self.chanName[ch], temp_up[str(chName)]))
        
    
    #function for grabbing the latest temperature values from the worker during shots
    @define_state(MODE_TRANSITION_TO_MANUAL,True)      
    def temp_shot_update(self):
        print('Attempting to Grab Temperatures...')
        temp_up = yield(self.queue_work(self._primary_worker,'temp_return'))
        for ch in range(self.numSensors):
            chName = ch+1
            #self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_up[str(chName)]))
            self.chanBut[ch].setText("%s \n %s C" %(self.chanName[ch], temp_up[str(chName)]))
        
    
    #function for reuqesting only new interlock status from the worker (linked to a button rather than auto-loop)    
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
            #self.ui.status_update.setText('%s' %(intlock_trigger))
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
    
    
    #function for reuqesting the interlock status from the worker during a shot    
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
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
 
    
    #function for reuqesting the current setpoints from the worker (linked to a button rather than auto-loop) 
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_setpoints(self):
        print('Attempting to Grab Setpoints...')
        set_update = yield(self.queue_work(self._primary_worker,'new_setpoints'))
        for ch in range(self.numSensors):
            chName = ch+1
            self.adjust[ch].setValue(set_update[str(chName)])

    
    #function that compiles new setpoint values into a dictionary for referencing the appropriate spinbox's set value    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_new_setpoints(self):
        print('Compiling New Setpoints...')     
        for ch in range(self.numSensors):
            set_value = self.adjust[ch].value()
            self.set_setpoint_vals[ch]=set_value
        
    
    #function for sending the compiled setpoints in the set_sendpoint_vals dictionary to the worker function
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_new_setpoints(self):
        print('Sending New Setpoints...')
        set_send = yield(self.queue_work(self._primary_worker,'set_setpoints', self.set_setpoint_vals))
           

    #function that activates the default setpoints worker function to reset setpoints to the arduino's default values
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_default_setpoints(self):
        print('Sending New Setpoints...')
        yield(self.queue_work(self._primary_worker,'set_default_setpoints'))

    
    #function used by auto-loop to grab a new packet of temperatures, setpoint, and status and then update the blacs tab 
    #       with the appropriate values/ information
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_packet_update(self):
        print('Attempting to Grab Temperatures and Status...')
        #grab the new packets from the worker
        temp_up, sets_up, stat_up = yield(self.queue_work(self._primary_worker,'new_packet', verbose = False))
        #set the channel buttons with the appropriate updated strings that include the latest temperatures
        for ch in range(self.numSensors):
            chName = ch+1
            #self.chanBut[ch].setText("%s \n %s C" %(self.chanText[ch], temp_up[str(chName)]))
            self.chanBut[ch].setText("%s \n %s C" %(self.chanName[ch], temp_up[str(chName)]))
        #grab the interlock trigger status and update appropriately
        intlock_trigger = str(stat_up[0])[0:4]
        if intlock_trigger == "Fals":
            icon = QtGui.QIcon(':/qtutils/fugue/tick-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
                
            self.ui.digital_reset.setStyleSheet("")
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
        #if true, update and check for the warning message  - then display warning and highlight the button of attention
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
                self.ui.digital_lock.setStyleSheet("color: red;border-style: solid;border-width: 2px;"
                                                   "border-color: red;border-radius: 3px")
            elif stat_mess == "HighT":
                self.ui.status_message.setText("Check Temperatures")
                for ch in range(self.numSensors):
                    chName = ch+1
                    if temp_up[str(chName)] > sets_up[str(chName)]:
                        self.adjust[ch].show()
                        self.adjust[ch].setStyleSheet("color: red;border-style: solid;border-width: 1px;border-color: red;"
                                                        "border-radius: 3px")
                        if self.chan_tog[ch]:
                            colorCol = self.chanCol[ch]
                        else:
                            colorCol = self.chanDisCol[ch]
                        self.chanBut[ch].setStyleSheet("color: #950000;background-color: %s;border-style: solid;border-width: 2px;"
                                                            "border-color: red;border-radius: 3px" %(colorCol))
                    else:
                        self.adjust[ch].setStyleSheet("")
                        if self.chan_tog[ch]:
                            colorCol = self.chanCol[ch]
                        else:
                            colorCol = self.chanDisCol[ch]
                        self.chanBut[ch].setStyleSheet("background-color: %s;border-style: solid;border-width: 1px;"
                                                            "border-color: gray;border-radius: 3px" %(colorCol))
            elif stat_mess == "React":
                self.ui.status_message.setText("Press Reset")
                #This is added to remove old attention warnings for the channels (as "React" can only be displayed once
                #       all channels have returned to acceptable temperature levels and all other checks are normal)
                self.ui.digital_reset.setStyleSheet("color: red;border-style: solid;border-width: 2px;"
                                                    "border-color: red;border-radius: 3px")
                for ch in range(self.numSensors):
                    self.adjust[ch].setStyleSheet("")
                    if self.chan_tog[ch]:
                        self.chanBut[ch].setStyleSheet("background-color: %s;border-style: solid;border-width: 1px;border-color: gray;"
                                                        "border-radius: 3px" %(self.chanCol[ch]))
                    else:
                        self.chanBut[ch].setStyleSheet("background-color: %s;border-style: solid;border-width: 1px;border-color: gray;"
                                                        "border-radius: 3px" %(self.chanDisCol[ch]))
            mess_icon = QtGui.QIcon(':/qtutils/fugue/exclamation')
            mess_pixmap = mess_icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_symbol.setPixmap(mess_pixmap)
            self.ui.status_symbol.show()
            self.ui.status_message.show()
        #if neither true nor false are returned, the status is unknown, so display a "question" icon
        else:
            icon = QtGui.QIcon(':/qtutils/fugue/question')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_symbol.hide()
            self.ui.status_message.hide()
        
    #Update the temperature graph with the new temperature data for each channel's line    
        
        #check for the maximum points on the graph, and if reached, remove the oldest column of data
        if self.iter_count > (self.max_graph_points):
            self.iter_count = self.max_graph_points
            self.plot_temp = np.delete(self.plot_temp, [0], axis = 1)
        
        #add the new temperature and time to the data array    
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
        
        #for each channel: if the button is active, plot the channel's temperature line
        for ch in range(self.numSensors):
            if self.chan_tog[ch]:
                self.chanPlotRef[ch].setData(self.plot_temp[16, 0:self.iter_count], self.plot_temp[ch, 0:self.iter_count])
       #increase point count by 1
        self.iter_count += 1

    
    
    #if a signal is recieved from the temperature_zero button, remove all the temperatures displayed on the button
    #       This DOES NOT affect the temperature graph, just the button displays
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)    
    def temp_zero(self, button):
        print('Returning Temperatures to Zero...')
        for ch in range(self.numSensors):
            #self.chanBut[ch].setText("%s \n 0.00 C" %(self.chanText[ch]))
            self.chanBut[ch].setText("%s \n 0.00 C" %(self.chanName[ch]))    
    
    #
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL,True)    
    def shot_read_check(self):
        self.shot_read = yield(self.queue_work(self._primary_worker,'shot_check'))
   
     
    #activates the auto-loop (continuos_loop) by either creating a new thread or, if one exists, changing the
    #       contin_on flag to True
    @define_state(MODE_MANUAL,True)
    def on_const_temps(self, button=0):
        print('Constant Temperature Acquisition Strarting...')  
        self.ui.start_continuous.hide()
        self.ui.stop_continuous.show()
        self.start_continuous()
        self.contin_on = True
        #self.auto_go = True
        if self.temp_check_flag == False:
            self.check_thread = threading.Thread(
                target=self.continuous_loop, args=(), daemon=True
                )
            self.check_thread.start()
            self.temp_check_flag = True
        else:
            self.contin_on = True
    
    #stops (pauses) the auto-loop (continuos_loop) by setting the contin_on flag to False
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL, True)
    def off_const_temps(self, button, verbose = False):
        if verbose:
            print('Stopping Constant Temperature Acquisition...')
        self.ui.stop_continuous.hide()
        self.ui.start_continuous.show()
        self.stop_continuous()
        self.contin_on = False


    #upon start-up / reinitialization, activates the inital_grab function in a thread
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL, True)
    def begin_autoloop(self):
        self.first_grab_thread = threading.Thread(target=self.initial_grab, args=(), daemon=True)
        self.first_grab_thread.start()
        
    
    #activates the worker to display that the auto-acquisition-loop had begun    
    @define_state(MODE_MANUAL, True)
    def start_continuous(self):
        yield(self.queue_work(self._primary_worker,'start_continuous'))
    
    
    #activates the worker to display that the auto-acquisition-loop had been stopped
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL, True)
    def stop_continuous(self):
        yield(self.queue_work(self._primary_worker,'stop_continuous'))
   
    
   #defines the loop for auto-aquisition of packets
    def continuous_loop(self, auto_go=True, interval = 5):
        self.auto_go = auto_go
        self.plot_start = time.time()
        while self.auto_go:
            self.shot_read_check()
            if self.shot_read:
                self.temp_shot_update()
                self.stat_shot_update()
            elif self.contin_on:
                self.grab_packet_update()
            time.sleep(interval)


            