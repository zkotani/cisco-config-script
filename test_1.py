import sys, getopt
import tempfile
import subprocess
import serial

with open('DLS1_config.txt', 'r', encoding='utf-8') as sw_config:
    conf_lines = sw_config.read()

conf_list = conf_lines.split('\n')
print(conf_list)


ser = serial.Serial('/dev/ttyUSB0')
ser.write(b'enable\r\nconfigure terminal\r\n')
for line in conf_list:
    line_b = line.encode()
    ser.write(line_b + b'\r\n')
ser.close()
