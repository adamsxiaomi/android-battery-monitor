# This Script Uses adb commands to poll the status of the phone battery. Saves data to file

import subprocess
import re
import sys
import json
import time
import threading
from datetime import datetime
import matplotlib.pyplot as plt
import argparse

DELAY = 2
VOLTAGE_STR = r'^ *voltage: (\d+)'
CURRENT_STR = r'^ *current now: (-?\d+)'
BATTERY_LEVEL = r'^ *level: (\d+)'

# Command line args
parser = argparse.ArgumentParser()
parser.add_argument('--ip')
parser.add_argument('-f', '--file')
parser.add_argument('-b', '--battery-target', type=int, required=False, default=101)
args = parser.parse_args()

# File to output values
outfile = args.file

# Determining What battery percent to stop logging
battery_setpoint = args.battery_target

logged_time = 0
start_time = time.time()
while (True):
	# Get battery info by using a system call
	battery_stats = subprocess.check_output(['adb', '-s', args.ip, 'shell', 'dumpsys', 'battery']).decode('utf-8')
	
	# Find info to write to file (relevant battery stats)
	timestamp = datetime.now().time() 
	voltage = float(re.search(VOLTAGE_STR, battery_stats, re.MULTILINE).group(1))
	current = float(re.search(CURRENT_STR, battery_stats, re.MULTILINE).group(1))
	battery_level = float(re.search(BATTERY_LEVEL, battery_stats, re.MULTILINE).group(1))

	# Ensure loop runs at specified intervals
	elapsed_time = time.time() - start_time
	time.sleep(max(0, DELAY - elapsed_time))
	start_time = time.time()
	logged_time += DELAY

	# print output to stdout as json
	f = open(outfile, 'a')
	f.write('[' + ','.join([str(logged_time), str(voltage), str(current), str(battery_level), '"' + str(timestamp) + '"', str(time.time())]) + ']'+ '\n')

	# Break if desired battery level is reached
	if battery_level >= battery_setpoint:
		break

f.close()