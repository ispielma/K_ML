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
import numpy as np
import threading, time
from qtutils import UiLoader, inmain_decorator
from qtutils.qt import QtWidgets, QtGui, QtCore
from labscript_utils.qtwidgets.toolpalette import ToolPaletteGroup
import pyqtgraph as pg

#@BLACS_tab
class Arduino_TEC_Control_Tab(DeviceTab):

#Big function that sets the GUI on blacs and prepares any necessary variables, lists, dictionaries, etc. - called on start-up
    def initialise_GUI(self):
        #sets layout to blacs tab layout
         layout = self.get_tab_layout()
         
         # Loads GUI for interlock from ui document made in QT Designer
         ui_filepath = os.path.join(
             os.path.dirname(os.path.realpath(__file__)), 'controller_GUI.ui'
         )
         self.ui = UiLoader().load(ui_filepath)       #loads filepath and sets as variable for convenient calling
         
         #Creates a scrollArea widget and adds the interlock ui inside 
         #      (allows ui window to be viewed  in smaller frame while maintaining size policies)
         scrollArea = QtWidgets.QScrollArea()
         scrollArea.setWidget(self.ui)

         #variables to be used later
         
         self.contin_on = False           #flag for pausing auto-loop
         
         self.temp_check_flag = False           #flag to indicate the need to start a new auto-loop thread
         self.pid_toggle = True           #toggle flag for interlock controls sub-tab
         self.tec_toggle = True           #toggle flag for channel monitor sub-tab
         self.gra_toggle = True           #toggle flag for temperature graph sub-tab
         self.auto_go = False         #flag for killing auto-loop thread
         
         #lists for storing values, GUI elements, properties, etc.
         self.chanCol = []          #stores channel active colors for convenient and iterative calling
         self.chanDisCol = []          #stores channel disable colors for convenient and iterative calling
         self.chanHovCol = []          #stores channel hover colors for convenient and iterative calling
         
         self.temp_tog = True
         self.volt_tog = True
         
         self.last_setpoint = 0
         self.last_kp = 0
         self.last_ki = 0
         self.last_kd = 0

         #integer variables for graphing
         self.loop_time = 0         #starts a time count for the graph
         self.iter_count = 0          #counts the number of iterations (to keep track of points on the graph)
         self.max_graph_points = 21600          #maximum points to be saved for temp graphing
         self.plot_temp = np.zeros([2, 1])             #creates an arry of 2 rows with 0s as the entries
         self.plot_start = 0                #begins the plotting time at zero seconds
         
         #adds the scrollArea widget (containing the interlock GUI) into the layout
         layout.addWidget(scrollArea)
         self.graph_widget = self.ui.graph_widget  #create graph widget and redefine for more convenient calling

         # define the data in the graph widget
         title = "TEC Temp Graph"
         plt = self.graph_widget        # create plot window object
         plt.showGrid(x = True, y = True) 
         plt.setLabel('left', 'Temperature', units ='degC')         #Note: defining units this way allows for autoscaling
         plt.setLabel('bottom', 'Time', units ='sec')
         plt.setTitle(title)
         
         #create a reference line to plot for each active channel and define attributes
         self.temp_ref = self.graph_widget.plot(self.plot_temp[1], self.plot_temp[0], pen ='r', name ='Temp') #red
         #self.volt_ref = self.graph_widget.plot(self.plot_temp[1], self.plot_temp[0], pen ='y', name ='Volt') #yellow

         #create lists for a general sub-tab function to use         
         self.sub_tab_button = [self.ui.pid_controls, self.ui.tec_controls, self.ui.tec_graph]        
         self.tab_toggle = [self.pid_toggle, self.tec_toggle, self.gra_toggle]
         self.sub_tab = [self.ui.pid_box, self.ui.tec_box, self.ui.graph_widget]


         # # Connect the appropriate signals for buttons
         #Connect clicked signal to the appropriate function for each respective sub-tab
         self.ui.pid_controls.clicked.connect(lambda: self.sub_tab_clicked(0))
         self.ui.tec_controls.clicked.connect(lambda: self.sub_tab_clicked(1))
         self.ui.tec_graph.clicked.connect(lambda: self.sub_tab_clicked(2))
         
         
         # #Connect clicked signal to the appropriate function for the auto-loop start/stop buttons
         # self.ui.start_continuous.clicked.connect(self.on_const_temps)
         # self.ui.stop_continuous.clicked.connect(self.off_const_temps)
          
         
         #Connect clicked signal to the appropriate function for each respective channel monitor button
         self.ui.temp_button.clicked.connect(self.temp_clicked)
         self.ui.volt_button.clicked.connect(self.volt_clicked)
         
        
        #Set parameters for spinboxes
         self.ui.kp_adjust.setRange(0.00,20.00)   #Sets the range of the kp share spinbox
         self.set_kp = 0   #creates a placeholder value for each spinbox and stores in self.set_setpoint_vals
         
         self.ui.ki_adjust.setRange(0.00,20.00)   #Sets the range of the kp share spinbox
         self.set_ki = 0   #creates a placeholder value for each spinbox and stores in self.set_setpoint_vals
         
         self.ui.kd_adjust.setRange(0.00,20.00)   #Sets the range of the kp share spinbox
         self.set_kd = 0   #creates a placeholder value for each spinbox and stores in self.set_setpoint_vals
         
         self.ui.temp_setpoint_adjust.setRange(0,80)   #Sets the range of the kp share spinbox
         self.set_setpoint = 0   #creates a placeholder value for each spinbox and stores in self.set_setpoint_vals
         
         
         #Connect editingFinished signal to the appropriate function for each respective adjustment spinbox
         self.ui.kp_adjust.editingFinished.connect(self.send_kp)
         self.ui.ki_adjust.editingFinished.connect(self.send_ki)
         self.ui.kd_adjust.editingFinished.connect(self.send_kd)
         self.ui.temp_setpoint_adjust.editingFinished.connect(self.send_temp_setpoint)

         
         # #Sets icons and tool-tip for start / stop continuous buttons
         # self.ui.start_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control'))
         # self.ui.start_continuous.setToolTip('Starts Automatic Updating of Temperatures, Graph, and Status')
         # self.ui.stop_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control-stop-square'))
         # self.ui.stop_continuous.setToolTip('Ends Automatic Updating of Temperatures, Graph, and Status')
         
         #Set icons and tool-tip for sub-tab buttons
         self.ui.pid_controls.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.pid_controls.setToolTip('Click to hide')
         self.ui.tec_controls.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.tec_controls.setToolTip('Click to hide')
         self.ui.tec_graph.setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
         self.ui.tec_graph.setToolTip('Click to hide')
    

         #define strings for gradient color background
         self.TempCol = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 0, 0, 255), stop:1 rgba(255, 0, 0, 255))"
         self.VoltCol = "qlineargradient(spread:pad, x1:0.489, y1:0.00568182, x2:0.489, y2:0.482955, stop:0 rgba(220, 220, 0, 255), stop:1 rgba(255, 255, 0, 255))"
 
         #Adds the channel colors as items in a list for convenient calling (they are such long strings, so this happens in 2 steps)
         self.chanCol = [self.TempCol, self.VoltCol]
         
         #Adds the channel disabled colors as items in a list for convenient calling
         self.chanDisCol = ["#8c0000", "#9a9a00"]

         #Adds the channel disabled colors as items in a list for convenient calling
         self.chanHovCol = ["#aa0000", "#b8b800"]

         
     #define attributes of the channel monitor button corresponding to a particular line on the graph
         self.ui.temp_button.setText("Temperature \n 0.00 C")
         self.ui.temp_button.setStyleSheet("background-color : %s;border-style: solid;border-width: 1px;"
                                               "border-color: gray;border-radius: 3px" %(self.chanCol[0])) 
         self.ui.volt_button.setText("Output Voltage \n 0.00 C")
         self.ui.volt_button.setStyleSheet("background-color : %s;border-style: solid;border-width: 1px;"
                                               "border-color: gray;border-radius: 3px" %(self.chanCol[1])) 
         
         self.ui.kp_marker.setText("Kp \n (Proportional Share)")
         self.ui.ki_marker.setText("Ki \n (Integral Share)")
         self.ui.kd_marker.setText("Kd \n (Derivative Share)")
        
         #hides a blank widget used for spacing (the widget pushes the other subtabs when the temp graph is hidden)
         self.ui.push_widg.hide()
         
         
