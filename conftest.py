"""রুট ডিরেক্টরি sys.path-এ যোগ করে — `pytest` ও `python -m pytest` দুভাবেই যেন চলে।
(CI-তে ধরা পড়া বাগ: bare `pytest` cwd যোগ করে না → ModuleNotFoundError: src)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
