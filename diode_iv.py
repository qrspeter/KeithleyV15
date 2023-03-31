from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

# define sweep parameters
sweep_start = 0.0
sweep_end = 10.0
sweep_step = 0.1

sample_name = 'subs7'

if sweep_start > sweep_end:
    sweep_step = -1 * np.abs(sweep_step)
else:
    sweep_step = np.abs(sweep_step)
    
steps = int((sweep_end - sweep_start) / sweep_step)


""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') # SMU26xx("TCPIP0::192.166.1.101::inst0::INSTR")

# get one channel of the Sourcemeter (we only need one for this measurement)
smu = sm.get_channel(sm.CHANNEL_A)

""" ******* Configure the SMU Channel A ******** """
#define a variable "current range" to be able to change it quickly for future measurements


current_range = 1e-2
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

#smu.set_measurement_speed_normal()
smu.set_measurement_speed_hi_accuracy()
'''
40 измерений (20В по 0.25)
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
time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
filename_csv = './data/' + time_for_name + '_' + sample_name +'_IV_' + str(sweep_end) + '.csv'
#filename_pdf = 'Diode_' + 'current_range_' + current_range_for_name + '_' + time_for_name +'.pdf'

#initializing a CSV file, to which the measurement data will be written - if this script is used to measure another characteristic than the U/I curve, this has to be changed
# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow(["# Voltage / V", "Current / A"])

""" ******* Make a voltage-sweep and do some measurements ******** """

# define variables we store the measurement in
# rename if needed
data_current = []
data_voltage = []

# enable the output
smu.enable_output()

smu.set_voltage(sweep_start)
smu.measure_current_and_voltage()

smu.set_voltage(sweep_start)
smu.measure_current_and_voltage()
# step through the voltages and get the values from the device
for nr in range(steps):
    # calculate the new voltage we want to set
    voltage_to_set = sweep_start + (sweep_step * nr)
    # set the new voltage to the SMU
    smu.set_voltage(voltage_to_set)
    # get current and voltage from the SMU and append it to the list so we can plot it later
    [current, voltage] = smu.measure_current_and_voltage()
    data_voltage.append(voltage_to_set)
    data_current.append(current)
    print(str(voltage_to_set) +' V; '+str(current)+' A')
    # Write the data in a csv
    with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow([voltage_to_set, current])
       

# disable the output
smu.disable_output()

# properly disconnect from the device
sm.disconnect()

""" ******* Plot the Data we obtained ******** """

#use plt instead of semilogy to plot in chartesian axis
plt.plot(data_voltage, data_current, label = r'$I_{D}$', color='red', linewidth=2)
#plt.semilogy(data_voltage, np.abs(data_current),'label = r'$I_{D}$', color='red', linewidth=2)

# set labels and a title
#suggestion: include some more information about the measurement (ref CSV file title)
plt.xlabel('Voltage / V', fontsize=14)
plt.ylabel('Current / A', fontsize=14)
plt.title(time_for_title, fontsize=14)
#plt.title('Characteristic curve of a diode', fontsize=14)
plt.tick_params(labelsize = 14)

# plt.savefig(filename_pdf)
plt.show()