#function used by blacs/labscript to load device worker -automatically called upon start-up
    def initialise_workers(self):
        worker_initialisation_kwargs = self.connection_table.find_by_name(self.device_name).properties
        worker_initialisation_kwargs['addr'] = self.BLACS_connection
        self.create_worker(
            'main_worker',
            'user_devices.Arduino_TEC_Control.blacs_workers.Arduino_TEC_Control_Worker',
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
        self.full_packet = yield(self.queue_work(self._primary_worker,'initial_packet'))
        self.ui.temp_button.setText("%s \n %s C" %('Temperature', self.full_packet[0]))
        self.tec_volt = (float(self.full_packet[1]) - 1.65)*10 
        self.ui.volt_button.setText("%s \n %.2f V" %('Output_Voltage', round(self.tec_volt,2)))
        if float(self.full_packet[2]) != self.last_setpoint:
            self.ui.temp_setpoint_adjust.setValue(float(self.full_packet[2]))
            self.last_setpoint = float(self.full_packet[2])
        if float(self.full_packet[5]) != self.last_kp:
            self.ui.kp_adjust.setValue(float(self.full_packet[5]))
            self.last_kp = float(self.full_packet[5])
        if float(self.full_packet[6]) != self.last_ki:
            self.ui.ki_adjust.setValue(float(self.full_packet[6]))
            self.last_ki = float(self.full_packet[6])
        if float(self.full_packet[7]) != self.last_kd:
            self.ui.kd_adjust.setValue(float(self.full_packet[7]))
            self.last_kd = float(self.full_packet[7])
        self.on_const_up()    
 

    #takes a signal from a sub-tab button and toggles the sub-tab between shown and hidden
    def sub_tab_clicked(self, ID):
        if self.tab_toggle[ID]:
            self.sub_tab[ID].hide()
            if ID == 2:
                self.ui.push_widg.show()
            self.tab_toggle[ID] = False
            self.sub_tab_button[ID].setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small-expand'))
            self.sub_tab_button[ID].setToolTip('Click to show')
        else:
            self.sub_tab[ID].show()
            if ID == 2:
                self.ui.push_widg.show()
            self.tab_toggle[ID] = True
            self.sub_tab_button[ID].setIcon(QtGui.QIcon(':/qtutils/fugue/toggle-small'))
            self.sub_tab_button[ID].setToolTip('Click to hide')
              
        
    # Function that toggles the temperature button 
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def temp_clicked(self, ch=0):
        if self.temp_tog:
            self.temp_tog = False
            self.temp_ref.setData([],[])
            color = self.chanDisCol[0]
            colorHov = self.chanHovCol[0]
            self.ui.temp_button.setToolTip('Click to Show on Graph')                                                   
        else:
            self.temp_tog = True
            self.temp_ref.setData(self.plot_temp[1, 1:self.iter_count], self.plot_temp[0, 1:self.iter_count])
            color = self.chanCol[0]
            colorHov = ''
            self.ui.temp_button.setToolTip('Click to Hide from Graph')
        self.ui.temp_button.setStyleSheet("""QPushButton{background-color : %s; border-style: solid;
                        border-width: 1px;border-color: gray;border-radius: 3px;}
                        QPushButton::hover {background-color: %s;}""" %(color, colorHov))


    # Function that toggles the output voltage button 
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def volt_clicked(self, ch=1):
        if self.volt_tog:
            self.volt_tog = False
            #self.volt_ref.setData([],[])
            color = self.chanDisCol[1]
            colorHov = self.chanHovCol[1]
            self.ui.volt_button.setToolTip('Click to Show on Graph')                                                   
        else:
            self.volt_tog = True
            #self.volt_ref.setData(self.plot_volt[1, 1:self.iter_count], self.plot_volt[0, 1:self.iter_count])
            color = self.chanCol[1]
            colorHov = ''
            self.ui.volt_button.setToolTip('Click to Hide from Graph')
        self.ui.volt_button.setStyleSheet("""QPushButton{background-color : %s; border-style: solid;
                        border-width: 1px;border-color: gray;border-radius: 3px;}
                        QPushButton::hover {background-color: %s;}""" %(color, colorHov))
                        
    
    #function for sending the compiled setpoints in the set_sendpoint_vals dictionary to the worker function
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_temp_setpoint(self):
        print('Sending New Setpoint...')
        self.set_setpoint = self.ui.temp_setpoint_adjust.value()
        yield(self.queue_work(self._primary_worker,'set_setpoint', self.set_setpoint))
    
    
    #function for sending the compiled setpoints in the set_sendpoint_vals dictionary to the worker function
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_kp(self):
        print('Sending New Setpoint...')
        self.set_kp = self.ui.kp_adjust.value()
        yield(self.queue_work(self._primary_worker,'set_Kp', self.set_kp))
        
        
    #function for sending the compiled setpoints in the set_sendpoint_vals dictionary to the worker function
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_ki(self):
        print('Sending New Setpoint...')
        self.set_ki = self.ui.ki_adjust.value()
        yield(self.queue_work(self._primary_worker,'set_Ki', self.set_ki))
        
        
    #function for sending the compiled setpoints in the set_sendpoint_vals dictionary to the worker function
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_kd(self):
        print('Sending New Setpoint...')
        self.set_kd = self.ui.kd_adjust.value()
        yield(self.queue_work(self._primary_worker,'set_Kd', self.set_kd))
    

    #function that activates the default setpoints worker function to reset setpoints to the arduino's default values
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def send_default(self):
        print('Sending New Setpoints...')
        yield(self.queue_work(self._primary_worker,'set_defaults'))

    
    #function used by auto-loop to grab a new packet of temperatures, setpoint, and status and then update the blacs tab 
    #       with the appropriate values/ information
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def grab_packet_update(self):
        print('Attempting to Grab Temperature and Voltage...')
        self.full_packet = yield(self.queue_work(self._primary_worker,'new_packet', verbose = False)) #grab the new packets from the worker
        
        #set the buttons and spinboxes with the appropriate updated information
        self.ui.temp_button.setText("%s \n %s C" %('Temperature', self.full_packet[0]))
        self.tec_volt = (float(self.full_packet[1]) - 1.65)*10 
        self.ui.volt_button.setText("%s \n %.2f V" %('Output_Voltage', round(self.tec_volt,2)))
        if float(self.full_packet[2]) != self.last_setpoint:
            self.ui.temp_setpoint_adjust.setValue(float(self.full_packet[2]))
            self.last_setpoint = float(self.full_packet[2])
        if float(self.full_packet[5]) != self.last_kp:
            self.ui.kp_adjust.setValue(float(self.full_packet[5]))
            self.last_kp = float(self.full_packet[5])
        if float(self.full_packet[6]) != self.last_ki:
            self.ui.ki_adjust.setValue(float(self.full_packet[6]))
            self.last_ki = float(self.full_packet[6])
        if float(self.full_packet[7]) != self.last_kd:
            self.ui.kd_adjust.setValue(float(self.full_packet[7]))
            self.last_kd = float(self.full_packet[7])
        
        #Update the temperature graph with the new temperature data for each channel's line      
        #       check for the maximum points on the graph, and if reached, remove the oldest column of data
        if self.iter_count > (self.max_graph_points):
            self.iter_count = self.max_graph_points
            self.plot_temp = np.delete(self.plot_temp, [0], axis = 1)
        
        #add the new temperature and time to the data array    
        self.plot_temp = np.insert(self.plot_temp, self.iter_count, [self.full_packet[0],
                                                                     int(time.time()-self.plot_start)], axis=1)
        #self.plot_volt (or maybe will be part of some self.plot_tec)
        
        #for each channel: if the button is active, plot the channel's temperature line
        if self.temp_tog:
            self.temp_ref.setData(self.plot_temp[1, 1:self.iter_count+1], self.plot_temp[0, 1:self.iter_count+1])
        # if self.volt_tog:
        #     self.volt_ref.setData(self.plot_volt[1, 1:self.iter_count+1], self.plot_temp[0, 1:self.iter_count+1])
       #increase point count by 1
        self.iter_count += 1


    #function for reuqesting the packet from the worker during a shot    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)      
    def packet_shot_update(self):
        print('Updating Temperatures and Status...')
        self.full_packet = yield(self.queue_work(self._primary_worker,'packet_return'))
        
        #set the buttons and spinboxes with the appropriate updated information
        self.ui.temp_button.setText("%s \n %s C" %('Temperature', self.full_packet[0]))
        #self.tec_volt = (self.full_packet -1.65)*10 
        self.tec_volt = (float(self.full_packet[1]) - 1.65)*10 
        self.ui.volt_button.setText("%s \n %.2f V" %('Output_Voltage', round(self.tec_volt,2)))
        if float(self.full_packet[2]) != self.last_setpoint:
            self.ui.temp_setpoint_adjust.setValue(float(self.full_packet[2]))
            self.last_setpoint = float(self.full_packet[2])
        if float(self.full_packet[5]) != self.last_kp:
            self.ui.kp_adjust.setValue(float(self.full_packet[5]))
            self.last_kp = float(self.full_packet[5])
        if float(self.full_packet[6]) != self.last_ki:
            self.ui.ki_adjust.setValue(float(self.full_packet[6]))
            self.last_ki = float(self.full_packet[6])
        if float(self.full_packet[7]) != self.last_kd:
            self.ui.kd_adjust.setValue(float(self.full_packet[7]))
            self.last_kd = float(self.full_packet[7])
   
     
    #activates the auto-loop (continuos_loop) by either creating a new thread or, if one exists, changing the
    #       contin_on flag to True
    @define_state(MODE_MANUAL,True)
    def on_const_up(self, button=0):
        print('Constant Temperature Acquisition Strarting...')  
        # self.ui.start_continuous.hide()
        # self.ui.stop_continuous.show()
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
    def off_const_up(self, button, verbose = False):
        if verbose:
            print('Stopping Constant Temperature Acquisition...')
        # self.ui.stop_continuous.hide()
        # self.ui.start_continuous.show()
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
    def continuous_loop(self, auto_go=True, interval = 2):
        self.auto_go = auto_go
        time_go = True
        while self.auto_go:
            if self.contin_on:
                self.grab_packet_update()
                time.sleep(interval)
            if time_go:
                self.plot_start = time.time()
                time_go = False

 
        