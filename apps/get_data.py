import cmath
import math
import sys
import enum
import csv
import numpy as np

#
# VALID_CHECK: Valid phase difference in degree
#
STEP_CUT_OFF = 0.1
VALID_CHECK = 3

VARIATION_OF_START_SIGNAL_MIN = 0.2
COMPARE_SAMPLE_INTERVAL = 10

BEGIN_CUT_OFF = 0.1
SAMPLES_PER_STEP = 0

#
# Signal State flows READY -> DOWN1 -> UP -> DOWN2 -> START
# 
#       ** -------  DOWN  ------  START  **
#           READY |______|  UP  |_______
#
class SignalState(enum.Enum):

    READY = 0
    DOWN = 1
    UP = 2
    START = 3

#
# Set target data types to enum
#
class TargetData(enum.Enum):

    AMPLITUDE = 0
    PHASE = 1

#
# Make log of data using given file type and data type
#
def make_file_by_step(file_name, data_type):

    global STEP_CUT_OFF
    global SAMPLES_PER_STEP
    
    if (data_type is TargetData.AMPLITUDE):
        src = np.fromfile(open('../result/' + file_name + '_amp'), dtype=np.float32)
        csv_file = open('../csv/' + file_name + '_amp.csv', 'w')
        csv_wr = csv.writer(csv_file, delimiter=',')

    elif (data_type is TargetData.PHASE):
        src = np.fromfile(open('../result/' + file_name + '_phase'), dtype=np.float32)
        csv_file = open('../csv/' + file_name + '_phase.csv', 'w')
        csv_wr = csv.writer(csv_file, delimiter=',')
    
    else:
        print('\n<< Data type error >>\n')
        sys.exit()
    
    # Get the number of samples to cut off
    samples_of_step_cut_off = (int)(SAMPLES_PER_STEP * STEP_CUT_OFF)
    samples_of_cut_off_result = (int)(SAMPLES_PER_STEP * (1.0 - 2.0*(STEP_CUT_OFF)))
    avg_value = 0
    for step in range(0, len(src), SAMPLES_PER_STEP):
        for sample in range(samples_of_step_cut_off, \
                            SAMPLES_PER_STEP-samples_of_step_cut_off):
            avg_value += src[step + sample]
        avg_value /= samples_of_cut_off_result
        csv_wr.writerow([avg_value])
        avg_value = 0
    
    csv_file.close()

#
# Compare first step and valid check step which appear after last step 
# First step and valid check step are controled to have same phase
#
def check_is_valid(first_step, valid_check_step):    

    global SAMPLES_PER_STEP
    global VALID_CHECK
    
    # Get the number of samples to cut off
    samples_of_step_cut_off = (int)(SAMPLES_PER_STEP * STEP_CUT_OFF)

    # Get the steps from result cutting off
    first_step_cut_off = first_step[samples_of_step_cut_off: -samples_of_step_cut_off]
    valid_check_step_cut_off = \
            valid_check_step[samples_of_step_cut_off: -samples_of_step_cut_off]
    
    # Get average phase of pulse in step
    samples_of_cut_off_result = len(first_step_cut_off)
    avg_phase_first_step = 0
    avg_phase_valid_check_step = 0
    for i in range(samples_of_cut_off_result):
        avg_phase_first_step += cmath.phase(first_step_cut_off[i])
        avg_phase_valid_check_step += cmath.phase(valid_check_step_cut_off[i])
    avg_phase_first_step /= samples_of_cut_off_result * 1.0
    avg_phase_valid_check_step /= samples_of_cut_off_result * 1.0
    
    if (avg_phase_first_step < 0):
        avg_phase_first_step += 2 * math.pi
    if (avg_phase_valid_check_step < 0):
        avg_phase_valid_check_step += 2* math.pi

    phase_gap_degree = abs(math.degrees(avg_phase_first_step) - \
                            math.degrees(avg_phase_valid_check_step))
    if (phase_gap_degree < VALID_CHECK):
        is_valid = True
        print('\n<< Valid >>')
        print('Phase gap in degree: ' + str(phase_gap_degree) + '\n')
    else:
        is_valid = False
        print('\n<< Unvalid >>')
        print('Phase gap in degree: ' + str(phase_gap_degree) + '\n')
    
    return is_valid


