find . -name "*.mp3" -exec ffmpeg -i {} {}.wav \;
