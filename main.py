#!/usr/bin/env python3
import subprocess
import shutil
import sys

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg is not installed or not in PATH.")
        sys.exit(1)

def build_crop_filter(crop_option, width, height):
    if crop_option == "1:1":
        size = min(width, height)
        return f"crop={size}:{size}"
    elif crop_option == "4:3":
        target_w = width
        target_h = int(width * 3 / 4)
        if target_h > height:
            target_h = height
            target_w = int(height * 4 / 3)
        return f"crop={target_w}:{target_h}"
    else:
        return None

def get_video_resolution(input_file):
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0", input_file
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        w, h = result.stdout.strip().split("x")
        return int(w), int(h)
    except Exception as e:
        print("Error reading video resolution:", e)
        sys.exit(1)

def cut_video(input_file, output_file, start_time, end_time, crop, volume):
    width, height = get_video_resolution(input_file)
    crop_filter = build_crop_filter(crop, width, height)

    filters = []
    if crop_filter:
        filters.append(crop_filter)
    if volume != 1:
        filters.append(f"volume={volume}")
    filter_chain = ",".join(filters) if filters else None

    cmd = ["ffmpeg", "-y", "-i", input_file, "-ss", start_time, "-to", end_time]
    if filter_chain:
        cmd += ["-vf", filter_chain]
    cmd.append(output_file)

    print("Running ffmpeg command...")
    try:
        subprocess.run(cmd, check=True)
        print("Video processing complete:", output_file)
    except subprocess.CalledProcessError as e:
        print("ffmpeg failed:", e)
        sys.exit(1)

def main():
    check_ffmpeg()

    input_file = input("Enter input video file: ").strip()
    output_file = input("Enter output video file: ").strip()
    start_time = input("Enter start time (HH:MM:SS): ").strip()
    end_time = input("Enter end time (HH:MM:SS): ").strip()
    crop = input("Enter crop option (original, 1:1, 4:3): ").strip().lower()
    volume = input("Enter volume multiplier (1-10): ").strip()

    try:
        volume = int(volume)
        if not (1 <= volume <= 10):
            raise ValueError
    except ValueError:
        print("Invalid volume multiplier. Must be an integer between 1 and 10.")
        sys.exit(1)

    cut_video(input_file, output_file, start_time, end_time, crop, volume)

if __name__ == "__main__":
    main()
