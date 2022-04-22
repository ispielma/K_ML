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
import threading, time
from qtutils import UiLoader#, inmain_decorator
import qtutils.icons
from qtutils.qt import QtWidgets, QtGui, QtCore

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
         self.loop_time = 0
         self.set_setpoint_vals = []
         self.adjust = []
         self.setpoint = []
         self.temp = []
         layout.addWidget(self.ui)
         
         # # Connect signals for buttons
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
         
         #Sets icons for start and stop continuous
         self.ui.start_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control'))
         self.ui.start_continuous.setToolTip('Periodic Updating of the Interlock Status and Thermocouple Temps')
         self.ui.stop_continuous.setIcon(QtGui.QIcon(':/qtutils/fugue/control-stop-square'))
         self.ui.start_continuous.setToolTip('Will Cease Periodic Updating of the Interlock Status and Thermocouple Temps')
  
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
        # intlock_trigger = str(stat_init)[0:4]
        # if intlock_trigger == "Fals":
        #     icon = QtGui.QIcon(':/qtutils/fugue/tick-circle')
        #     pixmap = icon.pixmap(QtCore.QSize(16, 16))
        #     self.ui.status_icon.setPixmap(pixmap)
        # elif intlock_trigger == "True":
        #     icon = QtGui.QIcon(':/qtutils/fugue/cross-circle')
        #     pixmap = icon.pixmap(QtCore.QSize(16, 16))
        #     self.ui.status_icon.setPixmap(pixmap)
        # else:
        #     icon = QtGui.QIcon(':/qtutils/fugue/question')
        #     pixmap = icon.pixmap(QtCore.QSize(16, 16))
        #     self.ui.status_icon.setPixmap(pixmap)
        #     self.ui.status_update.setText('%s' %(intlock_trigger))
            

    def initialise_workers(self):
        worker_initialisation_kwargs = self.connection_table.find_by_name(self.device_name).properties
        worker_initialisation_kwargs['addr'] = self.BLACS_connection
        self.create_worker(
            'main_worker',
            'user_devices.Arduino_Interlock.blacs_workers.Arduino_Interlock_Worker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'
        
        # time.sleep(2)
        # self.initial_grab()

        
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
        
        # for ch in range(self.numSensors):
        #     chName = ch+1
        #     self.setpoint[ch].setText('%s C' %(set_send[str(chName)]))
        # self.ui.chan_1_setpoint.setText('%s C' %(set_update['1']))
        # self.ui.chan_2_setpoint.setText('%s C' %(set_update['2']))
        # self.ui.chan_3_setpoint.setText('%s C' %(set_update['3']))
        # self.ui.chan_4_setpoint.setText('%s C' %(set_update['4']))
        # self.ui.chan_5_setpoint.setText('%s C' %(set_update['5']))
        # self.ui.chan_6_setpoint.setText('%s C' %(set_update['6']))
        # self.ui.chan_7_setpoint.setText('%s C' %(set_update['7']))
        # self.ui.chan_8_setpoint.setText('%s C' %(set_update['8']))
        # self.ui.chan_9_setpoint.setText('%s C' %(set_update['9']))
        # self.ui.chan_10_setpoint.setText('%s C' %(set_update['10']))
        # self.ui.chan_11_setpoint.setText('%s C' %(set_update['11']))
        # self.ui.chan_12_setpoint.setText('%s C' %(set_update['12']))
        # self.ui.chan_13_setpoint.setText('%s C' %(set_update['13']))
        # self.ui.chan_14_setpoint.setText('%s C' %(set_update['14']))
        # self.ui.chan_15_setpoint.setText('%s C' %(set_update['15']))
        # self.ui.chan_16_setpoint.setText('%s C' %(set_update['16']))
        
        # self.ui.chan_1_adjust.setValue(set_update['1'])
        # self.ui.chan_2_adjust.setValue(set_update['2'])
        # self.ui.chan_3_adjust.setValue(set_update['3'])
        # self.ui.chan_4_adjust.setValue(set_update['4'])
        # self.ui.chan_5_adjust.setValue(set_update['5'])
        # self.ui.chan_6_adjust.setValue(set_update['6'])
        # self.ui.chan_7_adjust.setValue(set_update['7'])
        # self.ui.chan_8_adjust.setValue(set_update['8'])
        # self.ui.chan_9_adjust.setValue(set_update['9'])
        # self.ui.chan_10_adjust.setValue(set_update['10'])
        # self.ui.chan_11_adjust.setValue(set_update['11'])
        # self.ui.chan_12_adjust.setValue(set_update['12'])
        # self.ui.chan_13_adjust.setValue(set_update['13'])
        # self.ui.chan_14_adjust.setValue(set_update['14'])
        # self.ui.chan_15_adjust.setValue(set_update['15'])
        # self.ui.chan_16_adjust.setValue(set_update['16'])    

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
    

    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)
    def temp_callout(self, button):
        #self.ui.digital_reset.setEnabled(False)
        print('Calling for New Temperatures...')
        yield(self.queue_work(self._primary_worker,'new_temps'))
    
    
    @define_state(MODE_MANUAL|MODE_TRANSITION_TO_MANUAL,True)    
    def temp_zero(self, button):
        #self.ui.digital_reset.setEnabled(False)
        print('Returning Temperatures to Zero...')
        for ch in range(self.numSensors):
            self.temp[ch].setText('0.00 C ')
    
    
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL,True)    
    def shot_read_check(self):
        #self.ui.digital_reset.setEnabled(False)
        #print('Checking for shots...')
        self.shot_read = yield(self.queue_work(self._primary_worker,'shot_check'))
   
        
    @define_state(MODE_MANUAL,True)
    def on_const_temps(self, button):
        #self.ui.start_continuous.setEnabled(True)
        print('Constant Temperature Acquisition Strarting...')  
        self.ui.start_continuous.hide()
        self.ui.stop_continuous.show()
        self.start_continuous()
        self.contin_on = True
        if self.temp_check_flag == False:
           # self.initial_grab()
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
        # while self.contin_on:
        #     if self.temp_check_flag:
        #         self.temp_update()
        #         self.temp_check_flag = False
    
    
    @define_state(MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL, True)
    def stop_continuous(self):
        yield(self.queue_work(self._primary_worker,'stop_continuous'))
   
    
    def continuous_loop(self):
        interval=5
        while True:
            self.shot_read_check()
            #if (time.time() - self.loop_time) > interval:
            if self.shot_read:
                #self.packet_update
                self.temp_shot_update()
                self.stat_shot_update()
            elif self.contin_on:
                self.grab_packet_update()
                #self.grab_temp_update()
                #self.grab_status_update()
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

