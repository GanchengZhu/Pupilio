# Pupilio SDK Update Log

## Version 1.1.5 (Build 1) - 2024-11-05
- Need to fix recalibration
- Improve calibration UI
- Fix a bug that causes Python processes to hang indefinitely.

## Version 1.1.4 (Build 1) - 2024-11-04
### Changes:
- Add create session name checking. The session name must contain only letters, digits or underscores without any special characters.
- Delete resource deep gaze icon.
- Update libfilter.dll with MSVC_RUNTIME_LIBRARY.
- Delete /example/run_demo.bat. Add example/picture_free_viewing/run_demo_psychopy.bat, and 
example/picture_free_viewing/run_demo_pygame.bat.
- Integrating dll files needed

## Version 1.1.3 (Build 1) - 2024-11-02
### Changes:
- Calibration_draw function logic modify.
- Calibration PsychoPy components set units `pix`.
- Press R to recalibrate.
- Deleting pygame.init in graphics.py, this may cause minimizing pygame screen.



## Version 1.1.2 (Build 1) - 2024-10-28
### Changes:
- Rewrite some features using c++
- Support PyGame and PsychoPy
- Removing some useless py files
- Update example code

## Version 1.1.1 (Build 3) - 2024-10-26
### Changes:
- Added `build` number mechanism using timestamp.
- Added `bino_eye_gaze_position`.
- Added heuristic filter.
- Added image previewer.
- 

### Bug Fixes:
- None

---

## Version 1.1.0 - 2024-09
### Changes:
- Introduced support for multiple libraries (`lib/*.dll`) in package data.
- Added dependencies: `numpy`, `pygame`, `websockets`.

### Bug Fixes:
- Fixed missing files in `lib` directory during packaging.
- Resolved compatibility issues with Python 3.8+.

---

