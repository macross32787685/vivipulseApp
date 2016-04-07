# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:12:09 2016

@author: zhen
"""

import os
import sys
from kivy.app import App
from kivy.uix.widget import Widget
from math import sin
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.garden.graph import MeshLinePlot
from functools import partial
import random
import time
from jnius import autoclass

#BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
#BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
#UUID = autoclass('java.util.UUID')
# Create a listener function
class ViViChart(Widget):
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    paired_device = StringProperty('No Paired Device')

    def __init__(self):
        super(ViViChart, self).__init__()
        graph_theme = {'background_color': 'f8f8f2'}
        self.graph = self.ids.graph
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = []
        self.graph.add_plot(self.plot)
        self.start = time.time()               
    
    def get_socket_stream(self):
        paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()        
        return str(len(paired_devices))
        #paired_devices = [random.random(), random.random()]         
        #socket = None
        #for device in paired_devices:
        #    return device.getName()
            #if device.getName() == name:
            #    socket = device.createRfcommSocketToServiceRecord(
            #        self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
            #    recv_stream = socket.getInputStream()
            #    break
        #socket.connect()
        #return recv_stream
    
    
    def update(self, outfile, dt):
        # Plot data in real time
        self.graph.remove_plot(self.plot)
        self.plot.points = [( x, sin(x / 10.)) for x in range(0, int(200*random.random()) )] # This is just some mock data
        self.graph.add_plot(self.plot)
        self.paired_device = self.get_socket_stream()
        
        # Data logging
        now = time.time() - self.start # Generate a time stamp
        data = ' ' #self.recv_stream
        outfile.write(str(now) + "," + str(data)  + "\n")
        sys.stdout.write(".")
        sys.stdout.flush()
        #self.DataHandler(self, outfile)

   # btn1 = Button(text="Bluetooth")

class ViViTestApp(App):
    def build(self):
        # Clear and open the data file for writing
        outfile = open("data.csv", "w")
        # Write a header to the text file first thing
        outfile.write("Time, Data\n")
        chart = ViViChart()
        Clock.schedule_interval(partial(chart.update, outfile), 1.0 / 60.0)
        return chart
     
    def exit(self):
        exit()

if __name__ == '__main__':
    ViViTestApp().run()