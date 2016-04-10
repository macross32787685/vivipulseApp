# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:12:09 2016

@author: zhen
"""

import os
import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from math import sin
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.garden.graph import MeshLinePlot
from functools import partial
import random
import time
from jnius import autoclass

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
#BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
#BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
UUID = autoclass('java.util.UUID')
# Create a listener function
class ViViChart(Widget):
    paired_device = StringProperty('No Paired Device')
    n_paired_devices = NumericProperty(0)
    data = NumericProperty(0)
    
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
        #self.paired_device = self.get_socket_stream()
        #self.n_paired_devices = self.get_socket_stream()
        # Data logging
        now = time.time() - self.start # Generate a time stamp
        data = ' ' #self.recv_stream
        outfile.write(str(now) + "," + str(data)  + "\n")
        sys.stdout.write(".")
        sys.stdout.flush()
        #self.DataHandler(self, outfile)
class Device(Button):
    def on_release(self):
        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        for device in paired_devices:
            if device.getName() == self.text:
                socket = device.createRfcommSocketToServiceRecord(
                    UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                break
        recv_stream = socket.getInputStream()
        return recv_stream

class ViViTestApp(App):
    def build(self):
        # Clear and open the data file for writing
        outfile = open("vivipulse_data.csv", "w")
        # Write a header to the text file first thing
        outfile.write("Time, Data\n")
        chart = ViViChart()
        Clock.schedule_interval(partial(chart.update, outfile), 1.0 / 60.0)
        return chart
     
    def exit(self):
        exit()

if __name__ == '__main__':
    ViViTestApp().run()