import time
import grpc
import os

# Import the generated gRPC modules.
from Testing.Benchmark.BenchmarkGRPC import Benchmark_pb2, Benchmark_pb2_grpc

# Configuration
SERVER_ADDRESS = 'localhost:50051'
# When running from the Code folder, assume Music is at the project root level.
MUSIC_DIR = "../Music"

def upload_file(file_path):
    """Upload a single file via gRPC."""
    with open(file_path, 'rb') as f:
        audio_bytes = f.read()
    
    # Channel options to allow larger message sizes.
    options = [
        ('grpc.max_send_message_length', 100 * 1024 * 1024),   # 100 MB
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)  # 100 MB
    ]
    channel = grpc.insecure_channel(SERVER_ADDRESS, options=options)
    stub = Benchmark_pb2_grpc.MusicUploadServiceStub(channel)
    
    # Use the file's basename as the file name.
    file_name = os.path.basename(file_path)

    # Prepare the request message.
    request = Benchmark_pb2.UploadMusicRequest(
        file_name=file_name,
        audio_data=audio_bytes
    )
    
    start_time = time.perf_counter()
    response = stub.UploadMusic(request)
    elapsed_time = time.perf_counter() - start_time
    file_size_mb = len(audio_bytes) / (1024 * 1024)
    print(f"Uploaded '{file_name}': {file_size_mb:.2f} MB in {elapsed_time:.4f} sec")

def run_upload_all():
    """Iterate over the entire MUSIC_DIR and upload each audio file."""
    for file in os.listdir(MUSIC_DIR):
        # Process common audio file types. Add more extensions if needed.
        if file.lower().endswith(('.mp3', '.wav', '.flac', '.aac')):
            file_path = os.path.join(MUSIC_DIR, file)
            print(f"Uploading: {file_path}")
            upload_file(file_path)

if __name__ == "__main__":
    run_upload_all()
