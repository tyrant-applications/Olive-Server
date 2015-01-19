import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.join(os.path.dirname( __file__ ), '..')


print os.path.abspath(BASE_DIR)
print os.path.abspath(PROJECT_PATH)
