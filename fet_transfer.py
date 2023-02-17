from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

gate_start = 0.0
gate_end = -40.1
gate_step = 0.25
ch_bias = -5


if gate_start > gate_end:
    gate_step = -1 * np.abs(gate_step)
else:
    gate_step = np.abs(gate_step)
    
    
gate_steps = int((gate_end - gate_start) / gate_step)

current_range = 1e-3
current_range_for_name = str(current_range)

""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') # SMU26xx("TCPIP0::192.166.1.101::inst0::INSTR")

# get one channel of the Sourcemeter (we only need one for this measurement)
smu_ch = sm.get_channel(sm.CHANNEL_A)
smu_gate = sm.get_channel(sm.CHANNEL_B)

""" ******* Configure the SMU Channel A ******** """
#define a variable "current range" to be able to change it quickly for future measurements



# reset to default settings
smu_ch.reset()
smu_gate.reset()
# setup the operation mode of the source meter to act as a voltage source - the SMU generates a voltage and measures the current
smu_ch.set_mode_voltage_source()
smu_gate.set_mode_voltage_source()
# set the voltage and current parameters
smu_ch.set_voltage_range(40)
smu_ch.set_voltage_limit(40)
smu_ch.set_voltage(0)
smu_ch.set_current_range(current_range)
smu_ch.set_current_limit(current_range)
smu_ch.set_current(0)

smu_gate.set_voltage_range(40)
smu_gate.set_voltage_limit(40)
smu_gate.set_voltage(0)
smu_gate.set_current_range(current_range)
smu_gate.set_current_limit(current_range)
smu_gate.set_current(0)

smu_ch.set_measurement_speed_fast()
#smu_ch.set_measurement_speed_hi_accuracy()
smu_gate.set_measurement_speed_fast()
'''
40 измерений (20В по 0,25)
set_measurement_speed_hi_accuracy - 37 секунд (1.41859e-09 A)
set_measurement_speed_fast - 2 секунды (4.65035e-08 A)

SPEED_FAST / SPEED_MED / SPEED_NORMAL / SPEED_HI_ACCURACY
'''

""" ******* For saving the data ******** """

#some suggestions for improvement of the data saving
	#the file name should identify the file uniquely
	#therefore specifying for example the voltage range, and the
	#type of characteristic (U/I, U/R, etc...) is suggested

# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
filename_csv = './data/' + 'FET_' + time_for_name + '_vds_' + str(ch_bias) + '.csv'
filename_pdf = 'Diode_' + 'current_range_' + current_range_for_name + '_' + time_for_name +'.pdf'

#initializing a CSV file, to which the measurement data will be written - if this script is used to measure another characteristic than the U/I curve, this has to be changed
# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
        writer.writerow(["# Gate / V", "Channel / A", "Channel / V", "Gate / A"])

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
# sweep_start = -10.0
# sweep_end = 10.0
# sweep_step = 0.25
# steps = int((sweep_end - sweep_start) / sweep_step)



# define variables we store the measurement in
# rename if needed
ch_current = []
gate_voltage = []
gate_current = []

# enable the output
smu_ch.enable_output()
smu_gate.enable_output()


smu_ch.set_voltage(ch_bias)

# step through the voltages and get the values from the device
for nr in range(gate_steps):
    # calculate the new voltage we want to set
    ch_voltage = gate_start + (gate_step * nr)
    # set the new voltage to the SMU
    smu_gate.set_voltage(ch_voltage)
    # get current and voltage from the SMU and append it to the list so we can plot it later
    [current, voltage] = smu_ch.measure_current_and_voltage()
    gate_voltage.append(ch_voltage)
    ch_current.append(current)
    g_curr = smu_gate.measure_current()
    gate_current.append(g_curr)
    print(str(ch_voltage)+'V; '+str(current)+' A; ' + str(g_curr) + ' A')
    # Write the data in a csv
    with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t',  lineterminator='\n')
        writer.writerow([ch_voltage, current, ch_bias, g_curr])
       

# disable the output
smu_ch.disable_output()
smu_gate.disable_output()


# properly disconnect from the device
sm.disconnect()

""" ******* Plot the Data we obtained ******** """

#use plt instead of semilogy to plot in chartesian axis
#plt.semilogy(gate_voltage, np.abs(ch_current),'x-', linewidth=2)
plt.plot(gate_voltage, ch_current, label = r'$I_{DS}$', color='red', linewidth=2)
plt.plot(gate_voltage, gate_current, label = r'$I_{GS}$', color='black', linestyle='dashed', linewidth=1)

# set labels and a title
#suggestion: include some more information about the measurement (ref CSV file title)
plt.xlabel('Voltage / V', fontsize=14)
plt.ylabel('Current / A', fontsize=14)
plt.title('FET transfer characteristics' + r', $V_{DS}$ = ' + str(ch_bias), fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc = 'upper right')

# plt.savefig(filename_pdf)
plt.show()
