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


from pymodbus.client.sync import ModbusSerialClient as mbc
from datetime import datetime
from time import sleep
import os

def establish_modbus(tty):
    #Diese Methode baut ein Objekt mit dem Modbus-Client und gibt es zurück, dass an die Logger-Methoden übergeben wird.
    client = mbc(method="rtu", port=tty, stopbits=1, bytesize=8, parity='N', baudrate=9600,timeout=0.1)
    return client

def get_modbus(client,startadd,numofreg,address):
  #Abfrage von mehreren Registern sequentiell über ein Modbus-Client-Objekt.
  #  client: Modbus-Client-Objekt
  #  startadd: Startadresse
  #  numofreg: Anzahl der zu lesenden Registern
  #  address: Modbus-Adresse
  client.connect()
  read = client.read_holding_registers(startadd, numofreg, unit=address)
  client.close()
  sleep(0.05)
  return read.registers

client=establish_modbus("/dev/ttyUSB0")


def search_devices(range):
    #Devices-Array erstellen
    devices=[]

    for address in range:
        try:
            #Versuch 1: Einfach mal die Adresse auslesen...
            mb_address= get_modbus(client,0,1,address)[0]
            if mb_address == address:
                # Wenn das klappt lesen wir Register 200 aus.
                u1_umg96S = get_modbus(client,200,1,address)[0]
            if 2000 < u1_umg96S < 2500:
                # Wenn das ausgelesene Register einen sinnvollen Wert hat,
                # dann haben wir wohl ein UMG96S gefunden.
                print("Found UMG 96S on Address "+str(address))
                # Hier wird das UMG zum Array hinzugefügt.
                devices.append([address,"UMG96S"])
            else:
                # Wenn nicht, dann lesen wir Register 3530 aus, 
                # dass dann einen sinnvollen Wert ergeben sollte...
                u1_umg96RM= get_modbus(client,3530,1,address)[0]
                if 2000 < u1_umg96RM < 2500:
                        print("Found UMG 96RM on Address "+str(address))
                        # Wenn der Wert passt adden wir das UMG zum Array
                        devices.append([address,"UMG96RM"])
        except AttributeError:
            # Wenn auf der Adresse nichts (oder Blödsinn) antwortet:
            print("Nothing on Address "+str(address))
    return devices

def get_device_info(devices):
    # Nun wollen wir von allen Devices die Eingenschaften haben
    dev_info = {}
    devnum=0
    for dev in devices:
        device = {}
        # Zuerst basteln wir den Namen zusammen
        name="A"+str(dev[0]).zfill(3)+"_"+dev[1]
        device['name'] = name
        # Dann die Adresse
        device['address'] = dev[0]
        # und den Typ (UMG96 RM oder UMG96S)
        device['type'] = dev[1]
        address = dev[0]
        if dev[1]=="UMG96S":
            # Hier holen wir die Werte für die Strom und Spannungsumrechnung
            device['transvalues']=get_modbus(client,600,4,address)
            # Hier holen wir die PIN
            device['pin']=get_modbus(client,11,1,address)
            # Just for Fun auch noch die Temp und die Höhe der internen Spannung.
            temp_vint=get_modbus(client,408,2,address)
            device['temp']=temp_vint[0]
            device['vint']=temp_vint[1]
            # Hier setzen wir einmal den Maximalstrom für das Display
            device['maxamps']=32
        elif dev[1]=="UMG96RM":
            transvalue=get_modbus(client,10,24,address)
            device['maxamps']=80
        # Jedes Device-Dict wird in das dev_info-Dict gespeichert
        dev_info[devnum]=device
        devnum +=1
    print(dev_info)

# ------------------------------------------------------------------------- #
#
#  Ab hier gehts los mit der Konfig.
#
# ------------------------------------------------------------------------- #

# Einmal die Addressrange definiert und los gehts.

get_device_info(search_devices(range(1,20)))

quit()
