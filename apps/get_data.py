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
THRESHOLD_TO_GET_END_PHASE = 10
THRESHOLD_TO_GET_END_AMPLITUDE = 0.05

MARGIN_TO_EVALUATE_360 = 3

#
# Signal State flows READY -> UP1 -> DOWN -> UP2 -> START -> END
#
#       **  READY  -------  DOWN  -------  START
#          _______| UP1  |_______|  UP2 |_______
#                  < Amplitude >
#
#       ** -----  END           ----- **       ** ----- END
#               |_____ or _____| END                  |_____
#                  < Phase >                    <Amplitude>
#
class SignalState(enum.Enum):

    READY = 0
    UP1 = 1
    DOWN = 2
    UP2 = 3
    START = 4
    END = 5

#
# Set target data types to enum
#
class DataType(enum.Enum):

    PHASE = 0
    AMPLITUDE = 1

#
# Make log of data using given file type and data type
#
def make_file_by_step(file_name):

    global STEP_CUT_OFF
    global SAMPLES_PER_STEP

    src = np.fromfile(open('../result/' + file_name), dtype=np.float32)
    csv_file = open('../csv/' + file_name + '.csv', 'w')
    csv_wr = csv.writer(csv_file, delimiter=',')

    # Get the number of samples to cut off
    samples_of_step_cut_off = (int)(SAMPLES_PER_STEP * STEP_CUT_OFF)
    samples_of_cut_off_result = (int)(SAMPLES_PER_STEP * (1.0 - 2.0*(STEP_CUT_OFF)))
    avg_value = 0
    for step in range(0, len(src)-SAMPLES_PER_STEP, SAMPLES_PER_STEP):
        for sample in range(samples_of_step_cut_off, \
                            SAMPLES_PER_STEP-samples_of_step_cut_off):
            avg_value += src[step + sample]
        avg_value /= samples_of_cut_off_result
        csv_wr.writerow([avg_value])
        avg_value = 0

    csv_file.close()

#
# Get start point of signal by detecting start pattern
# Signal states are described above
#
def detect_start(src, sample_rate):

    global VARIATION_OF_START_SIGNAL_MIN
    global COMPARE_SAMPLE_INTERVAL
    global BEGIN_CUT_OFF
    global SAMPLES_PER_STEP

    # Set source file's location
    # Set location to read
    cut_off_samples = (int)(BEGIN_CUT_OFF * sample_rate)

    # Find start point
    # Set start_flag to READY
    state = SignalState.READY
    ready_idx = 0
    for i in range(cut_off_samples + COMPARE_SAMPLE_INTERVAL, len(src)):
        # Set new prev_amp
        prev_amp = abs(src[i - COMPARE_SAMPLE_INTERVAL])
        amp = abs(src[i])
        variation_of_amp = amp - prev_amp

        # If the variation of amplitude is larger than threshold
        # Increase: READY->UP1, DOWN->UP2
        if ((variation_of_amp > (VARIATION_OF_START_SIGNAL_MIN * amp))):
            # Check the signal's state and move next state
            if (state is SignalState.READY):
                state = SignalState.UP1
                ready_idx = i
            elif (state is SignalState.DOWN):
                state = SignalState.UP2

        # Decrease: UP1->DOWN, UP2->START
        elif ((-variation_of_amp > (VARIATION_OF_START_SIGNAL_MIN * prev_amp))):
            # Check the signal's state and move next
            if (state is SignalState.UP1):
                state = SignalState.DOWN
            elif (state is SignalState.UP2):
                state = SignalState.START

        # If the state is START, then return start point
        if (state is SignalState.START):
            start_point  = i
            break

    # Fail to detect start pattern
    if (state is not SignalState.START):
        print('\n<< Fail to detect start pattern >>\n')
        sys.exit()

    # Print the result
    SAMPLES_PER_STEP = (start_point - ready_idx) / 3
    print('\n<< Success to detect start pattern >>\n')

    return start_point

#
# Get end point of stage with varying data
# If end point is not detected, then use samples per step obtained before
#
def detect_end(src, start_point, steps, varying_data):

    global COMPARE_SAMPLE_INTERVAL
    global SAMPLES_PER_STEP
    global THRESHOLD_TO_GET_END_PHASE
    global THRESHOLD_TO_GET_END_AMPLITUDE

    # Get end point using start point and total steps
    state = SignalState.START
    last_step_start_point = start_point + (steps - 1) * SAMPLES_PER_STEP
    if (varying_data is DataType.PHASE):
        for i in range(last_step_start_point, last_step_start_point + 2 * SAMPLES_PER_STEP):
            # Set new prev_phase
            phase = math.degrees(cmath.phase(src[i]))
            next_phase = math.degrees(cmath.phase(src[i + COMPARE_SAMPLE_INTERVAL]))
            variation_of_phase = abs(phase - next_phase)
            if (variation_of_phase > THRESHOLD_TO_GET_END_PHASE):
                print('\n<< Detect end point >>')
                state = SignalState.END
                end_point = i
                samples_in_target = end_point - start_point
                SAMPLES_PER_STEP = (samples_in_target + SAMPLES_PER_STEP * 3) / (steps + 3)
                break
    elif (varying_data is DataType.AMPLITUDE):
        for i in range(last_step_start_point, last_step_start_point + 2 * SAMPLES_PER_STEP):
            # Set new prev_amp
            amp = abs(src[i])
            next_amp = abs(src[i + COMPARE_SAMPLE_INTERVAL])
            variation_of_amp = abs(amp - next_amp)
            if (variation_of_amp > THRESHOLD_TO_GET_END_AMPLITUDE):
                print('\n<< Detect end point >>')
                state = SignalState.END
                end_point = i
                samples_in_target = end_point - start_point
                SAMPLES_PER_STEP = (samples_in_target + SAMPLES_PER_STEP * 3) / (steps + 3)
                break

    # Fail to detect end point, then guess the end point
    # Set end point using start point and total steps
    if (state is not SignalState.END):
        print('\n<< Fail to detect end point >>')
        end_point = start_point + (steps) * SAMPLES_PER_STEP

    print('Samples per step: ' + str(SAMPLES_PER_STEP))
    print('Samples in stage: ' + str(end_point - start_point) + '\n')
    src_target = src[start_point:end_point]

    if (varying_data is DataType.PHASE):
        src_target.tofile('../result/' + file_name + '_target0')
    elif (varying_data is DataType.AMPLITUDE):
        src_target.tofile('../result/' + file_name + '_target1')


    return end_point

