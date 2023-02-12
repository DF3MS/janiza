#!/usr/bin/python3

# ----------------------------------------------------- #
#                                                       #
# Methodensammlungzum Auslesen von Janitza UMG96        #
#                                                       #
# Bei Fragen: mail-janitza@f50hz.de                     #
#                                                       #
# Matthias Schlecht 2022 - 2023                         #
#                                                       #
# ----------------------------------------------------- #

from pymodbus.client.sync import ModbusSerialClient as mbc
from datetime import datetime
from time import sleep
import os

#----------------
# MODBUS 
#----------------

def establish_modbus(tty,baudrate=9600,timeout=1):
    #Diese Methode baut ein Objekt mit dem Modbus-Client und gibt es zurück, dass an die Logger-Methoden übergeben wird.
    client = mbc(method="rtu", port=tty, stopbits=1, bytesize=8, parity='N', baudrate=baudrate,timeout=timeout)
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

#----------------
# Devices suchen 
#----------------
def search_devices(client,range):
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

def get_device_info(client,devices):
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
            # Hier holen wir die Mittelwertszeit für Strom und Leistung.
            raw_avgtimes=get_modbus(client,57,2,address)
            avgtimes=[5,10,30,60,300,480,900]
            device['avg_current'] = avgtimes[raw_avgtimes[0] & 0b11111111 -1]
            device['avg_power'] = avgtimes[raw_avgtimes[1] & 0b11111111 -1]
            # Hier holen wir die PIN
            device['pin']=get_modbus(client,11,1,address)[0]
            # Just for Fun auch noch die Temp und die Höhe der internen Spannung.
            temp_vint=get_modbus(client,408,2,address)
            device['temp']=temp_vint[0]
            device['vint']=temp_vint[1]/100
            # Hier setzen wir einmal den Maximalstrom für das Display
            #device['maxamps']=32
        elif dev[1]=="UMG96RM":
            # Hier holen wir die Werte für die Strom und Spannungsumrechnung
            transvalue=get_modbus(client,10,24,address)
            transi1h=int(ieee2float(transvalue[0], transvalue[1]))
            transi1l=int(ieee2float(transvalue[2], transvalue[3]))
            transu1h=int(ieee2float(transvalue[4], transvalue[5]))
            transu1l=int(ieee2float(transvalue[6], transvalue[7]))
            device['transvalue']=[transi1h,transi1l,transu1h,transu1l]
            # Hier holen wir die Mittelwertszeit für Strom und Leistung.
            raw_avgtimes=get_modbus(client,40,3,address)
            avgtimes=[5,10,15,30,60,300,480,600,900]
            device['avg_current'] = avgtimes[raw_avgtimes[0] & 0b11111111 -1]
            device['avg_power'] = avgtimes[raw_avgtimes[1] & 0b11111111 -1]
            device['avg_voltage'] = avgtimes[raw_avgtimes[1] & 0b11111111 -1]
            # Hier holen wir die PIN
            device['pin']=get_modbus(client,50,1,address)[0]
            # 2x Anschlusskonfiguration (siehe Anleitung)
            device['anschluss_u_509']=get_modbus(client,509,1,address)[0]
            device['anschluss_i_510']=get_modbus(client,509,1,address)[0]
            # Hier setzen wir einmal den Maximalstrom für das Display
            #device['maxamps']=80
        print(device)
        # Jedes Device-Dict wird in das dev_info-Dict gespeichert
        dev_info[devnum]=device
        devnum +=1
#print(dev_info)

    
#----------------------------
# Type-Conversion 
#----------------------------
def ieee2float(reg1, reg2):
  #Methode zum IEEE754-Floats in python Floats zu konvertieren
  binaer = reg1 <<16 | reg2
  vz = binaer >> 31 
  expb = (binaer&0b01111111100000000000000000000000)>>23
  man = (binaer&0b00000000011111111111111111111111)
  bias = 127
  exp = expb-bias
  norm = (man/(0b1<<23))+1
  ret = (norm*(0b1<<exp))*((-1)**vz)
  return ret


def twoCompl(zahl):
    # Einmal 2-er-Komplement bitte
    if zahl > 0x8FFF:
        zahl=zahl-0xFFFF
    return zahl

