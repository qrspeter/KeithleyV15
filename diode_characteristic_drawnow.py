from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

from drawnow import drawnow # https://stackoverflow.com/a/23568399/20989132

def make_fig():
    plt.scatter(data_voltage, data_current)  # I think you meant this

plt.ion()  # enable interactivity
#fig = plt.figure()  # make a figure

"""
EXAMPLE: characteristic curve of a diode

Schematic:

    --------------
    |            |
  -----         -|-
  | A | SMU     \|/
  -----         -|-
    |            |
    --------------

"""

""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') # SMU26xx("TCPIP0::192.166.1.101::inst0::INSTR")

# get one channel of the Sourcemeter (we only need one for this measurement)
smu = sm.get_channel(sm.CHANNEL_A)

""" ******* Configure the SMU Channel A ******** """
#define a variable "current range" to be able to change it quickly for future measurements


current_range = 1e-4
current_range_for_name = str(current_range)

# reset to default settings
smu.reset()
# setup the operation mode of the source meter to act as a voltage source - the SMU generates a voltage and measures the current
smu.set_mode_voltage_source()
# set the voltage and current parameters
smu.set_voltage_range(40)
smu.set_voltage_limit(40)
smu.set_voltage(0)
smu.set_current_range(current_range)
smu.set_current_limit(current_range)
smu.set_current(0)

""" ******* For saving the data ******** """

#some suggestions for improvement of the data saving
	#the file name should identify the file uniquely
	#therefore specifying for example the voltage range, and the
	#type of characteristic (U/I, U/R, etc...) is suggested

# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
filename_csv = './data/' + 'Diode_' + 'current_range_' + current_range_for_name + '_' + time_for_name +'.csv'
filename_pdf = './data/' + 'Diode_' + 'current_range_' + current_range_for_name + '_' + time_for_name +'.pdf'

#initializing a CSV file, to which the measurement data will be written - if this script is used to measure another characteristic than the U/I curve, this has to be changed
# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
        writer.writerow(["# Voltage / V", "Current / A"])

""" ******* Make a voltage-sweep and do some measurements ******** """

#some suggestions for the improvement of the measurement process
	#it would be nice to have a primary measurement, in which the
	#type of junction was be determined and a parameter was set
	#that indicated the forward direction of the junction
	#this primary measurement could also be executed and inlcuded
	#in the file name
	#this procedure would spare us the time of finding the forward
	#direction

# define sweep parameters
sweep_start = -5
sweep_end = 5
sweep_step = 0.25
steps = int((sweep_end - sweep_start) / sweep_step)

# define variables we store the measurement in
# rename if needed
data_voltage = []
data_current = []

# enable the output
smu.enable_output()

# step through the voltages and get the values from the device
for nr in range(steps):
    # calculate the new voltage we want to set
    voltage_to_set = sweep_start + (sweep_step * nr)
    # set the new voltage to the SMU
    smu.set_voltage(voltage_to_set)
    # get current and voltage from the SMU and append it to the list so we can plot it later
    [current, voltage] = smu.measure_current_and_voltage()
    data_voltage.append(voltage)
    data_current.append(current)
    print(str(voltage)+' V; '+str(current)+' A')
    # Write the data in a csv
    with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
        writer.writerow([voltage, current])
    drawnow(make_fig)

# disable the output
smu.disable_output()

# properly disconnect from the device
sm.disconnect()


plt.ioff() # тогда нарисованный график никуда не пропадает, правда и следующий не появляется, и настройки надо бы унести вверх
""" ******* Plot the Data we obtained ******** """

#use plt instead of semilogy to plot in chartesian axis
plt.semilogy(data_voltage, np.abs(data_current),'x-', linewidth=2)

# set labels and a title
#suggestion: include some more information about the measurement (ref CSV file title)
plt.xlabel('Voltage (V)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title('Characteristic curve of a diode', fontsize=14)
plt.tick_params(labelsize = 14)

# plt.savefig(filename_pdf)
plt.show()
