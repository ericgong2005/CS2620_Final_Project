from concurrent import futures
import grpc
import time
import os

# Import the generated gRPC modules.
from Testing.Benchmark.BenchmarkGRPC import Benchmark_pb2, Benchmark_pb2_grpc

# Configuration
SERVER_ADDRESS = '[::]:50051'
OUTPUT_DIR = 'uploaded_files'  # Directory where uploaded files will be saved
OUTPUT_FILENAME = 'MapleLeafRag.mp3'  # File name for saving the uploaded audio

# Ensure the output directory exists.
os.makedirs(OUTPUT_DIR, exist_ok=True)

class MusicUploadServiceServicer(Benchmark_pb2_grpc.MusicUploadServiceServicer):
    def UploadMusic(self, request, context):
        # Write the received audio bytes to a file.
        file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        with open(file_path, 'wb') as f:
            f.write(request.audio_data)
        print(f"Received and saved audio file to {file_path}")
        # Return an empty response.
        return Benchmark_pb2.UploadMusicResponse()

def serve():
    # Create a gRPC server with options to support larger message sizes.
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
            time.sleep(86400)  # Keep the server alive.
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
