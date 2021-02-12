# Clean And Noisy Datasets Generation Tool for DeepSpeech STT Engine Based on Google Translate's API
The tool can generate both clean and noisy(additive white Gaussian noise(AWGN) and real-world noise(RWN)) datasets for DeepSpeech speech-to-text engine using Google Translate's text-to-speech API feature that can convert text to normal and slow speech. 
[DeepSpeech](https://github.com/mozilla/DeepSpeech) is a speech-to-text engine based on [Baidu's Deep Speech research paper](https://arxiv.org/abs/1412.5567). Project DeepSpeech uses datasets provided by Mozilla's other project calling Common Voice.

Audio clips specifications: 
  * Audio file format is .wav.
  * Channels number is 1(mono). 
  * Sampling rate is 16000 Hz.

config.yaml contains language, batch size, sleep time and signal to noise ratio(SNR) configurations. Set sleep time to avoid [gTTS](https://github.com/pndurette/gTTS)(Google Translate's text-to-speech API) problems(for example, IP address blocking). Batch processing feature is for increasing performance speed. Also, it is a maximum character limit that Google Translate's text-to-speech API takes at a time.
Another important note is that DeepSpeech can only process audios that are longer than 0.5 seconds, shorter than 20 seconds and are not too short for transcript. The tool checks for these too.

The tool  generates 1 clean and 2 noisy datasets(if --generate_noisy input argument is set to True) corresponding to the Common Voice datasets structure.
Generated datasets must be consists of the following components:
  * ~/corpus-^/clips/train.csv, ~/corpus-^/clips/dev.csv, ~/corpus-^/clips/test.csv files.
  * ~/corpus-^/clips/^.wav audio files.
  * ~/corpus-^/alphabet.txt file.
  * ~/corpus-^/checkpoint.meta, ~/corpus-^/checkpoint.row and ~/corpus-^/checkpoimt.text checkpoint files with .txt extension.
  
The .csv files have the following fields:
  * wav_filename - the path of the sample, either absolute or relative. Here, the importer produces relative paths.
  * wav_filesize - samples size given in bytes, used for sorting the data before training. Expects positive integer.
  * transcript - transcription target for the sample.

Each dataset corpus additionally contains validated.csv file. Audio files(clips) that are included in the training, development, and testing sets must be included in validated.csv file too. The clips division ratio is 80-10-10.

Supported Languages are:
  - [x] English(en)
  - [x] Russian(ru)

Adding noise to a neural network during training can improve the robustness of the network, evaluate the performance of machine learning models under these noisy conditions, resulting in better generalization and faster learning. Besides this, it is a common approach to combine clean and noisy data. First, pre-train a network using the large noisy dataset and then fine-tune with the clean dataset.

Additive white Gaussian noise(AWGN) is a basic noise model used in information theory to mimic the effect of many random processes that occur in nature. Additive white Gaussian noise is easier to model for analytical analyzes and it's easier to generate. But it may not represent realistic noise.

Real-world noises can be extracted from the environment. There are many types of real-world noises. For example: arctic wind noise, radio or tv static noise, etc. For adding real-world noise can be used another audio clip which contains real-world noise. It must just be removed from audio clip and add to target clip.

Signal to noise ratio, Additive white Gaussian noise(AWGN) and real-world noise(RWN) equations:

![alt text](https://github.com/Varuzhan97/Dataset-Generation-for-DeepSpeech-Speech-To-Text-Engine/blob/main/Images/SNR1.png)

![alt text](https://github.com/Varuzhan97/Dataset-Generation-for-DeepSpeech-Speech-To-Text-Engine/blob/main/Images/AWGN1.png)

![alt text](https://github.com/Varuzhan97/Dataset-Generation-for-DeepSpeech-Speech-To-Text-Engine/blob/main/Images/AWGN2.png)

![alt text](https://github.com/Varuzhan97/Dataset-Generation-for-DeepSpeech-Speech-To-Text-Engine/blob/main/Images/AWGN3.png)

![alt text](https://github.com/Varuzhan97/Dataset-Generation-for-DeepSpeech-Speech-To-Text-Engine/blob/main/Images/AWGN4.png)

![alt text](https://github.com/Varuzhan97/Dataset-Generation-for-DeepSpeech-Speech-To-Text-Engine/blob/main/Images/RWN1.png)

[To get more information about additive white Gaussian and real-world noises read this article.](https://medium.com/analytics-vidhya/adding-noise-to-audio-clips-5d8cee24ccb8)
### Environment and Requirements

Python version: 3.6.12.

Install the required dependencies using pip3:
> pip3 install -r requirements.txt

> sudo apt install ffmpeg
### Repository Structure:
* /Data

  Contains normalized text files that need to be processed.
  
  Text Normalization rules are:
    * Numbers, dates, acronyms, and abbreviations are non-standard "words" that need to be pronounced differently depending on the context. For example, "$200"           would be pronounced as "two hundred dollars" in English. 
    * The text need to be normalized by removing non-alphanumeric characters, diacritical marks and regular expressions.
    * The text need to be normalized by converting multiple whitespace characters to a single whitespace character.
    * The text need to be normalized by removing punctuation marks except apostrophe(').
    * The text need to be normalized by containing one sentence in each line.
    
    The system will automatically convert upper case to lower case before processing.
* /Noise Types

  Contains .wav audio files with real-world noises. Real-world noises must just be extracted from an audio clip and add to each audio clip of the database.
### Run
Input arguments are:
  * --checkpoint_path - an argument for the continuing of a broken process. Must be the absolute path of the folder that contains checkpoint files.
  * --input_path - an argument for absolute path of input text file or folder.
  * --output_path - an argument for absolute path of output.
  * --generate_noisy - an argument for generating noisy dataset(additive white Gaussian noise(AWGN) and real-world noise(RWN)).
* /Images

  Contains signal to noise ratio, additive white Gaussian noise(AWGN) and real-world noise(RWN) equations images.
  
First time run example:
> python3 main.py --input_path /path/to/file/or/folder --output_path /path/to/output/folder

Broken process continue example:
> python3 main.py --checkpoint_path path/to/file/or/folder/that/contains/checkpoint/files
