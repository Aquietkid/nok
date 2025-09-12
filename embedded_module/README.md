ESP32 Door Control
---

This repository hosts a part of a larger project: an automated door opening and closing system using facial recognition to identify authorized people and open the door for them.

This repository is the embedded module of the system, with a main program being flashed onto an ESP32 microcontroller. This program controls a servo motor which opens and closes a door. A button is attached to ring the doorbell, and request facial recognition from another server in the architecture of the larger system. Based on the authentication, the door will open for authorized persons, while remaining closed for unknown persons. There will be an administrative control panel provided to the user of the system to manually open and close the door.

# Development Environment
---

The project is built inside VSCodium in C++, using PlatformIO to aid in flashing the program onto the ESP32 and using the serial monitor over a USB port.