#
# Get start point(sample index) and end point of signal
# Make target binary file: (file_name)_target0,  (file_name)_target0
# target0: phase is varying, target1: amplitude is varying
#
def detect_target(file_name, sample_rate, steps1, steps2):

    src = np.fromfile(open('../result/' + file_name), dtype=np.complex64)

    start_point = detect_start(src, sample_rate)
    end_point = detect_end(src, start_point, steps1, DataType.PHASE)
    detect_end(src, end_point, steps2, DataType.AMPLITUDE)

#
# Make binary/csv files to save amplitude
# File format: (file_name)_amp, (file_name)_amp.csv
#
def get_amp(file_name, steps, file_idx):

    # Set source file's location
    src = np.fromfile(open('../result/' + file_name + '_target' + str(file_idx)), \
                            dtype=np.complex64)
    new_file_name = file_name + '_amp' + str(file_idx)
    dest = '../result/' + file_name + '_amp' + str(file_idx)

    # Get amplitude
    amp_list = []
    for i in range(len(src)):
        amp = abs(src[i])
        amp_list.append(amp)

    # Make binary file
    amp_list_np = np.asarray(amp_list, dtype=np.float32)
    amp_list_np.tofile(dest)

    # Make csv file by steps
    make_file_by_step(new_file_name)

#
# Make binary/csv files to save phase in degree
# File format: (file_name)_phase, (file_name)_phase.csv
#
def get_phase(file_name, steps, file_idx):

    global MARGIN_TO_EVALUATE_360
    global SAMPLES_PER_STEP

    # Set source and destination location
    src = np.fromfile(open('../result/' + file_name + '_target' + str(file_idx)), \
                            dtype=np.complex64)
    new_file_name = file_name + '_phase' + str(file_idx)
    dest = '../result/' + file_name + '_phase' + str(file_idx)

    # Save first sample and set it to prev_phase
    phase_list = []
    is_360 = False
    is_0 = False
    is_enter = False
    start_index_fluctuation = 0
    end_index_fluctuation = 0
    for i in range(len(src)):
        phase = cmath.phase(src[i])
        if (phase < 0):
            phase += 2 * math.pi
        phase_in_degree = math.degrees(phase)

        # Detect sample whose phase is about 2pi
        if (phase_in_degree > 360 - MARGIN_TO_EVALUATE_360):
            is_360 = True
            if (not is_0):
                # Tendency to increase
                if ((phase - cmath.phase(src[i/2])) > 0):
                    is_tend_inc = True
                # Tendency to decrease
                else:
                    is_tend_inc = False

        # Detect sample whose phase is about 0
        if (phase_in_degree < 0 + MARGIN_TO_EVALUATE_360):
            is_0 = True
            if (not is_360):
                # Tendency to increase
                if ((phase - cmath.phase(src[i/2])) > 0):
                    is_tend_inc = True
                # Tendency to decrease
                else:
                    is_tend_inc = False

        # After detect 0 and 360
        if (is_0 and is_360):
            # Set entering two steps to fluctuation region
            if (not is_enter):
                is_enter = True
                start_index_of_fluctuation = i
                end_index_of_fluctuation = i + 2 * SAMPLES_PER_STEP

            # In Fluctuation regin
            if (i < end_index_of_fluctuation):
                if (is_tend_inc):
                    if (not phase_in_degree > 360 - MARGIN_TO_EVALUATE_360):
                        phase_in_degree += 360
                else:
                    if (not phase_in_degree < 0 + MARGIN_TO_EVALUATE_360):
                        phase_in_degree -= 360
            else:
                if (is_tend_inc):
                    phase_in_degree += 360
                else:
                    phase_in_degree -= 360
        phase_list.append(phase_in_degree)

    # Make binary file
    phase_list_np = np.asarray(phase_list, dtype=np.float32)
    phase_list_np.tofile(dest)

    # Make csv file by steps
    make_file_by_step(new_file_name)

#
# Call get_amp & get_phase to get amplitude & phase
# steps1: # of steps in Phase varying stage
# steps2: # of steps in Amplitude varying stage
#
def get_data(file_name, sample_rate, steps1, steps2):

    detect_target(file_name, sample_rate, steps1, steps2)
    get_phase(file_name, steps1, 0)
    get_amp(file_name, steps1, 0)
    get_phase(file_name, steps2, 1)
    get_amp(file_name, steps2, 1)


if __name__ == '__main__':

    # Set parameter dynamically
    #file_name = sys.argv[1]
    #sample_rate = (float)(sys.argv[2])
    #total_steps = (int)(sys.argv[3])

    # Set parameter statically
    file_name = 'data'
    sample_rate = 2000000
    steps1 = 99
    steps2 = 49

    # Get Data
    get_data(file_name, sample_rate, steps1, steps2)
