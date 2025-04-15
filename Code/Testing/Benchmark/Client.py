import time
import grpc
import os
import csv
from mutagen import File as MutagenFile

# Import the generated gRPC modules.
from Testing.Benchmark.BenchmarkGRPC import Benchmark_pb2, Benchmark_pb2_grpc

# Configuration
SERVER_ADDRESS = 'localhost:50051'
# Assumes Music folder is one level above the Code folder.
MUSIC_DIR = "../Music"
LOG_FILE = "upload_log.csv"  # CSV file to log metrics

def upload_file(file_path):
    """Upload a single file and log its metrics."""
    file_name = os.path.basename(file_path)
    
    # Read the audio file as bytes.
    with open(file_path, 'rb') as f:
        audio_bytes = f.read()

    # Calculate file size in MB.
    file_size_mb = len(audio_bytes) / (1024 * 1024)

    # Extract duration (in seconds) using mutagen.
    audio_meta = MutagenFile(file_path)
    duration = audio_meta.info.length if audio_meta and audio_meta.info else 0

    # Create channel options to allow larger message sizes.
    options = [
        ('grpc.max_send_message_length', 100 * 1024 * 1024),   # 100 MB
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)  # 100 MB
    ]
    channel = grpc.insecure_channel(SERVER_ADDRESS, options=options)
    stub = Benchmark_pb2_grpc.MusicUploadServiceStub(channel)

    # Prepare the request message with the file name and audio bytes.
    request = Benchmark_pb2.UploadMusicRequest(
        file_name=file_name,
        audio_data=audio_bytes
    )
    
    # Measure the upload time.
    start_time = time.perf_counter()
    response = stub.UploadMusic(request)
    upload_time = time.perf_counter() - start_time

    print(f"Uploaded '{file_name}': {file_size_mb:.2f} MB, duration {duration:.2f} s, in {upload_time:.4f} s")

    # Log the metrics by appending a row to the CSV file.
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header if file is empty.
        if not file_exists or os.stat(LOG_FILE).st_size == 0:
            writer.writerow(["file_name", "file_size_mb", "duration", "upload_time"])
        writer.writerow([file_name, file_size_mb, duration, upload_time])

def run_upload_all():
    """Iterate over every audio file in the MUSIC_DIR and upload them."""
    for file in os.listdir(MUSIC_DIR):
        # Process common audio file types.
        if file.lower().endswith(('.mp3', '.wav', '.flac', '.aac')):
            file_path = os.path.join(MUSIC_DIR, file)
            print(f"Uploading: {file_path}")
            upload_file(file_path)

if __name__ == "__main__":
    run_upload_all()
