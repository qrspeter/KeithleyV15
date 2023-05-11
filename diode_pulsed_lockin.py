# для измерения напряжения на резисторе не подавая ан него смещение от Кейтли, тк на нео и так подается переменное напряжение, а сигнал снимается с выхода синхронного детектора

from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

# может интервал задавать в секундах, и внутри них уже считать? А то сейчас не предсказать длительность интервала.

#drain_bias = 1.0
cycles = 4
measurements = 30
halfperiods = 5
data_length = measurements * halfperiods

sample_name = 'rGO_B_DC_px5'

delay = 60

current_range = 1e-3
'''
Press Ctrl-C to terminate the loop.


'''




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
#smu_drain.set_voltage(0)
smu_drain.set_current_range(current_range)
smu_drain.set_current_limit(current_range)
#smu_drain.set_current(0)

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
filename_csv = './data/' + 'PhotoVolt_' + time_for_name + '_'  + sample_name +  '_cycles_' + str(cycles) + '.csv'
filename_raw_csv = './data/' + 'PhotoVolt_' + time_for_name + '_'  + sample_name + '_raw' + '.csv'

#initializing a CSV file, to which the measurement data will be written - if this script is used to measure another characteristic than the U/I curve, this has to be changed
# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow(["# Time / sec", "Voltage / V"])

""" ******* Make a voltage-sweep and do some measurements ******** """

# define variables we store the measurement in
data_accum = np.zeros((data_length, 2))
acquisition = np.zeros(data_length)

# enable the output
smu_drain.enable_output()
sm.write_lua("digio.writebit(1, 0)")


#smu_drain.set_voltage(drain_bias)
start = time.time()

try:
    print('Waiting for warm-up for {} seconds. Press Ctl+C to escape'.format(delay))
    t = time.time() - start
    while True and t < delay:
        voltage = smu_drain.measure_voltage()
        t = time.time() - start
        with open(filename_raw_csv, 'a') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n') # default delimiter=',', lineterminator='\r\n' 
            writer.writerow([t, voltage]) 
        print('Time ' + str(int(t)) + ' sec, Voltage ' + str(voltage))
#        time.sleep(3)
except KeyboardInterrupt:
    pass    
    
    

    
# step through the voltages and get the values from the device
cycle = 0
start_av = time.time()
try:
    print('Measurement started. Press Ctl+C to escape')
    while True and cycle < cycles:

        for i in range(halfperiods):
            
            sm.write_lua("digio.writebit(1, {})".format(i%2))
            
            for j in range(measurements):
                curr_elem = i * measurements + j
                voltage = smu_drain.measure_voltage()
                acquisition[curr_elem] = voltage
                t = time.time() - start
                if cycle == 0:
                    data_accum[curr_elem, 0] = t - (start_av - start)
                print('Cycle ' + str(cycle) + ', Point ' + str(curr_elem) + ', Voltage ' + str(voltage))
                    
                # Write the raw data in a csv
                with open(filename_raw_csv, 'a') as csvfile:
                    writer = csv.writer(csvfile, lineterminator='\n') # default delimiter=',', lineterminator='\r\n' 
                    writer.writerow([t, voltage])
        data_accum[:, 1] += acquisition
            
            
            
        cycle += 1    
        

except KeyboardInterrupt:
    sm.write_lua("digio.writebit(1,{})".format(0))
    #pass

sm.write_lua("digio.writebit(1,{})".format(0))

# disable the output
smu_drain.disable_output()
#    smu_gate.disable_output()


    # properly disconnect from the device
sm.disconnect()

if cycle == 0:
    cycle += 1

data_accum[:, 1] = data_accum[:, 1]/cycle

np.savetxt(filename_csv, data_accum, delimiter=",", header = 'Time / sec, \tVoltage / V') # fmt='%.3f', 


""" ******* Plot the Data we obtained ******** """

plt.plot(data_accum[:,0], data_accum[:, 1], label = r'$V_{lock-in}$', color='red', linewidth=2)
#plt.plot(time_arr, gate_current, label = r'$I_{GS}$', color='black', linestyle='dashed', linewidth=1)

# set labels and a title
plt.xlabel('Time / s', fontsize=14)
plt.ylabel('Voltage / V', fontsize=14)
plt.title(time_for_title + r', $Cycles$ = ' + str(cycle), fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc = 'upper right')

plt.show()
