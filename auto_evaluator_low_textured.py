'''
Will open config file, run, extract results and then perform the next iteration, Just specify data here.
'''
from evo.core import metrics
from evo.core.metrics import Unit
from evo.tools import file_interface
from evo.core import sync
import copy
import pprint
import os
import time
import matplotlib.pyplot as plt
import matplotlib
from ruamel.yaml import YAML
import subprocess
import os
import shutil
import time
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
        if key == "InputDatasetFolder":
            value['datadir'] = path
    return data



path_to_config = "config.yaml"
results_folder = "/home/dylanbrown/Desktop/results_folder"

distortion_coefficients = [[0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0], ]

depth_scale = [1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               1000,
               ]

dataset_array = ["/media/sf_Datasets/LowTextured/extreme_geometry/lines_01",
                "/media/sf_Datasets/LowTextured/extreme_geometry/circle_01",
                "/media/sf_Datasets/LowTextured/extreme_geometry/dodecagon_01",
                "/media/sf_Datasets/LowTextured/extreme_geometry/hexagon_01",
                "/media/sf_Datasets/LowTextured/extreme_geometry/square_01",
                "/media/sf_Datasets/LowTextured/extreme_geometry/triangle_01",
                "/media/sf_Datasets/LowTextured/extreme_geometry/triangle_02",
                "/media/sf_Datasets/LowTextured/extreme_geometry/triangle_03",
                "/media/sf_Datasets/LowTextured/loop/circle_dodecagon_01",
                "/media/sf_Datasets/LowTextured/loop/circle_hexagon_01",
                "/media/sf_Datasets/LowTextured/loop/circle_squares_01",
                "/media/sf_Datasets/LowTextured/sand/sand_rocks_01",
                "/media/sf_Datasets/LowTextured/sand/sand_rocks_02",
                "/media/sf_Datasets/LowTextured/sand/sand_rocks_03"]


