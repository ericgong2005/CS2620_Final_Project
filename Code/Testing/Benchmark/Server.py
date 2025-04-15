from concurrent import futures
import grpc
import time
import os

# Import the generated gRPC modules.
from Testing.Benchmark.BenchmarkGRPC import Benchmark_pb2, Benchmark_pb2_grpc

# Configuration
SERVER_ADDRESS = '[::]:50051'
OUTPUT_DIR = 'UploadedFiles'  # Directory where uploaded files are saved.

# Ensure the output directory exists.
os.makedirs(OUTPUT_DIR, exist_ok=True)

class MusicUploadServiceServicer(Benchmark_pb2_grpc.MusicUploadServiceServicer):
    def UploadMusic(self, request, context):
        # Extract the file name from the request and prepare a save path.
        file_name = request.file_name
        file_path = os.path.join(OUTPUT_DIR, file_name)
        
        # Write the audio bytes to the file.
        with open(file_path, 'wb') as f:
            f.write(request.audio_data)
        print(f"Received and saved audio file to {file_path}")
        
        return Benchmark_pb2.UploadMusicResponse()

def serve():
    # Create a gRPC server with options to support larger messages.
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),   # 100 MB
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)  # 100 MB
        ]
    )
    Benchmark_pb2_grpc.add_MusicUploadServiceServicer_to_server(MusicUploadServiceServicer(), server)
    server.add_insecure_port(SERVER_ADDRESS)
    server.start()
    print(f"Server running on {SERVER_ADDRESS} ...")
    try:
        while True:
            time.sleep(86400)  # Keep the server running.
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
