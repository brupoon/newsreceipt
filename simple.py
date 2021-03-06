"""
newsreceipt_simple.py
Copyright (c) 2015 Brunston Poon/brupoon

Written for Raspberry Pi and Adafruit Thermal Printer
Some code adapted from iworkinpixels/otp-gen
(note to self: try PEP8 for functions/classes, etc.)
"""

from __future__ import print_function
#import RPi.GPIO as GPIO
from urllib.request import urlopen
import json, webbrowser
import sys, os, random, getopt, re
import subprocess, time, socket
#from Adafruit_Thermal import *
import feedparser


"""Initialization"""

# led_pin = 18
# button_pin = 23
# hold_time = 3     # Duration for button hold (shutdown)
# tap_time = 0.01  # Debounce time for button taps
# printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
# printer.setLineHeight(23) # So graphical characters fit together
#
# # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
# GPIO.setmode(GPIO.BCM)
# # Enable LED and button (w/pull-up on latter)
# GPIO.setup(led_pin, GPIO.OUT)
# GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# # LED on while working
# GPIO.output(led_pin, GPIO.HIGH)
# # Processor load is heavy at startup; wait a moment to avoid
# # stalling during greeting.
# time.sleep(30)
#
# # Show IP address (if network is available)
# try:
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(('8.8.8.8', 0))
#     # printer.println('My IP address is ' + s.getsockname()[0])
#     # printer.boldOn()
#     # printer.println('Network connected.')
#     # printer.boldOff()
#     # printer.feed(3)
# except:
#     printer.boldOn()
#     printer.println('Network not connected.')
#     printer.boldOff()
#     printer.feed(3)
#

# GPIO.output(led_pin, GPIO.LOW)
#
# # Poll initial button state and time
# prev_button_state = GPIO.input(button_pin)
# prev_time = time.time()
# tap_enable = False
# hold_enable = False

"""End Initialization"""

"""Text Generation & Button Parsing"""

def generate_rcpt():
    #generates news receipt

    #Gets API and User information
    with open("dat/settings.cfg") as file:
        cfg_list = [line.rstrip('\n') for line in file]
    weather_key = cfg_list[0]
    username = cfg_list[1]
    weather_loc = cfg_list[2]
    news_source = cfg_list[3]
    news_source_name = cfg_list[4]
    news2_source = cfg_list[5]
    news2_source_name = cfg_list[6]

    #get weather (current and forecast of the day)
    weather_str_current = str('http://api.wunderground.com/api/'+weather_key+\
                      '/geolookup/conditions/q/'+weather_loc+'.json')
    f = urlopen(weather_str_current)
    json_string = f.read()
    json_middleman = json_string.decode('utf-8')
    weather_current = json.loads(json_middleman)

    weather_str_forc = str('http://api.wunderground.com/api/'+weather_key+\
                      '/geolookup/forecast/q/'+weather_loc+'.json')
    f = urlopen(weather_str_forc)
    json_string = f.read()
    json_middleman = json_string.decode('utf-8')
    weather_forc = json.loads(json_middleman)

    #get news
    news_data = feedparser.parse(news_source)
    news2_data = feedparser.parse(news2_source)

    #header
    with open("news_rcpt_head.txt", "w") as file:
        file.write("***The Newsreceipt***\n")
        file.write("Time of Generation:\n")
        file.write(time.asctime() + "\n\n")
        file.write("Hello, " + username + "!\n")

    #news, weather
    with open("news_rcpt.txt", "w") as file:
        file.write("\n\n---Weather---\n\n")
        file.write("Weather in " + weather_current["location"]["city"] + ":\n")
        file.write(weather_current["current_observation"]["weather"] + " and "+\
                   str(weather_current["current_observation"]["temp_f"]) + " deg.\n")

        file.write("Forecast in " + weather_forc["location"]["city"] + ":\n")
        file.write(weather_forc["forecast"]["txt_forecast"]["forecastday"][0]["fcttext"] + "\n")

        file.write("\n\n---News from {0}---\n\n".format(news_source_name))
        for i in range(10):
            file.write("[{0}]:".format(i+1) + news_data.entries[i].title + "\n")
            #file.write(news_data.entries[i].description + "\n")
        file.write("\n\n---News from {0}---\n\n".format(news2_source_name))
        for i in range(10):
            file.write("[{0}]:".format(i+1) + news2_data.entries[i].title + "\n")
            #file.write(news_data.entries[i].description + "\n")

