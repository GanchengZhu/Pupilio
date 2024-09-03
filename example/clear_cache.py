
"""
If you find that Deep Gaze generates some log files and temporary files
for the eye tracking stream during use, and these files are taking up
too much space on your disk, you can call the clear_cache function to
clean up these files.
"""

# step 1: load DeepGaze module
from deepgaze import DeepGaze

# step 2: instantiate DeepGaze
deep_gaze = DeepGaze()

# step 3: create a task session with passing an arbitrary argument
deep_gaze.create_session(session_name="tmp")

# step 4: do clear cache
deep_gaze.clear_cache()
