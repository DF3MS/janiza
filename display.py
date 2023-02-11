#!/usr/bin/python3

# ----------------------------------------------------- #
#                                                       #
# Skript zum Anzeigen von Janitza UMG96 - Logs          #
# Konfiguration erfolgt am unteren Ende :-)             #
#                                                       #
# Bei Fragen: mail-janitza@f50hz.de                     #
#                                                       #
# Matthias Schlecht 2022                                #
#                                                       #
# ----------------------------------------------------- #

from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.console import Group
from datetime import datetime
from datetime import timedelta
import time
import os


def get_data(filename):
  # Methode zu, auslesen der letzten Zeile einer Datei und Parsen der Werte
  #  filename: Das zu lesende File.
  
  # Datei öffnen und letzte Zeile auslesen.
  with open(filename, 'r') as f:
    last_line = f.readlines()[-1]
    csv=last_line.split(",") # Splitten anhand des Trenners ","
  
  # Datum mal direkt ordentlich als datetime-Objekt anlegen.
  datecsv= datetime.strptime(csv[0],'%Y_%m_%d-%H:%M:%S.%f')
  
  # Größe der Datei ermitteln
  fileinfo=os.stat(filename)
  filesize=str(round(fileinfo.st_size/(1024*1024),1))

  # Wenn die letzte Zeile zu alt ist, dann Warnung einfügen.
  if (datetime.now()-datecsv) > timedelta(seconds=10):
     warning="[blink]!! OLD DATA !!"
  else:
     warning=""
  
  # Aus dem CSV-String ein dict bauen.
  data = {
   "date": datecsv,
   "u1": csv[1],
   "u2": csv[2],
   "u3": csv[3],
   "u12": csv[4],
   "u23": csv[5],
   "u31": csv[6],
   "i1": csv[7],
   "i2": csv[8],
   "i3": csv[9],
   "iN": csv[10],
   "p1": csv[11],
   "p2": csv[12],
   "p3": csv[13],
   "freq": csv[14],
   "cos1": csv[15],
   "cos2": csv[16],
   "cos3": csv[17],
   "cosS": csv[18],
   "drehfeld": "-",
   "energy": csv[19][:-1],
   "warning": warning,
   "filesize": filesize
  }

  return data
    

def print_panel(filename,title,maxcurrent) -> Panel:
  # Methode um ein Rich-Panel mit der Tabelle der Werte zu generieren.
  # filename:   Dateiname der zu lesenden Datei
  # title:      Überschrift des Panels
  # maxcurrent: Stromschwelle für die Einfärbung der Phasen
  
  
  # Ein paar generelle Variablen für Einheiten und Einfärbungen.
  unitV="V"
  unitI="A"
  unitP="W"
  unitF="Hz"
  iyellow=maxcurrent*0.8
  ired=maxcurrent*0.95
  l1warn = l2warn = l3warn = lNwarn =  "[green]"

  # Dict mit den Daten holen.
  data = get_data(filename)

  # Bestimmen ob Stromwerte überschritten sind
  if float(data["i1"]) > ired:
   l1warn = "[bold bright_red]"
  elif float(data["i1"]) > iyellow:
   l1warn = "[bold bright_yellow]"

  if float(data["i2"]) > ired:
   l2warn = "[bold bright_red]"
  elif float(data["i2"]) > iyellow:
   l2warn = "[bold bright_yellow]"

  if float(data["i3"]) > ired:
   l3warn = "[bold bright_red]"
  elif float(data["i3"]) > iyellow:
   l3warn = "[bold bright_yellow]"

  if float(data["iN"]) > ired:
   lNwarn = "[bold bright_red]"
  elif float(data["iN"]) > iyellow:
   lNwarn = "[bold bright_yellow]"

  # Zusammenbasteln der Tabellen. Rich-Tables können keinen Col-Span daher drei Tabellen die gruppiert werden.
  header = Table.grid(expand=False,padding=(0,0,0,1))
  header.add_column()
  header.add_row("Last Value: "+datetime.strftime(data["date"],'%d.%m.%Y %H:%M:%S'))
  header.add_row("[red]"+data["warning"])


  table = Table.grid(expand=False,padding=(0,0,0,1))
  table.add_column(width=3)
  table.add_column(width=7)
  table.add_column(width=7)
  table.add_column(width=8)
  table.add_row("L1:",data["u1"]+unitV,"L1-L2:",data["u12"]+unitV)
  table.add_row("L2:",data["u2"]+unitV,"L2-L3:",data["u23"]+unitV)
  table.add_row("L3:",data["u3"]+unitV,"L3-L1:",data["u31"]+unitV)
  table.add_row("F:",data["freq"]+unitF,"cosPhi:",data["cosS"])
  table.add_row()
  table.add_row("I1:",l1warn+data["i1"]+unitI,"P1:",data["p1"]+unitP)
  table.add_row("I2:",l2warn+data["i2"]+unitI,"P2:",data["p2"]+unitP)
  table.add_row("I3:",l3warn+data["i3"]+unitI,"P3:",data["p3"]+unitP)
  table.add_row("IN:",lNwarn+data["iN"]+unitI)
  
  footer= Table.grid(expand=False,padding=(0,0,0,0))
  footer.add_column()
  footer.add_row()
  footer.add_row("Filesize: "+data["filesize"]+"M")
   
  #Tabellen gruppieren
  panel_group=Group(
     header,
     table,
     footer,
  )
  
  #Panel-Objekt bauen und mit Titel versehen.
  panel=Panel.fit(panel_group,title=title)
  return panel


