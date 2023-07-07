from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import winsound
import numpy as np

import time

sample_name = 'rGO_centrif_heated'

drain_bias = 2.0 # V
step = 0.4 # sec, errors if time is shorter
delay = 60 # sec, Delay for warm-up
periods = 4 # periods of acqusition for averaging

period = 150 # sec, repetition period of laser pulses
laser = 40  # sec, length of a single laser pulse
laser_delay = 5  # sec, pulse delay from the beginning of each period

current_range = 15e-3

'''
Press Ctrl-C to terminate any loop.
'''
# it is better to move graphs to some thread because they block main function

def warm_up(start_meas, data_raw):
    try:
        print('Waiting for warm-up for {} seconds. Press Ctl+C to escape.'.format(delay))
        start_warm_up = time.time()
        nt = time.time()
        
        length = int(delay / step)
        
        for i in range(length):

            [current, voltage] = smu_drain.measure_current_and_voltage()
            print('%.2f' % (nt - start_meas),  '%.5e' % current, '%.2f' % voltage)
            data_raw[i] = current

            while nt - start_warm_up < step * (i + 1):
                nt = time.time()
        print('End of warm-up')

    except KeyboardInterrupt:
        pass    

def acquisition(start_meas, arr, data_raw, offset):
    start_pulse = time.time()
    nt = time.time()
    laser_state = 0
    sm.write_lua("digio.writebit(1, 0)")
    
    for i in range(arr.size):
        if (i * step < laser_delay) or (i * step > laser_delay + laser): 
            laser_state = 0
            sm.write_lua("digio.writebit(1, {})".format(laser_state))
        else:
            laser_state = 1
            sm.write_lua("digio.writebit(1, {})".format(laser_state))
            

        [current, voltage] = smu_drain.measure_current_and_voltage()
        print('%.2f' % (nt - start_pulse), '%.5e' % current, '%.2f' % voltage, 'laser_state=', laser_state)
        arr[i] = current
        data_raw[i + offset] = current
        
   
        while nt - start_pulse < step * (i + 1):
            nt = time.time()   
   
    sm.write_lua("digio.writebit(1, 0)")



""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
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

'''
40 measurements (20В по 0.25) take time:
set_measurement_speed_hi_accuracy - 37 sec (1.41859e-09 A)
set_measurement_speed_fast - 2 sec (4.65035e-08 A, less precision)

SPEED_FAST / SPEED_MED / SPEED_NORMAL / SPEED_HI_ACCURACY
'''

""" ******* For saving the data ******** """

# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
filename_av = './data/' + 'PhotoCond_' + time_for_name + '_'  + sample_name + '_vds_' + str(drain_bias) +  '_cycles_' + str(periods) + '.csv'
filename_raw = './data/' + 'PhotoCond_' + time_for_name + '_'  + sample_name + '_raw' + '.csv'

""" ******* Do some measurements ******** """


# enable the output
smu_drain.enable_output()

# switch the laser off
sm.write_lua("digio.writebit(1, 0)")


smu_drain.set_voltage(drain_bias)

# check timing conditions
if period < laser + laser_delay:
    print("Check timing parameters - period, laser and laser_delay")
    exit()

period_length = int(period / step)
delay_length = int(delay / step)
data_raw_length = delay_length + period_length * periods

data_accum = np.zeros(period_length)
data_raw = np.zeros(data_raw_length)

timestamp_accum =  step * np.array(range(period_length))
timestamp_raw = step * np.array(range(data_raw_length))

# define variables we store the measurement in
column_names = []
lst_accum = []
lst_raw = []

column_names.append("Time (sec)")

lst_accum.append(timestamp_accum)
lst_raw.append(timestamp_raw)

print("Sample set name: ", sample_name)

while True:
    print('Enter sample label (or press Enter to finish): ')
    sample_label = input()
    if sample_label == "":
        break

    data_accum.fill(0.0)
    data_raw.fill(0.0)
    
    column_names.append(sample_label)
    data_acq = np.zeros(period_length)
    
    start_meas = time.time()
    warm_up(start_meas, data_raw)

    plt.ion()  # enable interactivity
    fig = plt.figure()  # make a figure
    ax = fig.add_subplot(111)
    line1, = ax.plot(timestamp_accum, data_accum, color='blue', linewidth=2)
    plt.xlabel('Time / s', fontsize=14)
    plt.ylabel('Voltage / V', fontsize=14)
    plt.title(time_for_title, fontsize=14)
    plt.tick_params(labelsize = 14)


    try:
        print('Measurement started. Press Ctl+C to escape')
        for i in range(periods):
            offset = delay_length + i * period_length
            acquisition(start_meas, data_acq, data_raw, offset)
            
            print('Cycle ', i + 1, ' from ', periods)

            data_accum += data_acq
                        
            line1.set_xdata(timestamp_accum)
            line1.set_ydata(data_accum / (i + 1))
            ax.relim()
            ax.autoscale()
            fig.canvas.draw()
            fig.canvas.flush_events()

    except KeyboardInterrupt:
        sm.write_lua("digio.writebit(1,0)")

    plt.ioff()

    data_accum = data_accum / periods
    
    lst_accum.append(data_accum.copy())
    lst_raw.append(data_raw.copy())
    
    np_data_accum   = np.stack(lst_accum, axis=0)
    np_data_raw     = np.stack(lst_raw, axis=0)
    
    delim = ','
    column_names_str = delim.join(column_names)
    np.savetxt(filename_av, np_data_accum.T, fmt='%.10g', delimiter=',', header=column_names_str) 

    np.savetxt(filename_raw, np_data_raw.T, fmt='%.10g', delimiter=",", header = column_names_str)

    plt.plot(timestamp_accum, data_accum, label = sample_label, color='red', linewidth=2)
    plt.xlabel('Time (sec)', fontsize=14)
    plt.ylabel('Current (A)', fontsize=14)
    plt.title(time_for_title + r', $Periods$ = ' + str(periods) + r', $V$ = ' + str(drain_bias), fontsize=14)
    plt.tick_params(labelsize = 14)
    plt.legend(loc = 'upper right')
    plt.show()
    
    # sound alarm - end of accumulation
#    print('\a')
    for i in range(3):
        winsound.Beep(1000, 300)
    

fig = plt.figure(figsize=(8,6))
for i in range(np_data_accum.shape[0]-1):
    plt.plot(np_data_accum[0, :], np_data_accum[i+1,:], label = column_names[i + 1], linewidth=2)
plt.xlabel('Time (s)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title(time_for_title, fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc='upper left')
plt.savefig(filename_av[:-4] + '.png')
plt.show()