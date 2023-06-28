from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

sample_name = 'GrGr_90m_70C_p3'

drain_bias = 1.0 # V

step = 1.0 # in sec. Not less than 0.7 for hi_accuracy and 0.4 for speed_normal

current_range = 3e-3
current_range_for_name = str(current_range)

""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') 

# get one channel of the Sourcemeter 
smu_drain = sm.get_channel(sm.CHANNEL_A)

# reset to default settings
smu_drain.reset()
# setup the operation mode of the source meter to act as a voltage source - the SMU generates a voltage and measures the current
smu_drain.set_mode_voltage_source()
# set the voltage and current parameters
smu_drain.set_voltage_range(40)
smu_drain.set_voltage_limit(40)
smu_drain.set_voltage(0)
smu_drain.set_current_range(current_range)
smu_drain.set_current_limit(current_range)
smu_drain.set_current(0)

smu_drain.set_measurement_speed_hi_accuracy()
#smu_drain.set_measurement_speed_normal()

'''
40 измерений (20В по 0,25)
set_measurement_speed_hi_accuracy - 37 секунд (1.41859e-09 A)
set_measurement_speed_fast - 2 секунды (4.65035e-08 A)

SPEED_FAST / SPEED_MED / SPEED_NORMAL / SPEED_HI_ACCURACY
'''

""" ******* For saving the data ******** """

# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

filename_csv = './data/' + 'I_T_' + sample_name + '_' + time_for_name + '_vds_' + str(drain_bias) + '.csv'

#initializing a CSV file, to which the measurement data will be written - if this script is used to measure another characteristic than the U/I curve, this has to be changed
# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow(["# Time (sec)", "Drain (A)", "Drain (V)"])


# define variables we store the measurement in
drain_current = []
time_arr = []

# enable the output
smu_drain.enable_output()

plt.ion()  # enable interactivity
fig = plt.figure()  # make a figure
ax = fig.add_subplot(111)
line1, = ax.plot(time_arr, drain_current, 'r.')
#line1, = ax.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
plt.xlabel('Time / s', fontsize=14)
plt.ylabel('Current / A', fontsize=14)
plt.title(time_for_title + r', $V_{DS}$ = ' + str(drain_bias), fontsize=14)
plt.tick_params(labelsize = 14)

# to skip drawing of first dot (draws with a big delay)
line1.set_xdata(time_arr)
line1.set_ydata(drain_current)
ax.relim()
ax.autoscale()
fig.canvas.draw()
fig.canvas.flush_events()


smu_drain.set_voltage(drain_bias)
# to skip the first measurement
smu_drain.measure_current_and_voltage()

  
try:
    start = time.time()
#    nt = time.time()

    while True:

        nt = time.time()
        [current, voltage] = smu_drain.measure_current_and_voltage()
        drain_current.append(current)
        time_arr.append(nt - start)
        
        print('%.2f' % (nt - start), ' sec; ', current, ' A')
        # Write the data in a csv
        with open(filename_csv, 'a') as csvfile:
            writer = csv.writer(csvfile,  lineterminator='\n')
            writer.writerow(['%.3f' % (nt - start), current, drain_bias])

        line1.set_xdata(time_arr)
        line1.set_ydata(drain_current)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        fig.canvas.flush_events()

        while (nt - start) < (step * len(time_arr)):
#            print(nt - start)
            nt = time.time() 

except KeyboardInterrupt:
    smu_drain.disable_output()


# properly disconnect from the device
smu_drain.disable_output()
sm.disconnect()

plt.ioff()
plt.show()
