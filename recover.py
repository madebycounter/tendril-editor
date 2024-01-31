from load import load_vein
import pickle
import os

SEARCH_DIR = "."

files = os.listdir(SEARCH_DIR)

found_crashes = set()

for file in files:
    if file.startswith("crash_"):
        split = file.split("_")
        if len(split) == 4:
            found_crashes.add(split[1] + "_" + split[2])

for idx, crash in enumerate(found_crashes):
    print(f"{idx + 1}. {crash}")

choice = int(input("Choose a crash to recover: ")) - 1
crash_name = list(found_crashes)[choice]

pickle_file = f"crash_{crash_name}_pickle.pickle"
points_file = f"crash_{crash_name}_points.vein"
veins_file = f"crash_{crash_name}_veins.vein"

pickle_data = None
points_data = None
veins_data = None

if os.path.exists(pickle_file):
    with open(pickle_file, "rb") as f:
        pickle_data = pickle.load(f)

if os.path.exists(points_file):
    points_data = load_vein(veins_file)

if os.path.exists(veins_file):
    veins_data = load_vein(veins_file)

print("\n\nPoints data:")
if points_data is not None:
    print(points_data)
else:
    print("None")

print("\n\nVeins data:")
if veins_data is not None:
    print(veins_data)
else:
    print("None")

print("\n\nPickle data:")
if pickle_data is not None:
    print(pickle_data)
else:
    print("None")
