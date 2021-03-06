"""
This module get phase from source file with corresponding step sizes.
Example:
    $ python get_data.py data
"""
# -*- coding: utf-8 -*-
import cmath
import math
import sys
import enum
import csv
import numpy as np

SAMPLES_PER_STEP = 0

class SignalState(enum.Enum):
    """
    Signal State flows READY -> UP1 -> DOWN -> UP2 -> START -> END

       **  READY  -------  DOWN  -------  START
          _______| UP1  |_______|  UP2 |_______
                  < Amplitude >

       ** -----  END           ----- **       ** ----- END
               |_____ or _____| END                  |_____
                   < Phase >                    <Amplitude>
    """
    READY = 0
    UP1 = 1
    DOWN = 2
    UP2 = 3
    START = 4
    END = 5

class DataType(enum.Enum):
    """
    Set target data types to enum.
    """
    PHASE = 0
    AMPLITUDE = 1

def make_csv_by_step(target, dest_csv_name, steps):
    """
    Make csv file using target with corresponding steps.
    Args:
        target: Data array from target
        dest_csv_name: Prefix of name to save result file
        steps: The number of steps in each stages
    Outputs:
        (dest_csv_name)_(stage#).csv: Result of phase measurement from each stages
    """
    global SAMPLES_PER_STEP

    step_cut_off = 0.1 # Cut off ratio of measurement
    fluctuation_degree = 180

    # Get the number of samples to cut off
    samples_of_step_cut_off = (int)(SAMPLES_PER_STEP * step_cut_off)
    samples_of_cut_off_result = (int)(SAMPLES_PER_STEP * (1.0 - 2.0*(step_cut_off)))
    avg_value = 0
    start_idx_stage = 0
    end_idx_stage = 0
    for idx, step in enumerate(steps):
        if idx == (len(steps) - 1):
            step += 1
        csv_file = open('../csv/' + dest_csv_name + str(idx) + '.csv', 'w')
        csv_wr = csv.writer(csv_file, delimiter=',')
        start_idx_stage = end_idx_stage
        end_idx_stage += step * SAMPLES_PER_STEP
        for ith_step in range(step):
            start_idx_ith_step = start_idx_stage + ith_step * SAMPLES_PER_STEP
            end_idx_ith_step = start_idx_stage + (ith_step+1) * SAMPLES_PER_STEP

            init_data = target[start_idx_ith_step + samples_of_step_cut_off]
            for data_idx in range(start_idx_ith_step + samples_of_step_cut_off,
                                  end_idx_ith_step - samples_of_step_cut_off):
                if init_data - target[data_idx] > fluctuation_degree:
                    target[data_idx] += 360
                elif -(init_data - target[data_idx]) > fluctuation_degree:
                    target[data_idx] -= 360
                avg_value += target[data_idx]
            avg_value /= samples_of_cut_off_result
            csv_wr.writerow([avg_value])
            avg_value = 0
        csv_file.close()

def get_phase(target, src_file_name, creation_flag):
    """
    Make binary/csv files to save phase in degree.
    Args:
        target: Data array from target
        src_file_name: Name of source file
        creation_flag: Flag to determine whether save files during process
    Outpus:
        ** If creation_flag is True, then below file is created **
        (dest_file_name): Target data file from source file
    Returns:
        phase_list_np: Phase array from target
    """
    global SAMPLES_PER_STEP

    path = '../result/'
    dest_file_name = src_file_name + '_phase'

    phase_list = []
    for data in target:
        phase = cmath.phase(data)
        if phase < 0:
            phase += 2 * math.pi
        phase_in_degree = math.degrees(phase)
        phase_list.append(phase_in_degree)

    # Make binary file
    phase_list_np = np.asarray(phase_list, dtype=np.float32)
    if creation_flag:
        phase_list_np.tofile(path + dest_file_name)

    return phase_list_np

