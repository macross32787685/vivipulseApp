# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:53:12 2016

@author: zhen
"""

import kivy
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from jnius import autoclass

Context = autoclass('android.content.Context')
PythonActivity = autoclass('org.renpy.android.PythonActivity')
activity = PythonActivity.mActivity
btManager = activity.getSystemService(Context.BLUETOOTH_SERVICE)
btAdapter = btManager.getAdapter()

class BluetoothApp(App):
    def build(self):
        Layout=BoxLayout(orientation='vertical',spacing=20,padding=(200,20))
        self.ButtonConnect=Button(text='Connect')
#        self.BoutonConnect.bind(on_press=self.connect)
        Layout.add_widget(self.ButtonConnect)
        return Layout

if __name__ == '__main__':
    BluetoothApp().run()