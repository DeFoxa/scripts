import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

TARGET_1="/mnt/code/dev/scripts/sh/test"
TARGET_2="/mnt/code/dev/scripts/sh/test_2"

def sync_directories(source, destination):
    subprocess.run(["rsync", "-avz", "--delete", "--exclude", ".git", f"{source}/", f"{destination}/"])
    print(f"Synced from {source} to {destination}")

class SyncHandler(FileSystemEventHandler):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def on_any_event(self, event):
        print(f"Event detected: {event.event_type} - {event.src_path}")
        if event.is_directory:
            return
        sync_directories(self.source, self.destination)

if __name__ == "__main__":
    handler1 = SyncHandler(TARGET_1, TARGET_2)
    handler2 = SyncHandler(TARGET_2, TARGET_1)

    observer1 = Observer()
    observer2 = Observer()

    observer1.schedule(handler1, TARGET_1, recursive=True)
    observer2.schedule(handler2, TARGET_2, recursive=True)

    observer1.start()
    observer2.start()

    print(f"Watching {TARGET_1} and {TARGET_2} for changes. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer1.stop()
        observer2.stop()

    observer1.join()
    observer2.join()