#----------------------------
# logger für UMG96 RM
#----------------------------
def logger_UMG96RM(client,address,filename):
     #Logger-Methode für das UMG96RM.
     #  client: Modbus-Client-Objekt
     #  address: Modbus-Adresse
     #  filename: Log-File
     
     # Definition von Faktoren für Spannung, Strom, Leistung und cos(phi)
     factu=0.1
     facti=(100/5)*0.001
     factp=(100/5)*factu
     factcos=0.01

     # Lesen der Registerblöcke
     
     # Frequenz
     freqr = get_modbus(client,800,2,address)
     
     # L1,L2,L3, L1-L2, L2-L3, L3-L1
     valuesU = get_modbus(client,3530,6,address)

     # I1, I2, I3, IN(calc), P1,P2,P3,Psum 
     valuesIP = get_modbus(client,3916,8,address)

     # Cos(phi)
     valuesCos = get_modbus(client,3776,4,address)
     # Energie
     valuesEn  = get_modbus(client,19060,2,address)

     date = datetime.now().strftime('%Y_%m_%d-%H:%M:%S.%f')
    
     # Runden und Konvertieren der Werte 
     freq = round(ieee2float(freqr[0],freqr[1]),5)
     u1= round(valuesU[0]*factu,1)
     u2= round(valuesU[1]*factu,1)
     u3= round(valuesU[2]*factu,1)
     u12= round(valuesU[3]*factu,1)
     u23= round(valuesU[4]*factu,1)
     u31= round(valuesU[5]*factu,1)
     cos1=round(twoCompl(valuesCos[0])*factcos,3)
     cos2=round(twoCompl(valuesCos[1])*factcos,3)
     cos3=round(twoCompl(valuesCos[2])*factcos,3)
     cosSum=round(twoCompl(valuesCos[3])*factcos,10)

     i1=round(valuesIP[0]*facti,3)
     i2=round(valuesIP[1]*facti,3)
     i3=round(valuesIP[2]*facti,3)
     iN=round(valuesIP[3]*facti,3)
     p1=round(valuesIP[4]*factp,0)
     p2=round(valuesIP[5]*factp,0)
     p3=round(valuesIP[6]*factp,0)
     
     energy=round(ieee2float(valuesEn[0],valuesEn[1])/1000,3)

     # gepfuschtes Zusammenbauen einer CSV. Ja man könnte das mit einem Dict machen.
     value = date+","+str(u1)+","+str(u2)+","+str(u3)+","+str(u12)+","+str(u23)+","+str(u31)+","+str(i1)+","+str(i2)+","+str(i3)+","+str(iN)+","+str(p1)+","+str(p2)+","+str(p3)+","+str(freq)+","+str(cos1)+","+str(cos2)+","+str(cos3)+","+str(cosSum)+","+str(energy)

     # Speichern der Log-Zeile
     with open(filename, "a") as myfile:
      myfile.write(value+"\n")
      myfile.close()

#----------------------------
# logger für UMG96 S
#----------------------------
def logger_UMG96S(client,address,filename):
         # Logger-Methode für das UMG96S
     
     # Definition von Faktoren für Spannung, Strom, Leistung und cos(phi)
     factu=0.1
     facti=(100/5)*0.001
     factp=(100/5)*factu
     factcos=0.01
     factf=0.01
      
     # Lesen der Registerblöcke
     # Frequenz
     freqr = get_modbus(client,800,2,address)
     
     # Spannung, Stom, Leistung
     valuesUIP = get_modbus(client,200,21,address)
     # Summen der Phasen und iN
     valuesSums = get_modbus(client,275,5,address)
     # Energie
     valuesEn = get_modbus(client,416,2,address)

     date = datetime.now().strftime('%Y_%m_%d-%H:%M:%S.%f')
     
      # Runden und Konvertieren der Werte 
     freq = round(valuesSums[0]*factf,2)
     u1= round(valuesUIP[0]*factu,1)
     u2= round(valuesUIP[1]*factu,1)
     u3= round(valuesUIP[2]*factu,1)
     u12= round(valuesUIP[3]*factu,1)
     u23= round(valuesUIP[4]*factu,1)
     u31= round(valuesUIP[5]*factu,1)
     cos1=round(twoCompl(valuesUIP[18])*factcos,3)
     cos2=round(twoCompl(valuesUIP[19])*factcos,3)
     cos3=round(twoCompl(valuesUIP[20])*factcos,3)

     cosSum=round(twoCompl(valuesSums[1])*factcos,3)

     i1=round(valuesUIP[6]*facti,3)
     i2=round(valuesUIP[7]*facti,3)
     i3=round(valuesUIP[8]*facti,3)
     iN=round(valuesSums[3]*facti,3)
     p1=round(valuesUIP[9]*factp,0)
     p2=round(valuesUIP[10]*factp,0)
     p3=round(valuesUIP[11]*factp,0)
     energy=round(((valuesEn[0]*0x10000)+valuesEn[1])*factp*0.01,3)

 
     # gepfuschtes Zusammenbauen einer CSV. Ja man könnte das mit einem Dict machen.
     value = date+","+str(u1)+","+str(u2)+","+str(u3)+","+str(u12)+","+str(u23)+","+str(u31)+","+str(i1)+","+str(i2)+","+str(i3)+","+str(iN)+","+str(p1)+","+str(p2)+","+str(p3)+","+str(freq)+","+str(cos1)+","+str(cos2)+","+str(cos3)+","+str(cosSum)+","+str(energy)
     
     # Speichern der Log-Zeile
     with open(filename, "a") as myfile:
      myfile.write(value+"\n")
      myfile.close()
      
