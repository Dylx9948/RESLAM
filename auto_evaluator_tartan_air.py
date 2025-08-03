'''
Will open config file, run, extract results and then perform the next iteration, Just specify data here.
'''
from evo.core import metrics
from evo.core.metrics import Unit
from evo.tools import file_interface
from evo.core import sync
import copy
import pprint
from evo.tools import plot
import matplotlib.pyplot as plt
import matplotlib
from ruamel.yaml import YAML
import subprocess
import os
import numpy as np
from scipy.spatial.transform import Rotation
import os
import shutil
import time
import psutil
import signal
# Load your YAML file
yaml = YAML()
yaml.preserve_quotes = True
def replace_value(data, set_key, set_value):
    for key, value in data.items():
        if key == set_key:
            data[key] = set_value
    return data

def replace_path(data, path):
    for key, value in data.items():
        if key == "data":
            value['datadir'] = path
    return data
    
def replace_canny_value(data, lower, upper):
    for key, value in data.items():
        if key == "edge":
            value["canny_lower"] = lower
            value["canny_upper"] = upper
    return data

def process_file(input_file, output_file): #Use to create temp. file in TUM trajectory format for evaluation.
    with open(input_file, 'r') as f:
        lines = f.readlines()

    processed_lines = []

    for row_number, line in enumerate(lines):
        # Skip lines starting with comments or blank lines
        if line.strip().startswith("#") or not line.strip():
            continue

        # Split the line into values
        values = line.strip().split()

        # Prepend the row number to the values
        processed_line = [str(row_number)] + values

        # Ensure the line has exactly 8 entries (row number + 7 values)
        if len(processed_line) == 8:
            processed_lines.append(" ".join(processed_line))
        else:
            print(f"Warning: Skipping malformed line {row_number}: {line.strip()}")

    # Write the processed lines to the output file
    with open(output_file, 'w') as f:
        f.write("\n".join(processed_lines))
    print(f"Processed data written to {output_file}")

path_to_config = "config.yaml"
results_folder = "/home/dylanbrown/Desktop/results_folder"



dataset_array = [
                "/media/sf_Datasets/TartanAir/abandonedfactory",
                "/media/sf_Datasets/TartanAir/abandonedfactory_night",
                "/media/sf_Datasets/TartanAir/amusement",
                "/media/sf_Datasets/TartanAir/carwelding",
                "/media/sf_Datasets/TartanAir/endofworld",
                "/media/sf_Datasets/TartanAir/gascola",
                "/media/sf_Datasets/TartanAir/hospital",
                "/media/sf_Datasets/TartanAir/japanesealley",
                "/media/sf_Datasets/TartanAir/neighborhood",
                "/media/sf_Datasets/TartanAir/ocean",
                "/media/sf_Datasets/TartanAir/office",
                "/media/sf_Datasets/TartanAir/office2",
                "/media/sf_Datasets/TartanAir/oldtown",
                "/media/sf_Datasets/TartanAir/seasidetown",
                "/media/sf_Datasets/TartanAir/seasonsforest",
                "/media/sf_Datasets/TartanAir/seasonsforest_winter",
                "/media/sf_Datasets/TartanAir/soulcity",
                "/media/sf_Datasets/TartanAir/westerndesert",
]

canny_values = [[50, 100]]

#cx, cy, fx, fy for each dataset in same order as array:
camera_parameters = [[320.0, 240.0, 320.0, 320.0]]

print(len(dataset_array), len(canny_values), len(camera_parameters))

results_data = "Dataset name: \t ATE (m) \t RPE_t (m) \t RPE_R (deg) \t Frame Rate (fps)\n"

