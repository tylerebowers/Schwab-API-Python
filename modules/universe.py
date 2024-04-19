"""
This file stores variables to be used between python files and functions some
Github: https://github.com/tylerebowers/Schwab-API-Python
"""


class credentials:
    # Schwab account credentials
    appKey = "Your App Key"
    appSecret = "Your App Secret"
    callbackUrl = "https://127.0.0.1"
    accountNumber = ""
    encryptedId = ""


"""
Below here are variables for functionality of the program; they shouldn't be changed
"""


class cTerm:
    @staticmethod
    def info(string): print(f"\033[92m{'[INFO]: '}\033[00m{string}")
    @staticmethod
    def warning(string): print(f"\033[93m{'[WARN]: '}\033[00m{string}")
    @staticmethod
    def error(string): print(f"\033[91m{'[ERROR]: '}\033[00m{string}")
    @staticmethod
    def input(string): return input(f"\033[94m{'[INPUT]: '}\033[00m{string}")
    @staticmethod
    def user(string): print(f"\033[1;31m{'[USER]: '}\033[00m{string}")


from time import sleep
import tkinter as tk
from tkinter import ttk
import threading


class terminal(threading.Thread):

    def __init__(self, title="Terminal", height=20, width=200, font=("Courier New", "12"), backgroundColor="gray5", textColor="snow", allowClosing=True, ignoreClosedPrints=True):
        #params
        self.title = title
        self.height = height
        self.width = width
        self.font = font
        self.backgroundColor = backgroundColor
        self.textColor = textColor
        self.allowClosing = allowClosing
        self.ignoreClosedPrints = ignoreClosedPrints
        #internal variables
        self._root = None  # main window
        self._tb = None  # text box
        self.isOpen = False  # if the window is open
        self._safeExit = False  # if the window is safe to exit
        threading.Thread.__init__(self, daemon=True)  # kill child thread on main thread exit
        self.start()
        sleep(0.5)  # wait for window to open

    def close(self):
        if self.isOpen and self._safeExit:  # safeExit is True is no operations are being done (i.e. print)
            self.isOpen = False
            self._root.quit()
            self._root.update()
            self._root = None

    def run(self):
        self._root = tk.Tk()
        if self.allowClosing: self._root.protocol("WM_DELETE_WINDOW", self.close)
        else: self._root.protocol("WM_DELETE_WINDOW", lambda: None)
        self._root.title(self.title)
        self._tb = tk.Text(self._root, height=self.height, width=self.width, wrap="none", font=self.font)
        self._tb.pack(side="left", fill="both", expand=True)
        self._tb.configure(state="disabled", bg=self.backgroundColor, fg=self.textColor)
        sizegrip = ttk.Sizegrip(self._tb)
        sizegrip.configure(cursor="sizing")
        sizegrip.bind("<1>", self._resize_start)
        sizegrip.bind("<B1-Motion>", self._resize_update)
        self.isOpen = True
        self._safeExit = True
        self._root.mainloop()

    def print(self, toPrint, end="\n"):
        if self._root is None or not self.isOpen:
            if not self.ignoreClosedPrints: return print(f"Terminal \"{self.title}\" is closed")
            #if not self.ignoreClosedPrints: raise Exception(f"Terminal \"{self.title}\" is closed")
        else:
            self._safeExit = False  # needed so that we don't kill mainloop while printing
            self._tb.configure(state="normal")
            self._tb.see("end")
            self._tb.insert("end", f"{toPrint}{end}")
            self._tb.configure(state="disabled")
            self._safeExit = True

    def _resize_start(self, event):
        self._x = event.x
        self._y = event.y

    def _resize_update(self, event):
        delta_x = event.x - self._x
        delta_y = event.y - self._y
        self._tb.place_configure(width=self._tb.winfo_width() + delta_x, height=self._tb.winfo_height() + delta_y)

