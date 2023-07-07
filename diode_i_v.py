from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

# define sweep parameters
sweep_start = 0.0
sweep_end = 5.0
sweep_step = 0.1

sample_name = 'rGO_centrif_heated'

if sweep_start > sweep_end:
    sweep_step = -1 * np.abs(sweep_step)
else:
    sweep_step = np.abs(sweep_step)
    
steps = int((sweep_end - sweep_start) / sweep_step) + 1


""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') 

# get one channel of the Sourcemeter (we only need one for this measurement)
smu = sm.get_channel(sm.CHANNEL_A)

""" ******* Configure the SMU Channel A ******** """
#define a variable "current range" to be able to change it quickly for future measurements


current_range = 5e-3
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


# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
filename_csv = './data/' + time_for_name + '_' + sample_name +'_IV_' + str(sweep_end) + '.csv'

""" ******* Make a voltage-sweep and do some measurements ******** """

# enable the output
smu.enable_output()

smu.set_voltage(sweep_start)
smu.measure_current_and_voltage()

smu.set_voltage(sweep_start)
smu.measure_current_and_voltage()

# define variables we store the measurement in
column_names = []
data = []

voltages = np.empty(steps)
for i in range(steps):
    voltages[i] = sweep_start + (sweep_step * i)
column_names.append("Voltage (V)")
#column_names += "Voltage (V)"

data.append(voltages)

print("Sample set name: ", sample_name)

while True:
    print('Enter sample label (or press Enter to finish): ')
    sample_num = input()
    if sample_num == "":
        break

    column_names.append(sample_num)
    currents = np.zeros(steps)
    
    # additional measurement to exclude error of first measurement
    smu.set_voltage(voltages[0])
    [current, voltage] = smu.measure_current_and_voltage()

    for nr in range(steps):
        # calculate the new voltage we want to set
        # set the new voltage to the SMU
        smu.set_voltage(voltages[nr])
        # get current and voltage from the SMU and append it to the list so we can plot it later
        [current, voltage] = smu.measure_current_and_voltage()
        currents[nr] = current
        print(str('%.2f' % voltage) +' V; '+str('%.5e' % current)+' A')

    data.append(currents)
    fig = plt.figure(figsize=(8,6))
    plt.plot(voltages, currents, label = sample_num, linewidth=2)
    plt.xlabel('Voltage (V)', fontsize=14)
    plt.ylabel('Current (A)', fontsize=14)
    plt.title(time_for_title, fontsize=14)
    plt.tick_params(labelsize = 14)
    plt.legend(loc='upper left')
    plt.show()
    

np_data = np.stack(data, axis=0)    

delim = ','
column_names_str = delim.join(column_names)
np.savetxt(filename_csv, np_data.T, fmt='%.10g', delimiter=',', header=column_names_str)  

# disable the output
smu.disable_output()

# properly disconnect from the device
sm.disconnect()

""" ******* Plot the Data we obtained ******** """

fig = plt.figure(figsize=(8,6))
for i in range(np_data.shape[0]-1):
    plt.plot(np_data[0, :], np_data[i+1,:], label = column_names[i + 1], linewidth=2)
plt.xlabel('Voltage (V)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title(time_for_title, fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc='upper left')
plt.savefig(filename_csv[:-4] + '.png')
plt.show()

