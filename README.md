# Diode and FET measurement with Keithley 2636b using LAN

#Based on "Red Light Emitting Diode" from http://lampx.tugraz.at/~hadley/semi/studentreports/WS18/RedLED/RedLED.html
#by TU Graz / Graz University of Technology


KeithleyV15.py - KeithleyV15 library
diode_iv.py - IV measurement I(V)
diode_pulsed - I(t)  at given V with TTL controlled laser with start delay and accumulation.
diode_pulsed_lockin - V(t) (for measuring voltage from lock-in detector)
diode_temporal - I(t) at given V until break.
diode_temporal_lockin - V(t) (for measuring voltage from lock-in detector)
fet_output.py - output curve Ids(Vds) at given Vgs
fet_pulsed - I(t) at given V with pulsed laser and accumulation in cycles (and with delay). 
fet_transfer - transfer curve Ids(Vgs) at given Vds
fet_temporal.py - Ids(t) at given Vds and Vgs until break

Data are saved into ./data/ folder

Press Ctrl-C to exit from delay or accumulation loop