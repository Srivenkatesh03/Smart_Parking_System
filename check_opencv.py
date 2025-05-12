import cv2
import sys

print(f"OpenCV version: {cv2.__version__}")
print(f"Python version: {sys.version}")

# Check OpenCV build information
build_info = cv2.getBuildInformation()

# Look for video IO support in the build info
video_io = "Video I/O:" in build_info
ffmpeg = "ffmpeg" in build_info.lower()
gstreamer = "gstreamer" in build_info.lower()

print(f"Video I/O support available: {video_io}")
print(f"FFmpeg support: {ffmpeg}")
print(f"GStreamer support: {gstreamer}")