for k in range(0, len(dataset_array)):
    folder_path = dataset_array[k]
    subdirectories = [
        os.path.join(folder_path, item)
        for item in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, item))
    ]

    ape_list = []
    rpe_t_list = []
    rpe_r_list = []

    #Load data:
    for i in range(0, len(subdirectories)): #-1, -1, -1):


        #Get parameters to load in:

        #Dataset name:
        dataset_name = subdirectories[i]

        #Results path:
        results_name = "output.txt"
        results_name = "/home/reslam/Desktop/poses.txt"

    
        config_path = "/home/reslam/Documents/RESLAM-master_old/config_files/TARTAN.yaml"
    
        with open(config_path, 'r') as file: 
            lines = file.readlines()[1:]
        with open(config_path, 'w') as file: 
            file.writelines(lines)

        with open(config_path, 'r') as file:
            yaml_content = yaml.load(file)
    

        yaml_content["InputDatasetFolder"] = dataset_name

        with open(config_path, 'w') as file:
            yaml.dump(yaml_content, file)


        with open(config_path, 'r') as file: 
            lines = file.readlines()
        lines.insert(0,"%YAML:1.0\n")
        with open(config_path, 'w') as file: 
            file.writelines(lines)
        #Now run the program:
        print("Starting evaluator.")
        # Run main.py and wait for it to complete
        print('sudo', '/home/reslam/Documents/RESLAM-master_old/build/RESLAM', '/home/reslam/Documents/RESLAM-master_old/config_files/reslam_settings.yaml', config_path)
        t = time.time()
        result = subprocess.Popen(['sudo', '/home/reslam/Documents/RESLAM-master_old/build/RESLAM', '/home/reslam/Documents/RESLAM-master_old/config_files/reslam_settings.yaml', config_path])
        last_modified = os.path.getmtime("/home/reslam/Desktop/poses_kf.txt")
        counter = 0

        while (counter < 120 and (last_modified == os.path.getmtime("/home/reslam/Desktop/poses_kf.txt"))):
            counter += 1
            time.sleep(1)
        #result.kill()
        os.kill(result.pid, signal.SIGINT)
        parent = psutil.Process(result.pid)
        children = parent.children(recursive=True)
        for child in children: 
            os.kill(child.pid, signal.SIGINT)



        if result.returncode == 0:
            print("main.py ran successfully.")
            print("Output:", result.stdout)

        #EXtract the stored frame per second rate:
        if counter < 120: 
            with open(results_name, 'r') as file:
                run_time = time.time() - t
                # Read the first line
                first_line = file.readline()

                # Find the position of the 'FPS:' string
                fps_pos = first_line.find('FPS:')

                # Extract everything from 'FPS:' onward
                fps_result = len(file.readlines())/run_time


        #============================ CONVERT TO NED FROM CAMERA: TARTANAIR ONLY!!! ====================================
            est_file = results_name  # Default pose file name of TartanAir
            dst_folder = "results"
            dst_file = dst_folder + "/" + str(dataset_array[k].split("/")[-1] + "_" + str(subdirectories[i][-1])) + ".txt"
            os.makedirs(dst_folder, exist_ok=True)
            shutil.copy(est_file, dst_file)


            #Score:
            ref_file = dataset_name + "/groundtruth_tum.txt"
            if os.path.exists(ref_file):
                print(f"Reference file found: {ref_file}")
            else:
                ref_file = dataset_name + "/pose_left.txt" #Default pose file name of TartanAir

            #process_file(ref_file, "temp_gt.txt")
            est_file = results_name

            traj_ref = file_interface.read_tum_trajectory_file(ref_file)
            traj_est = file_interface.read_tum_trajectory_file(est_file)

            max_diff = 0.01

            traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est, max_diff)

            # Align trajectories:
            traj_est_aligned = copy.deepcopy(traj_est)
            traj_est_aligned.align(traj_ref, correct_scale=False, correct_only_scale=False)

            # Create data:
            data = (traj_ref, traj_est_aligned)

            # ATE:
            pose_relation = metrics.PoseRelation.translation_part
            ape_metric = metrics.APE(pose_relation)
            ape_metric.process_data(data)

            ape_stats = ape_metric.get_all_statistics()["rmse"]
            pprint.pprint(ape_stats)

            # RPE: m/s
            delta = 10
            delta_unit = Unit.frames  # Since Kinect is 30 fps, then delta = 30, means error per second.

            data = (traj_ref, traj_est)
            rpe_metric = metrics.RPE(pose_relation=pose_relation, delta=delta, delta_unit=delta_unit, all_pairs=True)
            rpe_metric.process_data(data)
            rpe_t_stats = rpe_metric.get_all_statistics()["rmse"]

        # RPE  deg/s
            pose_relation = metrics.PoseRelation.rotation_angle_deg
            delta = 10
            delta_unit = Unit.frames  # Since Kinect is 30 fps, then delta = 30, means error per second.

            data = (traj_ref, traj_est)
            rpe_metric = metrics.RPE(pose_relation=pose_relation, delta=delta, delta_unit=delta_unit, all_pairs=True)
            rpe_metric.process_data(data)
            rpe_r_stats = rpe_metric.get_all_statistics()["rmse"]

            ape_list.append(ape_stats)
            rpe_t_list.append(rpe_t_stats)
            rpe_r_list.append(rpe_r_stats)

            results_data += dataset_name.split("/")[-1] + "\t" + str(ape_stats) + "\t" + str(rpe_t_stats) + "\t" + str(rpe_r_stats) + "\t" + str(fps_result) + "\n"

            #Iteratively update text file:
            with open("results_tartan.txt", 'w') as file:
                file.write(results_data)  # Replace with your new content

    print(np.mean(ape_list), np.mean(rpe_t_list), np.mean(rpe_r_list)) #Print the means for the current dataset.
    print("===================")
    results_data += "================================\n" + str(np.mean(ape_list)) + " "  + str(np.mean(rpe_t_list)) + " " + str(np.mean(rpe_r_list)) + "\n"
    with open("results_tartan.txt", 'w') as file:
        file.write(results_data)  # Replace with your new content

print(results_data)


