import pyttsx3

"""语言播放Hello World"""
engine = pyttsx3.init()
engine.say("接下来会出现几个点，请依次注视它们")
engine.runAndWait()