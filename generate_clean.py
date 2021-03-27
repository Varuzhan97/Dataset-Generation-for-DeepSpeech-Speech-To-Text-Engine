import os
import sys
import time
import utils
from gtts import gTTS
from datetime import datetime

def g_tts(transcript, language, output_folder, index, generate_male):
    tts = gTTS(text=transcript, lang=language)
    tts_slow = gTTS(text=transcript, lang=language, slow=True)
    file = os.path.join(output_folder, 'gTTS-' + language + '-' + str(index) + '.mp3')
    file_slow = os.path.join(output_folder, 'gTTS-' + language + '-' + str(index) + '-slow.mp3')
    tts.save(file)
    tts_slow.save(file_slow)
    # If the index is even then generate male voice
    # In this case 50% of dataset will be male voice, 50% female voice
    if (generate_male) and ((index % 2) == 0):
        male_file = os.path.join(output_folder, 'temp.mp3')
        wait = os.system('ffmpeg -i ' + file + ' -af asetrate=24000*0.75,aresample=24000,atempo=0.75/1 ' + male_file)
        os.remove(file)
        os.rename(male_file, file)
        male_file_slow = os.path.join(output_folder, 'temp_slow.mp3')
        wait = os.system('ffmpeg -i ' + file_slow + ' -af asetrate=24000*0.75,aresample=24000,atempo=0.75/1 ' + male_file_slow)
        os.remove(file_slow)
        os.rename(male_file_slow, file_slow)
    return file, file_slow

def generate_clean_db(language, batch_size, sleep_time, parameters):
    lines = []
    csv_data = []
    clips_output_path = ''
    index = 0
    if parameters.checkpoint_path is not None:
        if not os.path.isdir(parameters.checkpoint_path):
            print ('Checkpoint Path Not Exist.')
            sys.exit()
        print('Loading Checkpoint.')
        clips_output_path = os.path.join(parameters.checkpoint_path, 'clips')
        index, lines, csv_data = utils.load_checkpoint(parameters.checkpoint_path)
    else:
        if (not os.path.isdir(parameters.input_path)) and (not os.path.isfile(parameters.input_path)):
            print ('Input Text File/Folder Not Exist.')
            sys.exit()
        if not os.path.isdir(parameters.output_path):
            print ('Output Path Not Exist.')
            sys.exit()
        now = datetime.now().strftime('%Y-%m-%d*%H-%M-%S')
        clips_output_path = os.path.join(parameters.output_path, 'corpus-' + now, 'clips')
        os.makedirs(clips_output_path)
        all_files = []
        if os.path.isdir(parameters.input_path):
            print('Input Is A Directory.')
            for file in os.listdir(parameters.input_path):
                if file.endswith(".txt"):
                    all_files.append(os.path.join(parameters.input_path, file))
        elif os.path.isfile(parameters.input_path):
            print('Input Is A Text File.')
            all_files.append(parameters.input_path)
        for file in all_files:
            current_file = open(file, 'r')
            for line in current_file:
                lines.append(line.strip())
        utils.create_checkpoint(os.path.split(clips_output_path)[0], lines, all_files)
    print('Converting Text To Speech And Generating Dataset.')
    print('Dataset Path: %s.' % os.path.split(clips_output_path)[0])
    for line in lines[index:]:
        pair = []
        current_file, current_file_slow = g_tts(line, language, clips_output_path, index, parameters.generate_male)
        current_file_size = os.path.getsize(current_file)
        current_file_size_slow = os.path.getsize(current_file_slow)
        print('Processing Item: %d/%d, Type: Normal.' % (index+1, len(lines)))
        is_valid, file, size = utils.check_audio(line, current_file,)
        if is_valid == True:
            csv_data.append([os.path.basename(file), str(size), line.strip().lower()])
            pair.append(csv_data[-1])
        else:
            print('Duration Of %s File Is Not Valid (Must Be Between 5-20 Seconds.)' % os.path.basename(current_file))
            os.remove(file)
        print('Processing Item: %d/%d, Type: Slow.' % (index+1, len(lines)))
        is_valid, file, size = utils.check_audio(line, current_file_slow)
        if is_valid == True:
            csv_data.append([os.path.basename(file), str(size), line.strip().lower()])
            pair.append(csv_data[-1])
        else:
            print('Duration Of %s File Is Not Valid (Must Be Between 0.5-20 Seconds.)' % os.path.basename(current_file_slow))
            os.remove(file)
        utils.save_checkpoint(os.path.split(clips_output_path)[0], pair, index)
        index += 1
        if index%batch_size==0:
            print('Sleep (%d Seconds).' % sleep_time)
            time.sleep(sleep_time)
    return csv_data, clips_output_path
