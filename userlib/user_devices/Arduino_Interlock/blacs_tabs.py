# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 12:10:25 2022

@author: rubidium

Defines the blacs tab class and GUI for the Arduino_Interlock device
"""

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
import pyqtgraph as pg

class Arduino_Interlock_Tab(DeviceTab):

    def initialise_GUI(self):
         layout = self.get_tab_layout()

         # # Load monitor UI
         ui_filepath = os.path.join(
             os.path.dirname(os.path.realpath(__file__)), 'interlock.ui'
         )
         self.ui = UiLoader().load(ui_filepath)
         
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
         self.temp = []
         self.chan_tog = [True, True, True, True, True, True, True, True, 
                          True, True, True, True, True, True, True, True]
         
         self.iter_count = 0
         self.max_graph_points = 1440
         self.plot_temp = np.zeros([17, 1])
         self.plot_start = 0
         
         layout.addWidget(self.ui)
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
         self.ch_1_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[0], pen ='r',# symbol = 'o', symbolPen = 'r', symbolBrush = 0.05, 
                                name ='Ch_1')
         self.ch_2_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[1], pen ='y',# symbol = 'o', symbolPen = 'y', symbolBrush = 0.05, 
                                name ='Ch_2')
         self.ch_3_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[2], pen ='g',# symbol = 'o', symbolPen = 'g', symbolBrush = 0.05,
                                name ='Ch_3')
         self.ch_4_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[3], pen ='c',# symbol = 'o', symbolPen = 'c', symbolBrush = 0.05,
                                name ='Ch_4')
         self.ch_5_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[4], pen ='b',# symbol = 'o', symbolPen = 'b', symbolBrush = 0.05,
                                name ='Ch_5')
         self.ch_9_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[8], pen =[248, 187, 208],# symbol = 'o', symbolPen = 'b', symbolBrush = 0.05,
                                name ='Ch_9')
         self.ch_10_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[9], pen =[184, 104, 200],# symbol = 'o', symbolPen = 'b', symbolBrush = 0.05,
                                name ='Ch_10')
         self.ch_11_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[10], pen =[255, 136, 0],# symbol = 'o', symbolPen = 'b', symbolBrush = 0.05,
                                name ='Ch_11')
         self.ch_12_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[11], pen =[204, 255, 144],# symbol = 'o', symbolPen = 'b', symbolBrush = 0.05,
                                name ='Ch_12')
         self.ch_13_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[12], pen =[215, 204, 200],# symbol = 'o', symbolPen = 'b', symbolBrush = 0.05,
                                name ='Ch_13')
         self.ch_16_ref = self.graph_widget.plot(self.plot_temp[16], self.plot_temp[15], pen =[250, 250, 250],# symbol = 'o', symbolPen = 'b', symbolBrush = 0.05,
                                name ='Ch_16')
         
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
         self.ui.send_setpoints.clicked.connect(self.send_setpoints_clicked)
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
         
         #Sets icons for start and stop continuous
         self.ui.start_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control'))
         self.ui.start_continuous.setToolTip('Periodic Updating of the Interlock Status and Thermocouple Temps')
         self.ui.stop_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control-stop-square'))
         self.ui.start_continuous.setToolTip('Will Cease Periodic Updating of the Interlock Status and Thermocouple Temps')
         self.ui.interlock_controls.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.interlock_controls.setToolTip('Click to hide')
         self.ui.channel_monitor.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.channel_monitor.setToolTip('Click to hide')
         self.ui.temp_graph.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.temp_graph.setToolTip('Click to hide')
    
         #Adds the temperature channel labels as items in a list for convenient calling
         self.temp.append(self.ui.chan_1_temp)
         self.temp.append(self.ui.chan_2_temp)
         self.temp.append(self.ui.chan_3_temp)
         self.temp.append(self.ui.chan_4_temp)
         self.temp.append(self.ui.chan_5_temp)
         self.temp.append(self.ui.chan_6_temp)
         self.temp.append(self.ui.chan_7_temp)
         self.temp.append(self.ui.chan_8_temp)
         self.temp.append(self.ui.chan_9_temp)
         self.temp.append(self.ui.chan_10_temp)
         self.temp.append(self.ui.chan_11_temp)
         self.temp.append(self.ui.chan_12_temp)
         self.temp.append(self.ui.chan_13_temp)
         self.temp.append(self.ui.chan_14_temp)
         self.temp.append(self.ui.chan_15_temp)
         self.temp.append(self.ui.chan_16_temp)
          
         #Sets initial temperature values in the ui to 0.00
         for ch in range(self.numSensors):
             self.temp[ch].setText('0.00 C ')
         
         #Adds the temperature channel labels as items in a list for convenient calling
         self.setpoint.append(self.ui.chan_1_setpoint)
         self.setpoint.append(self.ui.chan_2_setpoint)
         self.setpoint.append(self.ui.chan_3_setpoint)
         self.setpoint.append(self.ui.chan_4_setpoint)
         self.setpoint.append(self.ui.chan_5_setpoint)
         self.setpoint.append(self.ui.chan_6_setpoint)
         self.setpoint.append(self.ui.chan_7_setpoint)
         self.setpoint.append(self.ui.chan_8_setpoint)
         self.setpoint.append(self.ui.chan_9_setpoint)
         self.setpoint.append(self.ui.chan_10_setpoint)
         self.setpoint.append(self.ui.chan_11_setpoint)
         self.setpoint.append(self.ui.chan_12_setpoint)
         self.setpoint.append(self.ui.chan_13_setpoint)
         self.setpoint.append(self.ui.chan_14_setpoint)
         self.setpoint.append(self.ui.chan_15_setpoint)
         self.setpoint.append(self.ui.chan_16_setpoint)
         
         #Sets initial setpoint values in the ui to -
         for ch in range(self.numSensors):
             self.setpoint[ch].setText(' - ') 
         
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
             self.setpoint[ch].hide()
         
         #hides the setpoint adjust spinboxes and buttons initially
         self.ui.send_setpoints.hide()
         self.ui.default_setpoints.hide()
         self.ui.release_setpoints.hide()
         for ch in range(self.numSensors):
             self.adjust[ch].hide()
         
         self.ui.stop_continuous.hide()
         self.ui.push_widg.hide()
         
         #since labels have no attribute "label.setIcon", create a pixelmap of the desired icon and set pixelmap 
         icon = QtGui.QIcon(':/qtutils/fugue/question')
         pixmap = icon.pixmap(QtCore.QSize(16, 16))
         self.ui.status_icon.setPixmap(pixmap)

          
         
         #self.supports_smart_programming(self.use_smart_programming) 

    #grabs the initial packet from the arduino (grabs all channel temperatures, setpoints, and the interlock status)
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)
    def initial_grab(self):
        temp_init, set_init, stat_init = yield(self.queue_work(self._primary_worker,'initial_packet'))
        for ch in range(self.numSensors):
             chName = ch+1
             self.temp[ch].setText('%s C' %(temp_init[str(chName)]))
             self.setpoint[ch].setText('%s C' %(set_init[str(chName)]))
            

    def initialise_workers(self):
        worker_initialisation_kwargs = self.connection_table.find_by_name(self.device_name).properties
        worker_initialisation_kwargs['addr'] = self.BLACS_connection
        self.create_worker(
            'main_worker',
            'user_devices.Arduino_Interlock.blacs_workers.Arduino_Interlock_Worker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'


    def plot(self, time, temp):    
        self.graph_widget.plot(time, temp)


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
             
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def lock_clicked(self, button):
        #self.ui.digital_lock.setEnabled(False)
        print('Attempting to lock...')
        lock_stat = yield(self.queue_work(self._primary_worker,'toggle_lock'))
        print(lock_stat)
        if lock_stat == "Digital Interlock Trigger... Stopping system!" or lock_stat == "System is already triggered... Digital Lock activated!":
            self.ui.digital_lock.setText('Unlock')
        else:
            self.ui.digital_lock.setText('Lock')
        
            
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def reset_clicked(self, button):
        print('Attempting to Reset...')
        yield(self.queue_work(self._primary_worker,'push_reset'))
    
        
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
            self.setpoint[ch].show()
        
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def hide_setpoints_clicked(self, button):
        self.ui.show_setpoints.show()
        self.ui.hide_setpoints.hide()
        self.ui.setpoints_label_1.hide()
        self.ui.setpoints_label_2.hide()
        for ch in range(self.numSensors):
            self.setpoint[ch].hide()


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def set_setpoints_clicked(self, button):
        self.ui.show_setpoints.hide()
        self.ui.hide_setpoints.hide()
        self.ui.set_setpoints.hide()
        self.ui.send_setpoints.show()
        self.ui.default_setpoints.show()
        self.ui.release_setpoints.show()
        self.grab_setpoints()
        
        self.ui.setpoints_label_1.show()
        self.ui.setpoints_label_2.show()
        
        for ch in range(self.numSensors):
            self.setpoint[ch].hide()
            self.adjust[ch].show()


    @define_state(MODE_MANUAL, True)      
    def send_setpoints_clicked(self, button):
        self.ui.show_setpoints.hide()
        self.ui.hide_setpoints.show()
        self.ui.set_setpoints.show()
        self.ui.send_setpoints.hide()
        self.ui.default_setpoints.hide()
        self.ui.release_setpoints.hide()
        self.ui.setpoints_label_1.show()
        self.ui.setpoints_label_2.show()
        
        self.grab_new_setpoints()
        self.send_new_setpoints()
        self.grab_setpoints()

        for ch in range(self.numSensors):
            self.adjust[ch].hide() 
            self.setpoint[ch].show()


    @define_state(MODE_MANUAL, True)      
    def default_setpoints_clicked(self, button):
        self.ui.show_setpoints.hide()
        self.ui.hide_setpoints.show()
        self.ui.set_setpoints.show()
        self.ui.send_setpoints.hide()
        self.ui.default_setpoints.hide()
        self.ui.release_setpoints.hide()
        self.ui.setpoints_label_1.show()
        self.ui.setpoints_label_2.show()
        
        self.send_default_setpoints()
        self.grab_setpoints()

        for ch in range(self.numSensors):
            self.adjust[ch].hide() 
            self.setpoint[ch].show()        
        
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def release_setpoints_clicked(self, button):
        self.ui.show_setpoints.hide()
        self.ui.hide_setpoints.show()
        self.ui.set_setpoints.show()
        self.ui.send_setpoints.hide()
        self.ui.default_setpoints.hide()
        self.ui.release_setpoints.hide()
        self.ui.setpoints_label_1.show()
        self.ui.setpoints_label_2.show()
        self.grab_setpoints()

        for ch in range(self.numSensors):
            self.adjust[ch].hide() 
            self.setpoint[ch].show()


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_1_clicked(self, button):
        if self.chan_tog[0]:
            self.chan_tog[0] = False
            self.ch_1_ref.setData([],[])
        else:
            self.chan_tog[0] = True
            # self.ch_1_ref = self.graph_widget.plot(self.plot_temp[5], self.plot_temp[0], pen ='r',# symbol = 'o', symbolPen = 'r', symbolBrush = 0.05, 
            #                        name ='Ch_1')
            self.ch_1_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[0, 0:self.iter_count-1])    
    
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_2_clicked(self, button):
        if self.chan_tog[1]:
            self.chan_tog[1] = False
            self.ch_2_ref.setData([],[])
        else:
            self.chan_tog[1] = True
            self.ch_2_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[1, 0:self.iter_count-1])    
    
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_3_clicked(self, button):
        if self.chan_tog[2]:
            self.chan_tog[2] = False
            self.ch_3_ref.setData([],[])
        else:
            self.chan_tog[2] = True
            self.ch_3_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[2, 0:self.iter_count-1])    
    
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_4_clicked(self, button):
        if self.chan_tog[3]:
            self.chan_tog[3] = False
            self.ch_4_ref.setData([],[])
        else:
            self.chan_tog[3] = True
            self.ch_4_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[3, 0:self.iter_count-1])    
    
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_5_clicked(self, button):
        if self.chan_tog[4]:
            self.chan_tog[4] = False
            self.ch_5_ref.setData([],[])
        else:
            self.chan_tog[4] = True
            self.ch_5_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[4, 0:self.iter_count-1])    
            
            
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_9_clicked(self, button):
        if self.chan_tog[8]:
            self.chan_tog[8] = False
            self.ch_9_ref.setData([],[])
        else:
            self.chan_tog[8] = True
            self.ch_9_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[8, 0:self.iter_count-1])  
            

    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_10_clicked(self, button):
        if self.chan_tog[9]:
            self.chan_tog[9] = False
            self.ch_10_ref.setData([],[])
        else:
            self.chan_tog[9] = True
            self.ch_10_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[9, 0:self.iter_count-1])  
            

    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_11_clicked(self, button):
        if self.chan_tog[10]:
            self.chan_tog[10] = False
            self.ch_11_ref.setData([],[])
        else:
            self.chan_tog[10] = True
            self.ch_11_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[10, 0:self.iter_count-1])  
            
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_12_clicked(self, button):
        if self.chan_tog[11]:
            self.chan_tog[11] = False
            self.ch_12_ref.setData([],[])
        else:
            self.chan_tog[11] = True
            self.ch_12_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[11, 0:self.iter_count-1])  
            
            
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_13_clicked(self, button):
        if self.chan_tog[12]:
            self.chan_tog[12] = False
            self.ch_13_ref.setData([],[])
        else:
            self.chan_tog[12] = True
            self.ch_13_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[12, 0:self.iter_count-1])  


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def channel_16_clicked(self, button):
        if self.chan_tog[15]:
            self.chan_tog[15] = False
            self.ch_16_ref.setData([],[])
        else:
            self.chan_tog[15] = True
            self.ch_16_ref.setData(self.plot_temp[16, 0:self.iter_count-1], self.plot_temp[15, 0:self.iter_count-1])  
            
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_temp_update(self):
        print('Attempting to Grab Temperatures...')
        temp_up = yield(self.queue_work(self._primary_worker,'new_temps'))
        for ch in range(self.numSensors):
            chName = ch+1
            self.temp[ch].setText('%s C' %(temp_up[str(chName)]))
        
    
    @define_state(MODE_TRANSITION_TO_MANUAL,True)      
    def temp_shot_update(self):
        print('Attempting to Grab Temperatures...')
        temp_up = yield(self.queue_work(self._primary_worker,'temp_return'))
        for ch in range(self.numSensors):
            chName = ch+1
            self.temp[ch].setText('%s C' %(temp_up[str(chName)]))
    
    # @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    # def status_update_clicked(self, button):
    #     #self.ui.digital_reset.setEnabled(False)
    #     self.grab_status_update()
        
        
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_status_update(self):
        print('Updating Interlock Status...')
        stat_up = yield(self.queue_work(self._primary_worker,'new_stat'))
        intlock_trigger = str(stat_up)[0:4]
        if intlock_trigger == "Fals":
            icon = QtGui.QIcon(':/qtutils/fugue/tick-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
        elif intlock_trigger == "True":
            icon = QtGui.QIcon(':/qtutils/fugue/cross-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
        else:
            icon = QtGui.QIcon(':/qtutils/fugue/question')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_update.setText('%s' %(intlock_trigger))

    
    @define_state(MODE_TRANSITION_TO_MANUAL,True)      
    def stat_shot_update(self):
        print('Updating Interlock Status...')
        stat_up = yield(self.queue_work(self._primary_worker,'stat_return'))
        intlock_trigger = str(stat_up)[0:4]
        if intlock_trigger == "Fals":
            icon = QtGui.QIcon(':/qtutils/fugue/tick-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
        elif intlock_trigger == "True":
            icon = QtGui.QIcon(':/qtutils/fugue/cross-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
        else:
            icon = QtGui.QIcon(':/qtutils/fugue/question')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_update.setText('%s' %(intlock_trigger))
 
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_setpoints(self):
        print('Attempting to Grab Setpoints...')
        set_update = yield(self.queue_work(self._primary_worker,'new_setpoints'))
        for ch in range(self.numSensors):
            chName = ch+1
            self.setpoint[ch].setText('%s C' %(set_update[str(chName)]))
        
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


    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)
    def initial_grab(self):
        yield(self.queue_work(self._primary_worker,'initial_packet'))

    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_packet_update(self):
        print('Attempting to Grab Temperatures and Status...')
        temp_up, sets_up, stat_up = yield(self.queue_work(self._primary_worker,'new_packet', verbose = False))
        for ch in range(self.numSensors):
            chName = ch+1
            self.temp[ch].setText('%s C' %(temp_up[str(chName)]))
            self.setpoint[ch].setText('%s C' %(sets_up[str(chName)]))
        intlock_trigger = str(stat_up)[0:4]
        if intlock_trigger == "Fals":
            icon = QtGui.QIcon(':/qtutils/fugue/tick-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
        elif intlock_trigger == "True":
            icon = QtGui.QIcon(':/qtutils/fugue/cross-circle')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
        else:
            icon = QtGui.QIcon(':/qtutils/fugue/question')
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
            self.ui.status_icon.setPixmap(pixmap)
            self.ui.status_update.setText('%s' %(intlock_trigger))
        #create plot of ch1-ch5 temp    
        # self.plot_temp_ch1.append(temp_up['1'])
        # self.plot_temp_ch2.append(temp_up['2'])
        # self.plot_temp_ch3.append(temp_up['3'])
        # self.plot_temp_ch4.append(temp_up['4'])
        # self.plot_temp_ch5.append(temp_up['5'])
        # self.plot_time.append(int(time.time()-self.plot_start))
        # if self.iter_count > self.graph_points:
        #     self.iter_count = 1440
        #     self.plot_temp_ch1 = np.roll(self.plot_temp_ch1, -1)
        #     self.plot_temp_ch2 = np.roll(self.plot_temp_ch2, -1)
        #     self.plot_temp_ch3 = np.roll(self.plot_temp_ch3, -1)
        #     self.plot_temp_ch4 = np.roll(self.plot_temp_ch4, -1)
        #     self.plot_temp_ch5 = np.roll(self.plot_temp_ch5, -1)
        #     self.plot_time = np.insert(self.plot_time, -1)
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
            self.temp[ch].setText('0.00 C ')
    
    
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL,True)    
    def shot_read_check(self):
        #print('Checking for shots...')
        self.shot_read = yield(self.queue_work(self._primary_worker,'shot_check'))
   
        
    @define_state(MODE_MANUAL,True)
    def on_const_temps(self, button):
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

            
    # # This function gets the status of the Pulseblaster from the spinapi,
    # # and updates the front panel widgets!
    # @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL,True)  
    # def status_monitor(self):
    #     self.status = yield(self.queue_work(self._primary_worker,'check_status')) 
            

    #     # Update widgets with new status
    #     for state in self.status_states:
    #         if self.status[state]:
    #             icon = QtGui.QIcon(':/qtutils/fugue/tick')
    #         else:
    #             icon = QtGui.QIcon(':/qtutils/fugue/cross')
            
    #         pixmap = icon.pixmap(QtCore.QSize(16, 16))
    #         self.status_widgets[state].setPixmap(pixmap)

