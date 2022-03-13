"""
Purpose of this file is to be the runnable version of the manual labeler.

Note: this replaces the legacy 'tkint-test' file
"""

from DatasetManager import DatasetManager
from ImageDispenser import ImageDispenser
from ManualLabeler import ManualLabeler
from enums import *

if __name__ == "__main__":
    dm = DatasetManager(TEST_DB_NAME)
    id = ImageDispenser(GENERAL_INPUT_PATH)
    ml = ManualLabeler(id, dm)