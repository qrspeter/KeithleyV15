from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np



# gate_start = -0
# gate_end = -40.2
# gate_step = 0.25
drain_bias = -5
gate_bias = -40

'''
#Use a try except statement with the while loop inside of the try block and a Keyboard Interrupt exception in the except statement. When Ctrl-C is pressed on the keyboard, the while loop will terminate.
# https://www.adamsmith.haus/python/answers/how-to-kill-a-while-loop-with-a-key-stroke-in-python

# https://stackoverflow.com/questions/18994912/ending-an-infinite-while-loop

'''

# if gate_start > gate_end:
    # gate_step = -1 * np.abs(gate_step)
# else:
    # gate_step = np.abs(gate_step)
    
    
#gate_steps = int((gate_end - gate_start) / gate_step)

current_range = 1e-3
current_range_for_name = str(current_range)

""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') 

# get one channel of the Sourcemeter 
smu_drain = sm.get_channel(sm.CHANNEL_A)
smu_gate = sm.get_channel(sm.CHANNEL_B)


# reset to default settings
smu_drain.reset()
smu_gate.reset()
# setup the operation mode of the source meter to act as a voltage source - the SMU generates a voltage and measures the current
smu_drain.set_mode_voltage_source()
smu_gate.set_mode_voltage_source()
# set the voltage and current parameters
smu_drain.set_voltage_range(40)
smu_drain.set_voltage_limit(40)
smu_drain.set_voltage(0)
smu_drain.set_current_range(current_range)
smu_drain.set_current_limit(current_range)
smu_drain.set_current(0)

smu_gate.set_voltage_range(40)
smu_gate.set_voltage_limit(40)
smu_gate.set_voltage(0)
smu_gate.set_current_range(current_range)
smu_gate.set_current_limit(current_range)
smu_gate.set_current(0)

smu_drain.set_measurement_speed_hi_accuracy()
#smu_ch.set_measurement_speed_hi_accuracy()
smu_gate.set_measurement_speed_fast()
'''
40 измерений (20В по 0,25)
set_measurement_speed_hi_accuracy - 37 секунд (1.41859e-09 A)
set_measurement_speed_fast - 2 секунды (4.65035e-08 A)

SPEED_FAST / SPEED_MED / SPEED_NORMAL / SPEED_HI_ACCURACY
'''

""" ******* For saving the data ******** """

# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
filename_csv = './data/' + 'FET_' + time_for_name + '_time_' + '_vds_' + str(drain_bias) +  '_vgs_' + str(gate_bias) + '.csv'

#initializing a CSV file, to which the measurement data will be written - if this script is used to measure another characteristic than the U/I curve, this has to be changed
# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["# Time / sec", "Drain / A", "Drain / V", "Gate / A"])

""" ******* Make a voltage-sweep and do some measurements ******** """

# define variables we store the measurement in
drain_current = []
gate_current = []
time_arr = []

# enable the output
smu_drain.enable_output()
smu_gate.enable_output()


smu_drain.set_voltage(drain_bias)
smu_gate.set_voltage(gate_bias)
start = time.time()
# step through the voltages and get the values from the device

try:
    while True:
        # calculate the new voltage we want to set
    #    g_voltage = gate_start + (gate_step * nr)
        # set the new voltage to the SMU
        smu_gate.set_voltage(gate_bias)
        # get current and voltage from the SMU and append it to the list so we can plot it later
        [current, voltage] = smu_drain.measure_current_and_voltage()
        drain_current.append(current)
        g_curr = smu_gate.measure_current()
        gate_current.append(g_curr)
        
        # Вычисление времени от начала измерения datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
        t = time.time() - start
        time_arr.append(t)
        
        print(str(t)+ ' sec; '+str(current)+' A; ' + str(g_curr) + ' A')
        # Write the data in a csv
        with open(filename_csv, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([t, current, drain_bias, g_curr])

except KeyboardInterrupt:
# disable the output
    smu_drain.disable_output()
    smu_gate.disable_output()


    # properly disconnect from the device
    sm.disconnect()

""" ******* Plot the Data we obtained ******** """

plt.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
plt.plot(time_arr, gate_current, label = r'$I_{GS}$', color='black', linestyle='dashed', linewidth=1)

# set labels and a title
plt.xlabel('Time / s', fontsize=14)
plt.ylabel('Current / mA', fontsize=14)
plt.title('Temporal characteristics' + r', $V_{DS}$ = ' + str(drain_bias) + r', $V_{GS}$ = ' + str(gate_bias), fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc = 'upper right')

plt.show()
