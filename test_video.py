import cv2
import os
import sys


def test_video_file(file_path):
    print(f"Testing file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")

    # Try with forward slashes
    forward_path = file_path.replace('\\', '/')
    print(f"Testing with forward slashes: {forward_path}")

    try:
        cap = cv2.VideoCapture(forward_path)
        is_opened = cap.isOpened()
        print(f"Video opened successfully: {is_opened}")

        if is_opened:
            ret, frame = cap.read()
            if ret:
                print(f"Successfully read frame with shape: {frame.shape}")
                height, width = frame.shape[:2]
                print(f"Video dimensions: {width}x{height}")
            else:
                print("Could not read frame")

        cap.release()
    except Exception as e:
        print(f"Error opening video: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_video_file(sys.argv[1])
    else:
        # Provide a default path to test or ask for input
        video_path = input("Enter full path to video file: ")
        test_video_file(video_path)