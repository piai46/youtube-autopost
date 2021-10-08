# Youtube auto post

## How to use:
1 - Install Python and Firefox

2 - Open CMD inside the folder that contain main.py and insert the following command: ```pip install -r requirements.txt```

3 - Open Firefox and login with account of the youtube channel

4 - Copy ```geckodriver.exe``` and paste where ```firefox.exe``` is

5 - Go to ```C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles``` and copy the path to your profile, like: 
```C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\sm1g0yf3.default-1631840458096A``` Open main.py, change the value of ```MOZILLA_PROFILE_PATH``` and replace ```\``` to ```\\```

6 - Add the channel to download the videos in ```CHANNEL```

7 - Change the value of ```AMOUNT_VIDEO``` to the last X videos that will be download

8 - Change the value of ```TIME_BETWEEN_POSTS``` to the time beetween the videos posts (in seconds)