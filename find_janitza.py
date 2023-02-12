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

import janitza_methods

client=establish_modbus("/dev/ttyUSB0")


# ------------------------------------------------------------------------- #
#
#  Ab hier gehts los mit der Konfig.
#
# ------------------------------------------------------------------------- #

# Einmal die Addressrange definiert und los gehts.

get_device_info(search_devices(range(1,20)))
