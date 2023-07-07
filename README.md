# Diode and FET measurement with Keithley 2636b using LAN

Based on "Red Light Emitting Diode" from http://lampx.tugraz.at/~hadley/semi/studentreports/WS18/RedLED/RedLED.html
by TU Graz / Graz University of Technology


* KeithleyV15.py - KeithleyV15 library.
* diode_i_v.py - IV measurement I(V). Several samples into one file.
* diode_i_t.py - I(t) at given U until break.
* diode_i_t_pulsed - I(t)  at given V with pulsed laser with delay and accumulation.  Several samples into one file.
* fet_output.py - output curve Ids(Vds) at given Vgs.
 *fet_transfer - transfer curve Ids(Vgs) at given Vds.

Data are saved into ./data/ folder

Press Ctrl-C to exit from delay or accumulation loop