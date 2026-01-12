import sys
import os

print("=== DEBUG START ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

print("\n=== Checking imports ===")
try:
    import aiogram
    print(f"✓ aiogram imported, version: {aiogram.__version__}")
except Exception as e:
    print(f"✗ Error importing aiogram: {e}")

print("\n=== Checking environment variables ===")
bot_token = os.getenv('BOT_TOKEN')
print(f"BOT_TOKEN exists: {'Yes' if bot_token else 'No'}")

print("=== DEBUG END ===")
