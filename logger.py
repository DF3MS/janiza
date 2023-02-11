#!/usr/bin/python3

# ----------------------------------------------------- #
#                                                       #
# Skript zum Auslesen von Janitza UMG96                 #
# Konfiguration erfolgt am unteren Ende :-)             #
#                                                       #
# Bei Fragen: mail-janitza@f50hz.de                     #
#                                                       #
# Matthias Schlecht 2022                                #
#                                                       #
# ----------------------------------------------------- #


from pymodbus.client.sync import ModbusSerialClient as mbc
from datetime import datetime
from time import sleep
import os

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


#Modbus-Foo

def establish_modbus(tty):
    #Diese Methode baut ein Objekt mit dem Modbus-Client und gibt es zurück, dass an die Logger-Methoden übergeben wird.
    client = mbc(method="rtu", port=tty, stopbits=1, bytesize=8, parity='N', baudrate=9600)
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
     freqr = get_modbus(800,2,address)
     
     # L1,L2,L3, L1-L2, L2-L3, L3-L1
     valuesU = get_modbus(3530,6,address)

     # I1, I2, I3, IN(calc), P1,P2,P3,Psum 
     valuesIP = get_modbus(3916,8,address)

     # Cos(phi)
     valuesCos = get_modbus(3776,4,address)
     # Energie
     valuesEn  = get_modbus(19060,2,address)

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

# Ab hier kommet das Haupt-Programm

# Zuerst mal die Konsole leeren....
os.system('clear')

# ------------------------------------------------------------------------- #
#
#  Ab hier gehts los mit der Konfig.
#
# ------------------------------------------------------------------------- # 

# Modbus-Client-Objekt instanzieren 
# Hier könnte man das tty-Device ändern.
client=establish_modbus("/dev/ttyUSB0")

while True:
    
    # Beispiele für Filenames mit Datum drin, wenn man mal länger loggen will.

    filename1 = datetime.now().strftime('powerdata_100'+'_%Y_%m_%d.log')
    
    # Und los: Einmal eine Methodenaufruf für jedes Janiza. Danach eine kurze Statusausgabe.
    try:
       logger_UMG96S(client,3,"A003_powerdata.log")
       logger_UMG96S(client,4,"A004_powerdata.log")
       #logger_UMG96RM(client,100,"A100_powerdata.log")
       
       
       print("Last Log: "+datetime.now().strftime('%H:%M:%S'))
    
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