def make_Layout() -> Layout:
# Methode zum Erstellen des Grund-Layouts
  lay=Layout()
  lay.split_column(
    Layout(name="header"), 
    Layout(name="row1"), 
    Layout(name="row2"), 
    Layout(name="footer"),
  )
  lay["row1"].split_row(
    Layout(name="UMG1"),
    Layout(name="UMG2"),
  )
  lay["row2"].split_row(
    Layout(name="UMG3"),
    Layout(name="UMG4"),
  )
  lay["header"].size=3
  lay["footer"].size=3
  lay["row1"].size=15
  lay["row2"].size=15

  return lay

def print_Header() -> Panel:
# Methode zum Erstellen des Header-Panels

  headertext="JANITZA UMG96 Strommonitoring"
  header=Panel(headertext)

  return header

def print_Footer(text) -> Panel:
# Methode zum Erstellen des Footer-Panels

  headertext=datetime.now().strftime('%d.%m.%Y %H:%M:%S')+" [bold red]"+text
  header=Panel(headertext)

  return header


# Ab hier kommet das Haupt-Programm

# Grund-Layout erstellen
lay=make_Layout()
# Konsole instanzieren.
console = Console()

# ------------------------------------------------------------------------- #
#
#  Ab hier gehts los mit der Konfig.
#
# ------------------------------------------------------------------------- # 

#Live-Objekt instanziern
with Live(lay, refresh_per_second=1) as live:
    while (1):
        # Und los: 
        try:
          # Hier werden die 4 Panels mit Inhalt gefüllt
          #                                filenme             Name             Strom
          lay["UMG1"].update(print_panel("A010_powerdata.log","TEST 16A",16))
          #lay["UMG2"].update(print_panel("A002_powerdata.log","Benenn Mich 16A",16))
          #lay["UMG3"].update(print_panel("A100_powerdata.log","Benenn Mich 16A",16))
          #lay["UMG4"].update(print_panel("/tmp/testdaten.log","Ton 5A",5))
        
          # Header und Footer aktualisieren
          lay["header"].update(print_Header())
          lay["footer"].update(print_Footer(""))          
          
          # Anti-Eskalations-Sleep
          time.sleep(0.4)
          
        # Wenn was schief geht:
        except Exception as excep:
          # Nur den Header und den Footer aktualisiern und die exception in den Footer schreiben. So bleiben die alten Werte stehen und das Display flackert nicht.
          lay["header"].update(print_Header())
          lay["footer"].update(print_Footer("Fehler!:"+str(excep)))
        # Wenn jemand STRG+C macht ordentlich beenden.
        except KeyboardInterrupt:
          break
quit()
