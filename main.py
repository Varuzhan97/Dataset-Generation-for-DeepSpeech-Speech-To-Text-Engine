import os
import yaml
import time
import utils
import argparse
import generate_clean
import generate_noise

def parse_args():
    parser = argparse.ArgumentParser(description='Arguments and Their Descriptions.')
    parser.add_argument('--checkpoint_path', default = None,
                        help='An Argument For The Continuing Of A Broken Process. Must Be The Absolute Path Of The Folder That Contains Checkpoint Files.')
    parser.add_argument('--input_path', default = None,
                        help='An Argument For Absolute Path Of Input Text File Or Folder.')
    parser.add_argument('--output_path', default = None,
                        help='An Argument For Absolute Path Of Output.')
    parser.add_argument('--generate_noisy', default = True,
                        help='An Argument For Generating Noisy Dataset (Additive White Gaussian Noise (AWGN) and Real World Noise (RWN)).')
    parser.add_argument('--generate_male', default = False,
                        help='An Argument For The Continuing Of A Broken Process. Must Be The Absolute Path Of The Folder That Contains Checkpoint Files.')
    args = parser.parse_args()
    if args.checkpoint_path is not None:
        if((args.input_path is not None) or (args.output_path is not None)):
            print('Please Specify Either --input_path, --output_path  Or --checkpoint_path Arguments.')
            sys.exit()
    elif (args.input_path is None) or (args.output_path is None):
            print('Please Specify --input_path/--output_path Arguments.')
            sys.exit()
    return args

if __name__ == "__main__":
    params = parse_args()
    config_file = os.path.join(os.getcwd(), 'config.yaml')
    with open(config_file, 'r') as file:
        main_configs = yaml.full_load(file)
        config_language_name = main_configs['Language']
        config_batch_size = main_configs['Batch Size']
        config_sleep_time = main_configs['Sleep Time']
        config_snr = main_configs['SNR']
    start_time = time.time()
    csv_data, clips_folder = generate_clean.generate_clean_db(config_language_name, config_batch_size, config_sleep_time, params)
    print('Generating CSV Files For Clean Dataset.')
    validated_csv_path = utils.write_to_csv(csv_data, clips_folder)
    if params.generate_noisy:
        awgn_csv_data, awgn_clips_folder, rwn_csv_data, rwn_clips_folder = generate_noise.generate_noisy_db(csv_data, config_snr, clips_folder)
        print('Generating CSV Files For Dataset With Additive White Gaussian Noise.')
        utils.write_to_csv(awgn_csv_data, awgn_clips_folder)
        print('Generating CSV Files For Dataset With Real-World Noises.')
        utils.write_to_csv(rwn_csv_data, rwn_clips_folder)
    print('Generating Alphabet For Dataset(s).')
    utils.generate_alphabet(validated_csv_path, os.path.split(clips_folder)[0])
    process_sec = round(time.time() - start_time)
    (process_min, process_sec) = divmod(process_sec,60)
    (process_hour, process_min) = divmod(process_min,60)
    print('Process Took: %dH:%dM:%dS, Language: %s.' % (process_hour, process_min, process_sec, config_language_name))
