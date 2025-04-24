from source.framework import Framework
from pygame import init, quit


if __name__ == "__main__":
    init()

    framework = Framework()
    framework.start()

    quit()