def text_setter():
    #makes sure all text will fit on the line, using new line.
    f1 = open("news_rcpt_head.txt", "r")
    f2 = open("news_rcpt_head.txt.tmp", "w")
    for line in f1:
        if len(line) > 32:
            line_list = [line[i:i+31] for i in range(0, len(line), 31)]
            for adj_line in range(len(line_list)):
                if adj_line != len(line_list):
                    f2.write(line_list[adj_line] + "-\n")
                else:
                    f2.write(line_list[adj_line])
        else:
            f2.write(line)
    f1.close()
    f2.close()
    os.remove('news_rcpt_head.txt')
    os.rename('news_rcpt_head.txt.tmp', 'news_rcpt_head.txt')

    f1 = open("news_rcpt.txt", "r")
    f2 = open("news_rcpt.txt.tmp", "w")
    for line in f1:
        if len(line) > 32:
            line_list = [line[i:i+31] for i in range(0, len(line), 31)]
            for adj_line in range(len(line_list)):
                if adj_line != len(line_list):
                    f2.write(line_list[adj_line] + "-\n")
                else:
                    f2.write(line_list[adj_line])
        else:
            f2.write(line)
    f1.close()
    f2.close()
    os.remove('news_rcpt.txt')
    os.rename('news_rcpt.txt.tmp', 'news_rcpt.txt')


    return None

def tap():
    # Called when button is briefly tapped.  Prints one copy of the news_rcpt.
    # GPIO.output(led_pin, GPIO.HIGH)  # LED on while working

    #generate receipt
    generate_rcpt()
    news_rcpt_head = file("news_rcpt_head.txt") #add /ramdisk/ on RPi
    news_rcpt = file("news_rcpt.txt") #add /ramdisk/ on RPi

    #print receipt
    printer.feed(3)
    printer.justify('C')
    printer.boldOn()
    for line in news_rcpt_head:
        printer.println(line)
    printer.boldOff()
    printer.justify('L')

    for line in news_rcpt:
        printer.println(line)
    printer.feed(3)

    file.close(news_rcpt)
    #GPIO.output(led_pin, GPIO.LOW)

    return None

def hold():
    # Called when button is held down.  Invokes shutdown process.
    GPIO.output(led_pin, GPIO.HIGH)
    subprocess.call(["shutdown", "-h", "now"])
    GPIO.output(led_pin, GPIO.LOW)
    return None

"""End Text Generation & Button Parsing"""

"""Main Loop"""

def main_loop():
    while(True):
      # Poll current button state and time
      button_state = GPIO.input(button_pin)
      t = time.time()

      # Has button state changed?
      if button_state != prev_button_state:
        prev_button_state = button_state   # Yes, save new state/time
        prev_time = t
      else:                             # Button state unchanged
        if (t - prev_time) >= hold_time:  # Button held more than 'hold_time'?
          # Yes it has.  Is the hold action as-yet untriggered?
          if hold_enable == True:        # Yep!
            hold()                      # Perform hold action (usu. shutdown)
            hold_enable = False          # 1 shot...don't repeat hold action
            tap_enable = False          # Don't do tap action on release
        elif (t - prev_time) >= tap_time: # Not hold_time.  tap_time elapsed?
          # Yes.  Debounced press or release...
          if button_state == True:       # Button released?
            if tap_enable == True:       # Ignore if prior hold()
              tap()                     # Tap triggered (button released)
              tap_enable = False        # Disable tap and hold
              hold_enable = False
          else:                         # Button pressed
            tap_enable = True           # Enable tap and hold actions
            hold_enable = True

      # LED blinks while idle, for a brief interval every 2 seconds.
      # Pin 18 is PWM-capable and a "sleep throb" would be nice, but
      # the PWM-related library is a hassle for average users to install
      # right now.  Might return to this later when it's more accessible.
      if ((int(t) & 1) == 0) and ((t - int(t)) < 0.15):
        GPIO.output(led_pin, GPIO.HIGH)
      else:
        GPIO.output(led_pin, GPIO.LOW)

if __name__ == '__main__':
    # generate_rcpt()
    # text_setter()
    ask = input("Press Enter to Print, any letter to cancel.")
    if ask == "":
        tap()
    # main_loop()
