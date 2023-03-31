# Diode and FET measurement with Keithley 2636b using LAN

#Based on "Red Light Emitting Diode" from http://lampx.tugraz.at/~hadley/semi/studentreports/WS18/RedLED/RedLED.html
#by TU Graz / Graz University of Technology


KeithleyV15.py - KeithleyV15 library
diode_iv.py - IV measurement I(V)
diode_temporal - I(t) at given U until break
diode_pulsed - I(t)  at given V with pulsed laser. With delay and accumulation.
fet_output.py - output curve Ids(Vds) at given Vgs
fet_transfer - transfer curve Ids(Vgs) at given Vds
fet_temporal.py - Ids(t) at given Vds and Vgs until break
fet_pulsed - I(t) at given V with pulsed laser and accumulation in cycles (and with delay). With delay and accumulation.

Data are saved into ./data/ folder

Press Ctrl-C to exit from delay or accumulation loop