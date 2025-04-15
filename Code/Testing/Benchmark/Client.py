import time
import grpc
import os

# Import the generated gRPC modules.
from Testing.Benchmark.BenchmarkGRPC import Benchmark_pb2, Benchmark_pb2_grpc

# Configuration
SERVER_ADDRESS = 'localhost:50051'
# Adjust the relative path and filename as needed (note the underscores in the actual file name).
AUDIO_FILE_PATH = "../Music/MapleLeafRag.mp3"
OUTPUT_FILENAME = 'MapleLeafRag.mp3'  # The name for cross-checking on the server side

def run_upload():
    # Read the audio file as bytes.
    with open(AUDIO_FILE_PATH, 'rb') as f:
        audio_bytes = f.read()

    # Create channel options to allow larger message sizes.
    options = [
        ('grpc.max_send_message_length', 100 * 1024 * 1024),   # 100 MB
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)  # 100 MB
    ]

    # Create a gRPC channel with the specified options.
    channel = grpc.insecure_channel(SERVER_ADDRESS, options=options)
    stub = Benchmark_pb2_grpc.MusicUploadServiceStub(channel)

    # Prepare the request message.
    request = Benchmark_pb2.UploadMusicRequest(audio_data=audio_bytes)

    # Start the timer.
    start_time = time.perf_counter()

    # Make the gRPC call.
    response = stub.UploadMusic(request)

    # Stop the timer.
    elapsed_time = time.perf_counter() - start_time

    # Print the metric: file size and elapsed time.
    file_size_mb = len(audio_bytes) / (1024 * 1024)
    print(f"Uploaded file of size: {file_size_mb:.2f} MB in {elapsed_time:.4f} seconds")

if __name__ == "__main__":
    run_upload()
