import re
import csv
import numpy as np
import random
import os
from pydub import AudioSegment

def write_to_csv(data, output_folder):
    print('Generating CSV Files.')
    random.shuffle(data)
    csv_header = ['wav_filename','wav_filesize','transcript']
    train, dev, test = np.split(data, [int(len(data)*0.8), int(len(data)*0.9)])
    train_file_path = os.path.join(output_folder, 'train.csv')
    dev_file_path = os.path.join(output_folder, 'dev.csv')
    test_file_path = os.path.join(output_folder, 'test.csv')
    validated_file_path = os.path.join(output_folder, 'validated.csv')
    with open(train_file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter = ',')
        csvwriter.writerow(csv_header)
        for line in train:
            csvwriter.writerow(line)
    with open(dev_file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter = ',')
        csvwriter.writerow(csv_header)
        for line in dev:
            csvwriter.writerow(line)
    with open(test_file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter = ',')
        csvwriter.writerow(csv_header)
        for line in test:
            csvwriter.writerow(line)
    with open(validated_file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter = ',')
        csvwriter.writerow(csv_header)
        for line in data:
            csvwriter.writerow(line)
    print('Total Files: %d, Train Files: %d, Dev Files: %d, Test Files: %d.' % (len(data), len(train), len(dev), len(test)))
    return validated_file_path

# Common Voice Audio Configurations
# 16000 Hz Sample Rate
# Mono Channel
# 16 bit 64 kbps Bit Rate
def mp3_to_wav(file):
    new_file = file[0:-4] + '.wav'
    song = AudioSegment.from_mp3(file)
    song.export(new_file, format='wav', bitrate='64k', parameters=['-vn', '-ar', '16000', '-ac', '1'])
    os.remove(file)
    return new_file

# Remove Audios That Are Shorter Than 0.5 Seconds And Longer Than 20 Seconds
# Remove Audios That Are Too Short For Transcript
def check_audio(transcript, file):
    temp_file = file
    # Convert File To WAV Because gTTS Stores MP3 File
    temp_file = mp3_to_wav(file)
    size = os.path.getsize(temp_file)
    if ((size / 32000) > 0.5 and (size / 32000) < 20 and transcript != "" and size / len(transcript) > 1400):
        return True, temp_file, size
    else:
        return False, temp_file, size

def load_checkpoint(checkpoint_path):
    checkpoint_text_file = os.path.join(checkpoint_path, 'checkpoint.text')
    checkpoint_row_file = os.path.join(checkpoint_path, 'checkpoint.row')
    checkpoint_meta_file = os.path.join(checkpoint_path, 'checkpoint.meta')
    with open(checkpoint_meta_file, 'r') as f:
        index_line = f.readline().strip()
    counter = int(index_line.split(':')[1])+1
    with open(checkpoint_text_file, 'r') as f:
        lines = f.readlines()
    csv_data = []
    with open(checkpoint_row_file, 'r') as f:
        for line in f:
            csv_data.append(line.strip().split(','))
    return counter, lines, csv_data

def create_checkpoint(checkpoint_path, text, processed_files):
    checkpoint_text_file = os.path.join(checkpoint_path, 'checkpoint.text')
    checkpoint_meta_file = os.path.join(checkpoint_path, 'checkpoint.meta')
    with open(checkpoint_text_file, 'w') as f:
        for line in text:
            f.write('%s\n' % line)
    with open(checkpoint_meta_file, 'w') as f:
        f.write('Last Index: %d\n' % (-1))
        for file in processed_files:
            f.write('File: %s\n' % file)

def save_checkpoint(checkpoint_path, row, index):
    checkpoint_text_file = os.path.join(checkpoint_path, 'checkpoint.text')
    checkpoint_row_file = os.path.join(checkpoint_path, 'checkpoint.row')
    checkpoint_meta_file = os.path.join(checkpoint_path, 'checkpoint.meta')
    data = []
    with open(checkpoint_meta_file, 'r') as f:
        data = f.readlines()
    with open(checkpoint_meta_file, 'w') as f:
        data[0] = ('Last Index: %d\n' % index)
        for item in data:
            f.write('%s\n' % item.strip())
    with open(checkpoint_row_file, 'a') as f:
        for item in row:
            f.write('%s,%s,%s\n' % (item[0], item[1], item[2]))

def generate_alphabet(csv_file_path, output_file_path):
    output_file = os.path.join(output_file_path, 'alphabet.txt')
    all_text = set()
    with open(csv_file_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        # Skip The File Header
        next(reader, None)
        for row in reader:
            all_text |= set(row[2])
    header_text = ['# Each line in this file represents the Unicode codepoint (UTF-8 encoded)\n', '# associated with a numeric label.\n', '# A line that starts with # is a comment. You can escape it with \# if you wish\n', '# to use \'#\' as a label.\n']
    footer_text = ['# The last (non-comment) line needs to end with a newline.\n']
    with open(output_file, "w") as alphabet_file:
        alphabet_file.writelines(header_text)
        for char in list(all_text):
            alphabet_file.write(char + '\n')
        alphabet_file.writelines(footer_text)
    print('Alphabet Path: %s.' %output_file)
