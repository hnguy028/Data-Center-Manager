##
#   main.py
##

from application import *
import sys

if __name__ == "__main__":
    print("Initializing DC Manager")
    app = DCApplication()

    sys.exit(app.exec())
