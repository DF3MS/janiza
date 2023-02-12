#!/usr/bin/python3
# ----------------------------------------------------- #
#                                                       #
# Skript zum Auffinden von Janitza UMG96                #
# Konfiguration erfolgt am unteren Ende :-)             #
#                                                       #
# Bei Fragen: mail-janitza@f50hz.de                     #
#                                                       #
# Matthias Schlecht 2022-2023                           #
#                                                       #
# ----------------------------------------------------- #

import janitza_methods as jm

#Modbus-Client definieren
client=jm.establish_modbus("/dev/ttyUSB0",timeout=0.1,baudrate=9600)

# Einmal die Addressrange definiert und los gehts.

devices=jm.search_devices(client,range(1,20))
client.timeout=2
jm.get_device_info(client,devices)

