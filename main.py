# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:12:09 2016
Updated on Sun Apr 10
Version = 0.3
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
import numpy

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
    data = ListProperty([])
    recv_stream = ObjectProperty(None)
    #exception = StringProperty(None)
    data_thread = ObjectProperty(None)
    spike_threshold = NumericProperty(None)
    H1 = ListProperty([])
    N1 = ListProperty([])
    
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
    
    def search_for_devices(self):
        self.popup=Popup(title='Paired devices', size_hint = [0.8, 0.8],
                         on_open=self.ids.popup2.dismiss)
        btns = self.discover()
        popup_grid = GridLayout(rows = len(btns))
        for btn in btns:        
            popup_grid.add_widget(btn) 
        self.popup.add_widget(popup_grid)
        self.popup.open()
        
    def H1_indices(data, spike_threshold):
        result = []
        for i in xrange(0, len(data)-1):
            if data[i] > spike_threshold and data[i] > data[i - 1] and data[i] >= data[i + 1]:
                result.append(i)
        return numpy.array(result, dtype = int)
    
    # Locate indices for Notch 1 (N1)
    def N1_indices(data, H1):
        result = []
        for i in xrange(0, len(H1) - 1):
            # fist local minimum after H1 as the notch
            pt = next(j for j in xrange(H1[i], H1[i+1]+1) if data[j] <= data[j - 1] and data[j] <= data[j + 1])
            result.append(pt)
        return numpy.array(result, dtype = int)
        
    # Locate indices of P2 peaks
    #def H2_indices(data, H1, N1):
    #    result = []
    #    # in between each spike there is a mini-peak. find it
    #    for i in xrange(0, len(H1)):
    #        # these are subthreshold places where it goes from increasing to decreasing
    #        d = data[H1[i]:N1[i]]
    #        d = signal.savgol_filter(d, 5, 2, 2)
    #        pt = next(j for j in xrange(1,(len(d) - 1)) if d[j-1] >= 0 and d[j+1] <= 0)
    #        result.append(int(range(H1[i],N1[i])[pt]))
    #    return numpy.array(result, dtype = int)
        
    def update(self, outfile, dt):
        
        try:
            BluetoothSocket.isConnected()
        except Exception:
            pass
        else:
            if BluetoothSocket.isConnected() and self.data_thread is None:
                self.data_thread = threading.Thread(target = self.data_logging, args = (outfile,))
                self.data_thread.setDaemon(True)
                self.data_thread.start()
    
                    
        # Plot data in real time
        try:
            self.graph.remove_plot(self.plot)
            #self.data = random.sample(range(0,1024), 300) #mock data
            self.plot.points = zip(range(1, len(self.data)+1), self.data)#[( x, sin(x / 10.)) for x in range(0, int(200*random.random()) )] # This is just some mock data
            self.graph.add_plot(self.plot)
        except Exception:
            pass
        
        try:
            #x = random.sample(xrange(1,100), 10)
            self.spike_threshold = int(numpy.mean(self.data) + numpy.std(self.data))
        except Exception:
            pass
        
        try:
            self.H1 = self.H1_indices(self.data, self.spike_threshold)
        except Exception:
            pass
        
        try:
            self.N1 = self.N1_indices(self.data, self.spike_threshold)
        except Exception:
            pass
        
        
    def data_logging(self, outfile):
        recv_stream = BufferedReader(InputStreamReader(BluetoothSocket.getInputStream()))
        while recv_stream.readLine is not None:
            d = recv_stream.readLine()
            try:
                self.data.append(float(d[:4]))
                self.data = self.data[-300:] #plot the latest 300 data points in real-time
                self.data = numpy.array(self.data)
            except Exception:
                pass
            now = time.time()
            outfile.write(str(now) + "," + str(d)  + "\n")
        
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
