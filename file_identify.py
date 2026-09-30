from pathlib import Path
from magika import Magika

# Defining the Target Directory
target_dir = Path("~/Desktop/Python-Projects").expanduser()
m = Magika()

# Looping through the files
for file_path in target_dir.rglob("*"):
    if file_path.is_file():
        res = m.identify_path(file_path)
        print(f"{file_path} -> {res.output.label}")