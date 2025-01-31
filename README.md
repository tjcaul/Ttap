# TTAP

*Text To Audio Processor*

## Why?

Many foreign films have English subtitles but no English audio. Subtitles aren't a viable or enjoyable option for many people.
TTAP makes formerly inaccessible media accessible for people with reading/vision impairments, when audio is unclear or there is no dubbing, or for people who just like their subtitles read out.

## What?

TTAP is a client-side live automated dubbing program. 
It uses Google's Tesseract OCR system to read subtitles off the screen, making it flexible for use on any streaming platform.
The text is then quickly read aloud by the Unreal Speech API in a configurable voice.
A minimal frontend written in customTkinter allows you to tell the program where the subtitles are and change the voice settings. Then it gets out of your way to let you enjoy the movie.

## How?

**Installation**
```commandline
$ mkdir venv
$ python3 -m venv venv
$ cd venv
$ git clone https://github.com/tjcaul/ttap
$ source bin/activate
$ cd ttap
$ cat other-requirements.txt
. . .
```
Then use your system's package manager to install the listed packages.
```commandline
$ pip3 install -r requirements.txt
$ cp .env-template .env
$ vim .env
```
Add your Unreal Speech API key to the file.

**Running**
```commandline
$ cd venv/ttap
$ source ../bin/activate
$ python3 main.py
```

## Who?

TTAP was written by Ray Chen, Tyson Caul, and Sark Asadourian for the UofTHacks 2025 hackathon.

We were originally going to do a completely different project involving security. When the tech we were going to use proved to be unviable in a short timeframe, we pivoted halfway through the project.
