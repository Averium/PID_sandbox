from pygame import init, quit

from source.framework import Framework

from ctypes import windll

errorCode = windll.shcore.SetProcessDpiAwareness(2)



if __name__ == "__main__":
    init()

    framework = Framework()
    framework.start()

    quit()


# TODO:
#  plot widget text and ticks
#  switch widget
#  anti-windup and derivative filter switches