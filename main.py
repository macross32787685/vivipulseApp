# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:12:09 2016
Updated on Sun Apr 10
Version = 0.25
@author: zhen

Update note:
Connecting to Bluetooth device and receive streams of data enabled
"""
#TODO: 1. Fix BufferedReader readLine incomplete issue (DONE!!!)
#TODO: 2. Incoporate codes from Harrison 
#TODO: 3. Improve on API 
#TODO: 4. Establish app as service so it runs in backgroud

import os
import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from math import sin
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.garden.graph import MeshLinePlot
from functools import partial
import random
import time
from jnius import autoclass
import threading

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
InputStreamReader = autoclass('java.io.InputStreamReader')
BufferedReader = autoclass('java.io.BufferedReader')
UUID = autoclass('java.util.UUID')

# Create a listener function
class ViViChart(Widget):
    paired_device = StringProperty('No Paired Device')
    n_paired_devices = NumericProperty(0)
    data = StringProperty(0)
    recv_stream = ObjectProperty(None)
    #exception = StringProperty(None)
    data_thread = ObjectProperty(None)
    
    def __init__(self):
        super(ViViChart, self).__init__()
        graph_theme = {'background_color': 'f8f8f2'}
        self.graph = self.ids.graph
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = []
        self.graph.add_plot(self.plot)
        self.start = time.time()
        
    def discover(self):
        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        btns = []
        for device in paired_devices:
            btns.append(Device(text = device.getName()))
        return btns
        '''
            if device.getName() == 'MDR-XB950BT':
                socket = device.createRfcommSocketToServiceRecord(
                    self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                recv_stream = socket.getInputStream()
                self.paired_device = 'MDR-XB950BT'
                break
        socket.connect()
        '''
    
    def search_for_devices(self):
        self.popup=Popup(title='Paired devices', size_hint = [0.8, 0.8],
                         on_open=self.ids.popup2.dismiss)
        btns = self.discover()
        popup_grid = GridLayout(rows = len(btns))
        for btn in btns:        
            popup_grid.add_widget(btn) 
        self.popup.add_widget(popup_grid)
        self.popup.open()
        #return recv_stream
        #return len(paired_devices)#, recv_stream
        
    def update(self, outfile, dt):
        # Plot data in real time
        self.graph.remove_plot(self.plot)
        self.plot.points = [( x, sin(x / 10.)) for x in range(0, int(200*random.random()) )] # This is just some mock data
        self.graph.add_plot(self.plot)
        try:
            BluetoothSocket.isConnected()
        except Exception:
            pass
        else:
            if BluetoothSocket.isConnected() and self.data_thread is None:
                self.data_thread = threading.Thread(target = self.data_logging, args = (outfile,))
                self.data_thread.setDaemon(True)
                self.data_thread.start()
                    
    def data_logging(self, outfile):
        recv_stream = BufferedReader(InputStreamReader(BluetoothSocket.getInputStream()))
        while recv_stream.readLine is not None:
            self.data = str(recv_stream.readLine())
            now = time.time()
            outfile.write(str(now) + "," + str(self.data)  + "\n")
        
        #try:
        #    while recv_stream.readLine is not None:
        #        self.graph.remove_plot(self.plot)
        #        self.plot.points = [( x, sin(x / 10.)) for x in range(0, int(200*random.random()) )] # This is just some mock data
        #        self.graph.add_plot(self.plot)
        #        self.data = str(recv_stream.readLine())
        #        outfile.write(str(now) + "," + str(self.data)  + "\n")
        #        #sys.stdout.write(".")
        #        #sys.stdout.flush()
        #except Exception:
        #    pass
        
class Device(Button):
    def on_release(self):
        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        for device in paired_devices:
            if device.getName() == self.text:
                socket = device.createRfcommSocketToServiceRecord(
                    UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                break
        try:
            socket.connect()
        except Exception:
            pass
            
class Exception_popup(Popup):
    pass

class ViViTestApp(App):
    def build(self):
        # Clear and open the data file for writing
        outfile = open(self.user_data_dir + "/vivipulse_data.csv", "w")
        # Write a header to the text file first thing
        outfile.write("Time, Data\n")
        chart = ViViChart()    
        Clock.schedule_interval(partial(chart.update, outfile), 1.0)        
        return chart
     
    def exit(self):
        exit()

if __name__ == '__main__':
    ViViTestApp().run()