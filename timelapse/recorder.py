import os
import subprocess  # Taking screenshot
import datetime  # Filename
from multiprocessing import Process, Event
from PyObjCTools import AppHelper
from AppKit import NSEvent, NSScreen, NSMouseInRect

def get_screen_with_mouse_index():
    mouseLocation = NSEvent.mouseLocation()
    screens = NSScreen.screens()
    for i, screen in enumerate(screens):
        if NSMouseInRect(mouseLocation, screen.frame(), False):
            return i
    return 0

class Recorder(Process):
    """
    Takes a screenshot every 'interval' seconds and saves it into output_dir or a subdirectory thereof.
    """

    def __init__(self, output_dir, interval=4):
        # Initialize the thread
        Process.__init__(self)

        # Provide a way to stop the recorder
        self._stop = Event()
        self._stopped = Event()

        # Set config options
        self.output_dir = output_dir
        self.interval = interval
        self.format = "png"

        # Number of screenshots taken
        self.screenshot_counter = 0
        print("Recorder started")

    def join(self, timeout=None):
        """ Stop recording """
        self._stop.set()
        self._stopped.wait()
        print("Recorder stopped. Total recording time: " + self.get_recording_time() + ".")
        Process.join(self, timeout=timeout)

    def run(self):
        """ Periodically take a screenshots of the screen """
        while not self._stop.is_set():
            self.screenshot()
            self._stop.wait(self.interval)

        self._stopped.set()

    def get_recording_time(self):
        return str(self.screenshot_counter * self.interval) + " seconds"

    def get_filename(self):
        """ Call screencapture for mac screenshot """
        # The id is the unique part of the filename.
        id = str(datetime.datetime.now())
        # Format the id a bit (remove whitspace and special characters)
        id = id.replace(' ', '').replace(':', '').replace('.', '')
        filename = os.path.join(self.output_dir, id) + "." + self.format
        return filename

    def screenshot(self):
        """ This method uses Mac OSX screencapture from the commandline """
        filename = self.get_filename()
        print("Taking screenshot [" + filename + "]")
        subprocess.run(
            ['screencapture', '-S', '-o', '-x', '-D', str(get_screen_with_mouse_index() + 1), '-t', self.format, filename],
            check=True)
        self.screenshot_counter += 1
