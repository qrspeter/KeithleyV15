# Diode and FET measurement with Keithley 2636b using LAN

#Based on "Red Light Emitting Diode" from http://lampx.tugraz.at/~hadley/semi/studentreports/WS18/RedLED/RedLED.html
#by TU Graz / Graz University of Technology


KeithleyV15.py - KeithleyV15 library
iv_curve.py - IV measurement I(V)
fet_output.py - Output curve Ids(Vds) at given Vgs
fet_transfer - Transfer curve Ids(Vgs) at given Vds
fet_stability.py - Ids(t) at given Vds and Vgs
photocurrent - I(t) at given V with pulsed laser and accumulation in cycles (and with delay)

Data are saved into ./data/ folder

Press Ctrl-C to exit from delay or accumulation loop