import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient

ChannelFactoryInitialize(0) #, 'eth0'

audio_client= AudioClient()
audio_client.SetTimeout(10.0)
audio_client.Init()
audio_client.SetVolume(100)

def speak(text):
    audio_client.TtsMaker(text,1) # 1 meansEnglish
    time.sleep(1)
    audio_client.LedControl(255,0,0)
    time.sleep(1)
    audio_client.LedControl(0,255,0)
    time.sleep(1)
    audio_client.LedControl(0,0,255)
    
if __name__ == '__main__':
    speak("I am a robot")