def detect_end(src, start_point, total_steps):
    """
    Get end point of stage with varying data.
    If end point is not detected, then use samples per step obtained before.
    Args:
        src: Data array from source file
        start_point: Start index of data we measure
        total_steps: The number of all steps in measurement
    Returns:
        end_point_padd: Index of end point after padding
    """
    global SAMPLES_PER_STEP

    threshold_to_get_end_amplitude = 0.03   # Threshold to evaluate end pattern
    compare_sample_interval = 10    # Number of samples in comparing interval

    # Get end point using start point and total steps
    state = SignalState.START
    last_step_start_point = start_point + (total_steps-1)*SAMPLES_PER_STEP
    for i in range(last_step_start_point, last_step_start_point + 2 * SAMPLES_PER_STEP):
        # Set new prev_amp
        amp = abs(src[i])
        next_amp = abs(src[i + compare_sample_interval])
        variation_of_amp = abs(amp - next_amp)
        if variation_of_amp > threshold_to_get_end_amplitude:
            print('\n<< Detect end point >>')
            state = SignalState.END
            end_point = i
            samples_in_target = end_point - start_point
            SAMPLES_PER_STEP = (samples_in_target + 3*SAMPLES_PER_STEP)/(total_steps + 3)
            break

    # Fail to detect end point, then guess the end point
    # Set end point using start point and total steps
    if state is not SignalState.END:
        print('\n<< Fail to detect end point >>')
        end_point = start_point + (total_steps) * SAMPLES_PER_STEP

    # Padding one step for validation check
    end_point_padd = end_point + 2 * SAMPLES_PER_STEP
    print('Samples per step: ' + str(SAMPLES_PER_STEP))
    print('Samples in target: ' + str(end_point_padd - start_point) + '\n')

    return end_point_padd

def detect_start(src):
    """
    Get start point of signal by detecting start pattern.
    Signal states are described above class named SignalState.
    Args:
        src: Data array from source file
    Returns:
        start_point: Start index of data we measure
    """
    global SAMPLES_PER_STEP

    min_variation_of_start_signal = 0.03     # Minimum amp difference in pattern
    compare_sample_interval = 10    # Number of samples in comparing interval
    begin_cut_off = 500000     # Number of samples to cutoff (about 1/4 of sample rate)

    # Detect start pattern
    state = SignalState.READY
    for i in range(begin_cut_off + compare_sample_interval, len(src)):
        prev_amp = abs(src[i - compare_sample_interval])
        amp = abs(src[i])
        variation_of_amp = amp - prev_amp

        # Increase: READY->UP1, DOWN->UP2
        if variation_of_amp > (min_variation_of_start_signal):
            if state is SignalState.READY:
                state = SignalState.UP1
                up1_idx = i
            elif state is SignalState.DOWN:
                state = SignalState.UP2

        # Decrease: UP1->DOWN, UP2->START
        elif (-variation_of_amp) > (min_variation_of_start_signal):
            if state is SignalState.UP1:
                state = SignalState.DOWN
            elif state is SignalState.UP2:
                state = SignalState.START
                start_point = i
                break

    # Fail to detect start pattern
    if state is not SignalState.START:
        print('\n<< Fail to detect start pattern >>\n')
        sys.exit()

    # Print the result
    SAMPLES_PER_STEP = (start_point - up1_idx) / 3
    print('\n<< Success to detect start pattern >>')
    print('Start point: ' + str(start_point))
    print('Samples per step: ' + str(SAMPLES_PER_STEP) + '\n')

    return start_point

def detect_target(src_file_name, target_file_name, steps, creation_flag):
    """
    Get start point(sample index) and end point of signal.
    Args:
        src_file_name: Name of source file
        target_file_name: Name of target file
        steps: The number of steps in each stages
        creation_flag: Flag to determine whether save files during process
    Outputs:
        ** If creation_flag is True, then below file is created **
        (target_file): Target data file from source file
    Returns:
        target_data: Array with target data
    """
    path = '../result/'
    src = np.fromfile(open(path + src_file_name), dtype=np.complex64)

    start_point = detect_start(src)
    end_point = detect_end(src, start_point, sum(steps))
    target_data = src[start_point:end_point]

    if creation_flag:
        target_data.tofile(path + target_file_name)

    return target_data

def get_data(src_file_name, steps, creation_flag):
    """
    Extract target data from source file and get phase/amplitude from target.
    Args:
        src_file_name: Name of source file
        steps: The number of steps in each stages
        creation_flag: Flag to determine whether save files during process
    Outputs:
        (dest_csv_name)_(stage#).csv: Result of phase measurement from each stages
        ** If creation_flag is True, then below file is created **
        (target_file_name): Target data file from source file
    """
    target_file_name = src_file_name + '_target'
    dest_csv_name = src_file_name

    target = detect_target(src_file_name, target_file_name,
                           steps, creation_flag)
    target_phase = get_phase(target, src_file_name, creation_flag)
    make_csv_by_step(target_phase, dest_csv_name, steps)

if __name__ == '__main__':
    # Set parameters
    SOURCE_FILE_NAME = sys.argv[1]
    STEPS = [100, 50]
    CREATION_FLAG = False

    # Get Data from source file
    get_data(SOURCE_FILE_NAME, STEPS, CREATION_FLAG)
