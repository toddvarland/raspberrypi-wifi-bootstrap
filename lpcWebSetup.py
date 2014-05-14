#!/usr/bin/env python

# 23456789 123456789 123456789 123456789 123456789 123456789 123456789 12345678
# Note - this script must be run as root - sudo do to GPIO and reboot
# 23456789 123456789 123456789 123456789 123456789 123456789 123456789 12345678

import flask, flask.views
import os
import functools
import subprocess
from subprocess import call

app = flask.Flask(__name__)

class Main(flask.views.MethodView):
    def get(self):
        return flask.render_template('index.html')
    
    def post(self):
        required = ['SSIDname', 'SSIDpwd', 'SecurityMode']
        ssidname = flask.request.form['SSIDname']
        ssidpwd = flask.request.form['SSIDpwd']
        securitymode = flask.request.form['SecurityMode']
        
        if securitymode == "WPA Personal":
            proto = "WPA1"
        elif securitymode == "WPA2 Personal":
            proto = "RSN"
        else:
            proto = "RSN"
            
        with open('/etc/wpa_supplicant/wpa_supplicant.conf','w') as f2:
            f2.write(
                'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev' +
                "\n" + 'update_config=1' + "\n" + "\n" + 'network={' + "\n" +
                'ssid="' + ssidname + '"' + "\n" + 'psk="' + ssidpwd + '"' + "\n" +
                "\n" +"# Protocol type can be: RSN (for WP2) and WPA (for WPA1)" +
                "\n" +'proto=' + proto + "\n" +"\n" +
                "# Key management type can be: WPA-PSK or WPA-EAP" + "\n" +
                'key_mgmt=WPA-PSK' + "\n" +"\n" +
                "# Pairwise can be CCMP or TKIP (for WPA2 or WPA1)" + "\n" +
                'pairwise=TKIP' + "\n" +"\n" +
                "#Authorization option should be OPEN for both WPA1/WPA2" + "\n" +
                'auth_alg=OPEN' + "\n" +'}'
            )
        
        call(["service", "hostapd", "stop"])

        with open('/etc/network/interfaces','w') as f3:
            f3.write(
                'auto lo' + "\n" +
                'iface lo inet loopback' + "\n" +
                'iface eth0 inet dhcp' + "\n" +
                'allow-hotplug wlan0' + "\n" +
                '#This is the lpc run version' + "\n" + 
                'iface wlan0 inet dhcp' + "\n" + 
                'wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf' + "\n" +
                'iface default inet dhcp'
            )

        call(["update-rc.d", "isc-dhcp-server", "remove"])
        call(["update-rc.d", "hostapd", "remove"])
        call(["mpg321", "/home/pi/lpc/run_mode.mp3"])
        call(["shutdown", "now", "-r"])
    
app.add_url_rule('/', view_func=Main.as_view('index'), methods=["GET", "POST"])
app.run(host='10.10.0.1', port=80, debug=True)