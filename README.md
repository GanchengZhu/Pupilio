# Pupilio

Pupilio is a lightweight Python package developed by Hangzhou Shenning Technology Co., Ltd., designed to drive and control the Pupil.IO Eye Tracker. It offers a user-friendly interface for ease of use, providing functionalities for eye-tracking data recording, calibration, and validation. Pupilio seamlessly integrates with platforms such as PsychoPy, PyGame, and more.

## Features

- **High-performance control**: Manage the Pupil.IO Eye Tracker with high sampling rates and precise eye movement and pupil data.
- **Flexible Integration**: Supports integration with popular platforms like PsychoPy and PyGame.
- **User-friendly Interface**: Intuitive controls for calibration, validation, and data recording.

## What's Pupil.IO?

![Pupil.IO](docs/_static/images/intro/about/banner.png)

[Pupil.IO](https://www.deep-gaze.com/) is a high-performance, high-speed, and high-precision eye-tracking system designed by Hangzhou Shenning Technology Co., Ltd. It offers high sampling rates and precise eye movement data, making it a valuable tool for scientific and clinical applications.

### Specifications of Eye Tracker

| Attribute                | Specification                                 |
|--------------------------|-----------------------------------------------|
| Sample Rate              | 200 Hz [Firmware upgradable to 400 Hz]        |
| Accuracy                 | 0.5°                                          |
| Precision                | 0.03°                                         |
| Blink/Occlusion Recovery | 5 ms @ 200 Hz, 2.5 ms @ 400 Hz                |
| Head Box                 | 40 cm x 40 cm @ 70 cm                         |
| Operation Range          | 50 - 90 cm                                    |
| Gaze Signal Delay        | < 6 ms                                        |
| Tracking Technology      | Neural Networks                               |
| Dimension                | 32 cm x 45 cm x 20 cm                         |
| Weight                   | 5 kg [Eye-tracker + Display + Compute Module] |
| Operating System         | Windows 11                                    |
| SDK                      | C/C++/Python                                  |

## Installation

Currently, all eye trackers shipped with Pupilio are pre-configured with the necessary Pupilio Python packages. If we need to upgrade this package, please enter the following command in the command prompt or PowerShell window:

```bash
pip install -U pupilio
```


## Quick Start
Here is a simple example to get started with Pupilio:

```python
# load PyGame library
import pygame
from pygame.locals import FULLSCREEN, HWSURFACE

# initialize PyGame
pygame.init()
# define the scree size
scn_width, scn_height = (1920, 1080)
# set a fullscreen mode with the above size
win = pygame.display.set_mode((scn_width, scn_height), FULLSCREEN|HWSURFACE)

# load Pupilio library
from pupilio import Pupilio

# instantiate a connection to the tracker
pupil_io = Pupilio()

# create a task session, and set a session name. 
# The session name must contain only letters, digits or underscores without any special characters.
pupil_io.create_session(session_name="quick_start")

# calibration and validation (recommended)
# set 'validate' to True if we would like to verify the calibration results
pupil_io.calibration_draw(screen=win, validate=True)

# start retrieving gaze
pupil_io.start_sampling()

# hang the main thread for 5 seconds by game
# eye tracking sampling are running on the background thread
pygame.time.wait(5 * 1000)

# stop eye tracking sampling
pupil_io.stop_sampling()

# sleep for 100 ms to capture ending samples
pygame.time.wait(100)

# save eye movement data
pupil_io.save_data("eye_movement.csv")

# release the tracker instance
# clean up Pupilio resources
pupil_io.release()

# quit pygame
pygame.quit()
```

## Documentation

Comprehensive documentation is available at Pupilio [Documentation](https://pupilio.readthedocs.io/en/latest/start/demo.html).

## Support

If you encounter any issues or have questions, please open an issue on GitHub or contact [zhugc2016@gmail.com](mailto:zhugc2016@gmail.com).

## License

Pupilio is a proprietary software developed by Hangzhou Shenning Technology Co., Ltd. All rights reserved. Unauthorized use, distribution, or modification is prohibited without explicit permission. For licensing inquiries, please contact [zhugc2016@gmail.com](mailto:zhugc2016@gmail.com).

## Acknowledgments
Pupilio is developed and maintained by Hangzhou Shenning Technology Co., Ltd. Special thanks to the community for their valuable feedback and support.