#cx, cy, fx, fy for each dataset in same order as array:
camera_parameters = [[650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                     [650.889, 364.693, 908.479, 907.842],
                 
runfile_arr = ["TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml",
                 "TUM_4.yaml"
                 ]

canny_values = [[50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [50, 100],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [20, 30],
                [50, 100],
                [20, 30],
                [20, 30],
                ]

#cx, cy, fx, fy for each dataset in same order as array:
camera_parameters = [[318.6, 255.3, 517.3, 516.5],
                     [318.6, 255.3, 517.3, 516.5],
                     [318.6, 255.3, 517.3, 516.5],
                     [318.6, 255.3, 517.3, 516.5],
                     [318.6, 255.3, 517.3, 516.5],
                     [318.6, 255.3, 517.3, 516.5],
                     [318.6, 255.3, 517.3, 516.5],
                     [318.6, 255.3, 517.3, 516.5],
                     [318.6, 255.3, 517.3, 516.5],
                     [325.1, 249.7, 520.9, 521.0],
                     [325.1, 249.7, 520.9, 521.0],
                     [325.1, 249.7, 520.9, 521.0],
                     [325.1, 249.7, 520.9, 521.0],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [320.1, 247.6, 535.4, 539.2],
                     [319.5, 239.5, 481.2, 480.0],
                     [319.5, 239.5, 481.2, 480.0],
                     [319.5, 239.5, 481.2, 480.0],
                     [319.5, 239.5, 481.2, 480.0],
                     [359.2048034668, 202.47247314453, 726.21081542969, 726.21081542969],
                     [359.2048034668, 202.47247314453, 726.21081542969, 726.21081542969],
                     [356.69226074219, 186.45402526855, 726.30139160156, 726.30139160156],
                     ]

print(len(dataset_array), len(canny_values), len(camera_parameters))

results_data = "Dataset name: \t ATE (m) \t RPE_t (m) \t RPE_R (deg) \t Frame Rate (fps)\n"


#Load data:
number_of_iterations = 0
sum_ate = 0
sum_rpe_t = 0
sum_rpe_r = 0
sum_fps = 0

for i in range(29, len(dataset_array)): #-1, -1, -1):
    #Increment:
    number_of_iterations += 1

    #Dataset name:
    dataset_name = dataset_array[i]

    #Results path:
    results_name = "/home/reslam/Desktop/poses.txt"
    
    config_path = "/home/reslam/Documents/RESLAM-master/config_files/" + runfile_arr[i]
    
    with open(config_path, 'r') as file: 
        lines = file.readlines()[1:]
    with open(config_path, 'w') as file: 
        file.writelines(lines)

    with open(config_path, 'r') as file:
        yaml_content = yaml.load(file)
    
    #cx = camera_parameters[i][0]
    #cy = camera_parameters[i][1]
    #fx = camera_parameters[i][2]
    #fy = camera_parameters[i][3]
    #yaml_content["IntrinsicsCamFx"] = fx
    #yaml_content["IntrinsicsCamFy"] = fy
    #yaml_content["IntrinsicsCamCx"] = cx
    #yaml_content["IntrinsicsCamCy"] = cy
    yaml_content["InputDatasetFolder"] = dataset_name



    with open(config_path, 'w') as file:
        yaml.dump(yaml_content, file)


    with open(config_path, 'r') as file: 
        lines = file.readlines()
    lines.insert(0,"%YAML:1.0\n")
    with open(config_path, 'w') as file: 
        file.writelines(lines)
    
    t = time.time()
    result = subprocess.Popen(['sudo', '/home/reslam/Documents/RESLAM-master/build/RESLAM', '/home/reslam/Documents/RESLAM-master/config_files/reslam_settings.yaml', config_path])

    print('sudo', '/home/reslam/Documents/RESLAM-master/build/RESLAM', '/home/reslam/Documents/RESLAM-master/config_files/reslam_settings.yaml', config_path)
    last_modified = os.path.getmtime(results_name)
    counter = 0

    while ((counter < 180) and (last_modified == os.path.getmtime(results_name))):
        time.sleep(1)
        counter += 1
    result.kill()

    #EXtract the stored frame per second rate:
    with open(results_name, 'r') as file:
        run_time = time.time() - t
        # Read the first line
        first_line = file.readline()

        # Find the position of the 'FPS:' string
        fps_pos = first_line.find('FPS:')

        # Extract everything from 'FPS:' onward
	fps_result = len(file.readlines())/run_time

    #Score:
    if counter < 600:
        ref_file = dataset_name + "/groundtruth.txt"
        est_file = results_name

        dst_folder = "results"
        dst_file = dst_folder + "/" + str(dataset_array[i].split("/")[-1]) + ".txt"
        os.makedirs(dst_folder, exist_ok=True)
        shutil.copy(est_file, dst_file)
        
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
        delta = 30
        delta_unit = Unit.frames  # Since Kinect is 30 fps, then delta = 30, means error per second.
        
        data = (traj_ref, traj_est)
        rpe_metric = metrics.RPE(pose_relation=pose_relation, delta=delta, delta_unit=delta_unit, all_pairs=True)
        rpe_metric.process_data(data)
        rpe_t_stats = rpe_metric.get_all_statistics()["rmse"]
        
        # RPE  deg/s
        pose_relation = metrics.PoseRelation.rotation_angle_deg
        delta = 30
        delta_unit = Unit.frames  # Since Kinect is 30 fps, then delta = 30, means error per second.
        
        data = (traj_ref, traj_est)
        rpe_metric = metrics.RPE(pose_relation=pose_relation, delta=delta, delta_unit=delta_unit, all_pairs=True)
        rpe_metric.process_data(data)
        rpe_r_stats = rpe_metric.get_all_statistics()["rmse"]
        
        results_data += dataset_name.split("/")[-1] + "\t" + str(ape_stats) + "\t" + str(rpe_t_stats) + "\t" + str(rpe_r_stats) + "\t" + str(fps_result) + "\n"

        #Add to sum for mean calculation later:
        sum_ate += ape_stats
        sum_rpe_t += rpe_t_stats
        sum_rpe_r += rpe_r_stats
    else:
        results_data += "FAIL\n"

    #Iteratively update text file:
    with open("results_low_textured.txt", 'w') as file:
        file.write(results_data)  # Replace with your new content

results_data += "\n"
results_data += "==================================== Means ====================================\n"
results_data += "\t" + str(sum_ate/number_of_iterations) + "\t" + str(sum_rpe_t/number_of_iterations) + "\t" + str(sum_rpe_r/number_of_iterations) + "\n"
with open("results_low_textured.txt", 'w') as file:
    file.write(results_data)  # Replace with your new content
print(results_data)


