from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

import time, traceback

sample_name = 'GrGr-NPl-1week'

drain_bias = 1.0 # V
step = 0.4 # sec А вот 0.3 уже сбивается.
delay = 60 # sec Delay for warm-up
periods = 8 # periods of acqusition for averaging
laser_pulses = 2 # pulses inside a period
laser_on = 10 # sec
laser_off = 10  # sec

'''
period = laser_off + laser_pulses * (laser_on + laser_off)

measurement = delay + periods * period

'''

current_range = 3e-3

'''
Press Ctrl-C to terminate the loop.


'''
# надо рисование графиков в async/thread  перевести, чтобы не блокировали программу

def warm_up(start_meas, data_raw):
    try:
        print('Waiting for warm-up for {} seconds. Press Ctl+C to escape.'.format(delay))
        start_warm_up = time.time()
        nt = time.time()
        
        length = int(delay / step)
        
        for i in range(length):

            [current, voltage] = smu_drain.measure_current_and_voltage()
            # with open(filename_raw, 'a') as csvfile:
                # writer = csv.writer(csvfile, lineterminator='\n') 
                # writer.writerow([nt - start_meas, current])
            print(nt - start_meas, current, voltage)
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
    sm.write_lua("digio.writebit(1, {})".format(laser_state))
    
    for i in range(arr.size):
        length_on = int(laser_on / step)
        length_off = int(laser_off / step)
        a = i % (length_on + length_off)
        if a < length_off:
            laser_state = 0
            sm.write_lua("digio.writebit(1, {})".format(laser_state))
        else:
            laser_state = 1
            sm.write_lua("digio.writebit(1, {})".format(laser_state))
            
 # надо ввести деление на длину и смотреть остаток вместо трех сравнений
        # a = i % (int(laser_on / step) + int(laser_off / step))
        # if (a > int(laser_off / step) ) and (laser_state == 0):
            # laser_state = 1
            # sm.write_lua("digio.writebit(1, {})".format(laser_state))
        # elif (a < int(laser_off / step) ) and (laser_state == 1):
            # laser_state = 0
            # sm.write_lua("digio.writebit(1, {})".format(laser_state))

       
 # # for laser_before, laser_on and laser_off
        # if (i > laser_before / step) and (i < (laser_on + laser_before) / step) and (laser_state == 0):
            # laser_state = 1
            # sm.write_lua("digio.writebit(1, {})".format(laser_state))
        # elif (i > (laser_on + laser_before) / step) and (laser_state == 1):
            # laser_state = 0
            # sm.write_lua("digio.writebit(1, {})".format(laser_state))
        



        [current, voltage] = smu_drain.measure_current_and_voltage()
        # with open(filename_raw, 'a') as csvfile:
            # writer = csv.writer(csvfile, lineterminator='\n') 
            # writer.writerow([nt - start_meas, current])
        print(nt - start_meas, current, voltage)
        arr[i] = current
        data_raw[i + offset] = current
        
   
        while nt - start_pulse < step * (i + 1):
            nt = time.time()   
   
    laser_state = 0
    sm.write_lua("digio.writebit(1, {})".format(laser_state))







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


#smu_ch.set_measurement_speed_hi_accuracy()
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
filename_av = './data/' + 'PhotoCond_' + time_for_name + '_'  + sample_name + '_vds_' + str(drain_bias) +  '_cycles_' + str(periods) + '.csv'
filename_raw = './data/' + 'PhotoCond_' + time_for_name + '_'  + sample_name + '_raw' + '.csv'

""" ******* Make a voltage-sweep and do some measurements ******** """


# enable the output
smu_drain.enable_output()

# switch the laser off
sm.write_lua("digio.writebit(1, 0)")


smu_drain.set_voltage(drain_bias)

period_length = laser_pulses * (int(laser_off/ step) + int(laser_on / step)) + int(laser_off/ step)
#period_length = int(laser_off/ step) + int(laser_on / step) + int(laser_before / step)
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
#column_names += "Voltage (V)"

lst_accum.append(timestamp_accum)
lst_raw.append(timestamp_raw)

print("Sample name: ", sample_name)



while True:
    print('Enter sample number: ')
    sample_num = input()
    if sample_num == "":
        break


    data_accum.fill(0.0)
    data_raw.fill(0.0)
    
    column_names.append(sample_num)
    data_acq = np.zeros(period_length)
    
    start_meas = time.time()
    warm_up(start_meas, data_raw)

    plt.ion()  # enable interactivity
    fig = plt.figure()  # make a figure
    ax = fig.add_subplot(111)
    line1, = ax.plot(timestamp_accum, data_accum, color='blue', linewidth=2)
    #line1, = ax.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
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
            
 #           raw_pos = delay_length + i * period_length
 #           data_raw[raw_pos:(raw_pos + period_length)] = data_acq

                        
            line1.set_xdata(timestamp_accum)
            line1.set_ydata(data_accum / (i + 1))
            ax.relim()
            ax.autoscale()
            fig.canvas.draw()
            fig.canvas.flush_events()

    except KeyboardInterrupt:
        sm.write_lua("digio.writebit(1,{})".format(0))

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



    plt.plot(timestamp_accum, data_accum, label = 'I(t)', color='red', linewidth=2)
    plt.xlabel('Time (sec)', fontsize=14)
    plt.ylabel('Current (A)', fontsize=14)
    plt.title(time_for_title + r', $Periods$ = ' + str(periods) + r', $V$ = ' + str(drain_bias), fontsize=14)
    plt.tick_params(labelsize = 14)
    plt.legend(loc = 'upper right')
    plt.show()
    
    # sound alarm - end of accumulation
    print('\a')



fig = plt.figure(figsize=(8,6))
for i in range(np_data_accum.shape[0]-1):
    plt.plot(np_data_accum[0, :], np_data_accum[i+1,:], label = column_names[i + 1], linewidth=2)
plt.xlabel('Time (s)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title(time_for_title, fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc='upper left')
plt.show()