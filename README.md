# CARESSES applications for Nao and Pepper
This repository contains the CARESSES applications, available for the SoftBank robots Pepper and Nao.
Open the CARESSES_App application folder in Choregraphe, deploy it on the robot and launch it using one of the following trigger sentences:
```
"Let's talk" or "Connect to the Cloud"
```

Once started, the application allows interacting with the CARESSES Cloud. 

To stop the application say:
```
"Stop talking"
```

All the other applications are integrated with the main one and allow the robots to perform extra actions during the conversation.

## WordTools
This application contains three behaviours:
* *Wikisearch*: it looks for something on Wikipedia
* *Translator*: it translates a word or a sentence from English to one of the following languages: Arabic, Brazilian, Chinese, Czech, Danish, Dutch, English,
Finnish, French, German, Greek, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish, Swedish, Turkish*.
* *Dictionary*: it searches for the definition of a word in the dictionary.
*_Note: the destination language must be installed on the robot._

## Movement
This application contains four behaviours:
* *Go*: it makes the robot move in the asked direction and stops it when the head sensor is touched
* *Move*: it makes the robot perform a small movement in the asked direction (forward, back, left, right)
* *Set position*: it allows the robot to learn its position in the map of the house
* *Move to*: it makes the robot move to the desired place in the map. Note: it is necessary to set its position at least once before asking it to move somewhere.
* *Learn place*: it allows the robot to store the current position in the map. Note: it is necessary to set its position at least once before asking it to learn the position of a new place.

## Weather
This application contains one behaviour:
* *Weather*: it exploits OpenWeatherMap to allow the user to ask for the weather forecast of the desired city.

## MusicPlayer
This application contains one behaviour:
* *Playmusic*: it allows the robot to play the song requested by the user from YouTube.
