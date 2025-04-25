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
#  pretty tune widget
#  delay element
#  noise element
#  plot widget
#  fullscreen, system window, plot window, settings board