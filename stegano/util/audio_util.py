import wave
import subprocess


class AudioUtil:
    @staticmethod
    def convert_to_wav(file_in_path: str, file_out_path: str) -> None:
        subprocess.call(['ffmpeg', '-loglevel', 'quiet', '-i', file_in_path, file_out_path])
