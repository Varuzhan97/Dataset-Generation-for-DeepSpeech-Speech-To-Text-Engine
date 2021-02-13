import os
import math
import librosa
import numpy as np
from scipy.io.wavfile import write

def get_white_noise(signal, snr) :
    rms_s = math.sqrt(np.mean(signal**2))
    rms_n = math.sqrt(rms_s**2/(pow(10, snr/10)))
    std_n = rms_n
    noise = np.random.normal(0, std_n, signal.shape[0])
    return noise

def get_noise_from_sound(signal, noise, snr):
    rms_s = math.sqrt(np.mean(signal**2))
    rms_n = math.sqrt(rms_s**2/(pow(10, snr/10)))
    rms_n_current = math.sqrt(np.mean(noise**2))
    noise = noise*(rms_n/rms_n_current)
    return noise

def to_polar(complex_ar):
    return np.abs(complex_ar),np.angle(complex_ar)

def generate_noisy_db(csv_data, snr, output_path):
    noisy_wav_path = os.path.join(os.getcwd(), 'Noise Types')
    noisy_wav_files = []
    for file in os.listdir(noisy_wav_path):
        if file.endswith(".wav"):
            noisy_wav_files.append(os.path.join(noisy_wav_path, file))
    awgn_output_folder = os.path.join(os.path.split(output_path)[0], 'clips-awgn-' + str(snr) + '-dB-Noisy')
    os.makedirs(awgn_output_folder)
    rwn_output_folder = os.path.join(os.path.split(output_path)[0], 'clips-rwn' + str(snr) + '-dB-Noisy')
    os.makedirs(rwn_output_folder)
    awgn_csv_data = []
    rwn_csv_data = []
    index = 0
    print('Generating Additive White Gaussian Noise (AWGN) Dataset.')
    print('Additive White Gaussian Noisy (AWGN) Dataset Path: %s.' % awgn_output_folder)
    for wav_name in csv_data:
        wav_path = os.path.join(output_path, wav_name[0])
        print('Processing Item: %d/%d, Type: Additive White Gaussian Noise (AWGN).' % (index+1, len(csv_data)))
        signal, sr = librosa.load(wav_path)
        signal=np.interp(signal, (signal.min(), signal.max()), (-2147483648, 2147483647))
        noise=get_white_noise(signal,snr)
        X=np.fft.rfft(noise)
        radius,angle=to_polar(X)
        signal_noise=signal+noise
        output_file_path = os.path.join(awgn_output_folder, os.path.basename(wav_path)[:-4] + '-AWGN-' + str(snr) + '-dB-Noisy-' + str(index) + '.wav')
        write(output_file_path,16000,signal_noise.astype(np.int32))
        file_size = os.path.getsize(output_file_path)
        awgn_csv_data.append([os.path.basename(output_file_path), str(file_size), wav_name[2]])
        index+=1
    index = 0
    print('Generating Real World Noisy (RWN) Dataset.')
    print('Real World Noisy (RWN) Dataset Path: %s.' % rwn_output_folder)
    for wav_name in csv_data:
        wav_path = os.path.join(output_path, wav_name[0])
        for noisy_wav in noisy_wav_files:
            print('Processing Item: %d/%d, Type: %s.' % ((index/len(noisy_wav_files))+1, len(csv_data), os.path.basename(noisy_wav[:-4])))
            signal, sr = librosa.load(wav_path)
            signal=np.interp(signal, (signal.min(), signal.max()), (-2147483648, 2147483647))
            noise, sr = librosa.load(noisy_wav)
            noise=np.interp(noise, (noise.min(), noise.max()), (-2147483648, 2147483647))
            if(len(noise)>len(signal)):
                noise=noise[0:len(signal)]
            noise=get_noise_from_sound(signal,noise,snr)
            signal_noise=signal+noise
            output_file_path = os.path.join(rwn_output_folder, os.path.basename(wav_path)[:-4] + '-RWN-' + os.path.basename(noisy_wav[:-4]) + '-' + str(snr) + '-dB-Noisy-' + str(index) + '.wav')
            write(output_file_path,16000,signal_noise.astype(np.int32))
            file_size = os.path.getsize(output_file_path)
            rwn_csv_data.append([os.path.basename(output_file_path), str(file_size), wav_name[2]])
            index+=1
    return awgn_csv_data, awgn_output_folder, rwn_csv_data, rwn_output_folder
