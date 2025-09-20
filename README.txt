===============================================
    YouTube Downloader Windows - Portable Edition
===============================================

OVERVIEW:
---------
This is a portable YouTube video downloader for Windows that includes all necessary components:
- Python-based GUI application
- FFmpeg for audio/video merging
- yt-dlp for downloading
- Optimized for speed with 8x concurrent downloads

REQUIREMENTS:
-------------
- Windows 10/11
- Python 3.7 or higher (must be installed on the system)
- Internet connection

INSTALLATION:
-------------
1. Extract this folder to any location on your computer
2. Make sure Python is installed on your system
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

USAGE:
------
1. Double-click "Launch YouTube Downloader.bat"
2. The launcher will automatically:
   - Set up the portable environment
   - Check for required dependencies
   - Install yt-dlp if needed
   - Start the application

3. In the application:
   - Paste a YouTube URL
   - Optionally enter a custom filename
   - Select your preferred video quality
   - Click "Download"

FEATURES:
---------
✓ High-speed downloads (8x concurrent fragments)
✓ Zero sleep timers for maximum speed
✓ Network resilience (10 retries, 120s timeout)
✓ Custom filename support
✓ Audio/video merging for high-resolution videos
✓ Retry download button for failed downloads
✓ Multiple quality options (360p to 4K)
✓ Portable - no installation required

SPEED OPTIMIZATIONS:
--------------------
- 8 concurrent downloads for optimal performance
- 16KB buffer size for efficient throughput
- 10MB HTTP chunks for fast data transfer
- Zero artificial delays
- Network resilience for unstable connections

SUPPORTED FORMATS:
------------------
- MP4 (recommended)
- WebM
- MKV
- Audio: MP3, M4A, WebM

TROUBLESHOOTING:
----------------
If you encounter issues:

1. "Python not found":
   - Install Python from https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. "yt-dlp not found":
   - The launcher will automatically install it
   - If it fails, run: pip install yt-dlp

3. "ffmpeg not found":
   - The portable version includes ffmpeg
   - If issues persist, check the ffmpeg folder exists

4. Slow downloads:
   - Check your internet connection
   - Try different video qualities
   - The app uses 8 concurrent downloads by default

5. Download failures:
   - Use the "Retry Download" button
   - Check if the video is available
   - Try a different video quality

FILES INCLUDED:
---------------
- Launch YouTube Downloader.bat (Main launcher)
- Youtube_Downloader_Windows.py (Main application)
- ffmpeg/ (FFmpeg binaries - download separately due to size)
  - ffmpeg.exe (download from https://ffmpeg.org/download.html)
  - ffplay.exe (download from https://ffmpeg.org/download.html)
  - ffprobe.exe (download from https://ffmpeg.org/download.html)
- README.txt (This file)
- .gitignore (Git ignore file for repository)

NOTE: FFmpeg binaries are not included in the GitHub repository due to file size limits.
Download them separately from https://ffmpeg.org/download.html and place in the ffmpeg/ folder.

TECHNICAL DETAILS:
------------------
- Built with Python Tkinter
- Uses yt-dlp for YouTube downloading
- FFmpeg for audio/video processing
- Optimized for Windows 10/11
- Portable design - no registry changes

CONTACT:
--------
For issues or questions, check the troubleshooting section above.

===============================================
    Enjoy fast YouTube downloads!
===============================================
