#!/usr/bin/python3

# ----------------------------------------------------- #
#                                                       #
# Skript zum Auslesen von Janitza UMG96                 #
# Konfiguration erfolgt am unteren Ende :-)             #
#                                                       #
# Bei Fragen: mail-janitza@f50hz.de                     #
#                                                       #
# Matthias Schlecht 2022 - 2023                         #
#                                                       #
# ----------------------------------------------------- #

import janitza_methods as jm
from datetime import datetime
from time import sleep
import os

# Zuerst mal die Konsole leeren....
os.system('clear')

# ------------------------------------------------------------------------- #
#
#  Ab hier gehts los mit der Konfig.
#
# ------------------------------------------------------------------------- # 

# Modbus-Client-Objekt instanzieren 
# Hier könnte man das tty-Device ändern.
client=jm.establish_modbus("/dev/ttyUSB0")

#Wenn die Devices manuell konfiguruert werden sollen muss die folgende Variable auf True gesetzt werden:
manualconfig=False
searchrange=range(1,16)

#Anhängsel an den Dateinamen
#filenameext=""
filenameext=datetime.now().strftime('_%Y_%m_%d')


# ------------------------------------------------------------------------- #
#
#  Ende Config.
#
# ------------------------------------------------------------------------- #


if manualconfig == False:
  #Devices suchen und danach anfangen.
  print("Searching Janitzas (A 1 - 15)...")
  old_timeout=client.timeout
  client.timeout=0.1
  devices=jm.search_devices(client,searchrange)
  if len(devices) < 1:
    quit("No Devices found. Check ModBus or use manual Mode. Exiting.")
  print("Found following devices: "+str(devices))
  client.timeout=old_timeout
  
while True:
    
    # Und los: Die gefundenen Devices werden nacheinander geloggt.
    try:
     if manualconfig == False:
       for dev in devices:
          if dev[1] == "UMG96S":
             name="A"+str(dev[0]).zfill(3)+"_powerdata"+filenameext+".log"
             jm.logger_UMG96S(client,int(dev[0]),name)
             print("Last Log: "+name+" "+datetime.now().strftime('%H:%M:%S'))
          elif dev[1] == "UMG96RM":
             name="A"+str(dev[0]).zfill(3)+"_powerdata"+filenameext+".log"
             jm.logger_UMG96RM(client,int(dev[0]),name)
             print("Last Log: "+name+" "+datetime.now().strftime('%H:%M:%S'))
          else:
             print("Ungültiger Janitza-Typ")
             print(dev)
     else:
          jm.logger_UMG96S(client,4,"A004_powerdata.log")
          jm.logger_UMG96RM(client,10,"A010_powerdata.log")

    # Wenn irgendwas schief geht: Fehler ausgeben und 500ms warten.
    except Exception as err:
       #os.system('clear')
       print('oops... Es hat mal wieder nicht geklappt...')
       sleep(0.5)
       print(str(err))
       pass
   
    # Wenn jemand STRG+C macht ordentlich beenden.
    except KeyboardInterrupt:
       break
quit()
