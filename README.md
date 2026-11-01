<img align="left" width="80" src="https://github.com/user-attachments/assets/db3593cf-f007-4fb4-b7c5-117f489f5f92" />

# Audibly3D - 3D Audio For Windows
**A real-time positional acoustic simulation application for Windows to simulate 3D soundscapes**

* An interactive Tkinter UI allowing dynamic, real-time spatial manipulation of virtual audio sources
* Integrated Pycaw and comtypes libraries to interface directly with low-level Windows Audio Session APIs

## About
By interfacing with Windows Audibly3D adds real-time perceived directionality to your output device:

![OrbitGif](https://github.com/user-attachments/assets/8298719b-5e7a-40db-83ce-ebf2511c2b1b)

### Click Mode
Click mode allows you to move around the Audio Source yourself, either click or hold to move the Audio Source around.

### Orbit Mode
Orbit mode (As seen in the first demonstration GIF) gives a constantly rotating 360° Audio Source.

### Settings
Adjust settings in real-time, once you've honed in your sweet spot click save and your settings will stay between sessions! 

If you ever want to go back you can revert to the default settings at any time.

### Made in ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) Utilising:
* [Pycaw](https://github.com/AndreMiras/pycaw)
* [Tkinter](https://docs.python.org/3/library/tkinter.html)

## Getting Started
> [!NOTE]
>**THIS IS A WINDOWS ONLY PROJECT**!  
>This project interfaces directly with windows to control audio and therefore will **NOT** work with other operating systems

### Prerequisites
Install the prerequisites located in the requirements.txt file:
```sh
  pip install -r requirements.txt
```
### Installation
Clone the repo:
```sh
   git clone https://github.com/LoganMee/Audibly3D.git
```
## License
This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

## Acknowledgments
* [Top View Man Icon - Icons8](https://icons8.com/icon/118576/top-view-man)
* [Clockwise icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/clockwise)

<!-- MARKDOWN IMAGES & GIFS -->
[Audibly3DLogo]: https://github.com/user-attachments/assets/db3593cf-f007-4fb4-b7c5-117f489f5f92
[OrbitGif]: https://github.com/user-attachments/assets/8298719b-5e7a-40db-83ce-ebf2511c2b1b
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