#
# Get start point(sample index) and end point of signal
# Make target binary file: (file_name)_target
#
def detect_target(file_name, sample_rate, total_steps):
   
    global VARIATION_OF_START_SIGNAL_MIN
    global COMPARE_SAMPLE_INTERVAL
    global BEGIN_CUT_OFF
    global SAMPLES_PER_STEP

    # Set source file's location
    # Set location to read
    src = np.fromfile(open('../result/' + file_name), dtype=np.complex64)
    cut_off_samples = (int)(BEGIN_CUT_OFF * sample_rate)
    
    # Find start point
    # Set start_flag to READY
    state = SignalState.READY
    for i in range(cut_off_samples + COMPARE_SAMPLE_INTERVAL, len(src)):
        # Set new prev_amp 
        prev_amp = abs(src[i - COMPARE_SAMPLE_INTERVAL])
        amp = abs(src[i])      
        variation_of_amp = amp - prev_amp

        # If the variation of amplitude is larger than threshold 
        # Increase: DOWN->UP
        if ((variation_of_amp > (VARIATION_OF_START_SIGNAL_MIN * amp))):
            # Check the signal's state and move next state
            if (state is SignalState.DOWN):
                state = SignalState.UP
                samples_in_down = i - down_start
                up_start = i
        
        # Decrease: READY->DOWN, UP->START
        elif ((-variation_of_amp > (VARIATION_OF_START_SIGNAL_MIN * prev_amp))):
            # Check the signal's state and move next
            if (state is SignalState.READY):
                state = SignalState.DOWN
                down_start = i
            elif (state is SignalState.UP):
                state = SignalState.START
                samples_in_up = i - up_start
                SAMPLES_PER_STEP = (samples_in_up + samples_in_down) / 2
        
        # If the state is START, then return start point
        if (state is SignalState.START):
            start_point  = i
            break
    
    # Fail to detect start pattern
    if (state is not SignalState.START):
        print('\n<< Fail to detect start pattern >>\n')
        sys.exit()
    
    # Print the result
    print('\n<< Success to detect start pattern >>')
    print('Samples per step: ' + str(SAMPLES_PER_STEP) + '\n')
    
    # Set end point using start point and total steps
    end_point = start_point + (total_steps) * SAMPLES_PER_STEP
    
    # Check the target is valid
    first_step = src[start_point: start_point+SAMPLES_PER_STEP]
    valid_check_step = src[end_point + SAMPLES_PER_STEP: end_point + 2*SAMPLES_PER_STEP]
    if (check_is_valid(first_step, valid_check_step)):
        # Make binary file using target
        src_target = src[start_point:end_point]
        src_target.tofile('../result/' + file_name + '_target')
    else:
        print('\n<< Target is not valid >>\n')
        sys.exit()

# Make binary/csv files to save amplitude
# File format: (file_name)_amp, (file_name)_amp.csv
#
def get_amp(file_name, total_steps):
    
    # Set source file's location
    src = np.fromfile(open('../result/' + file_name + '_target'), dtype=np.complex64)

    # Get amplitude
    amp_list = []
    for i in range(len(src)):
        amp = abs(src[i])
        amp_list.append(amp)

    # Make binary file
    amp_list_np = np.asarray(amp_list, dtype=np.float32)
    amp_list_np.tofile('../result/' + file_name + '_amp')

    # Make csv file by steps
    make_file_by_step(file_name, TargetData.AMPLITUDE)
     
#
# Make binary/csv files to save [0, 2pi] phase in degree
# File format: (file_name)_phase, (file_name)_phase.csv
#
def get_phase(file_name, total_steps):
    
    # Set source file's location
    src = np.fromfile(open('../result/' + file_name + '_target'), dtype=np.complex64)
    
    # Save first sample and set it to prev_phase
    phase_list = []
    prev_phase = cmath.phase(src[0])
    if (prev_phase < 0):
        prev_phase += 2 * math.pi
    phase_list.append(prev_phase)

    # Get phase with range [0, 2pi]
    for i in range(1, len(src)):
        phase = cmath.phase(src[i])
        if (phase < 0):
            phase += 2 * math.pi
        
        phase_list.append(math.degrees(phase))
        prev_phase = phase

    # Make binary file
    phase_list_np = np.asarray(phase_list, dtype=np.float32)
    phase_list_np.tofile('../result/' + file_name + '_phase')

    # Make csv file by steps
    make_file_by_step(file_name, TargetData.PHASE)
    
#
# Call get_amp & get_phase to get amplitude & phase
# 
def get_data(file_name, sample_rate, total_steps):
    
    detect_target(file_name, sample_rate, total_steps)
    get_amp(file_name, total_steps)
    get_phase(file_name, total_steps)


if __name__ == '__main__':

    # Set parameter dynamically
    #file_name = sys.argv[1]
    #sample_rate = (float)(sys.argv[2])
    #total_steps = (int)(sys.argv[3])

    # Set parameter statically
    file_name = 'data'
    sample_rate = 2000000
    total_steps = 100

    # Get Data
    get_data(file_name, sample_rate, total_steps)

