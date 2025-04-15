
from concurrent import futures
import grpc
import time
import os


# Import the generated gRPC modules.
from Testing.Benchmark.BenchmarkGRPC import Benchmark_pb2, Benchmark_pb2_grpc


# Configuration
SERVER_ADDRESS = '[::]:50051'
OUTPUT_DIR = 'UploadedChunks'  # Directory to store uploaded files/chunks


# Ensure the output directory exists.
os.makedirs(OUTPUT_DIR, exist_ok=True)


class MusicUploadServiceServicer(Benchmark_pb2_grpc.MusicUploadServiceServicer):
   def UploadChunk(self, request, context):
       """
       Receives a chunk and appends it to the file corresponding to request.file_name.
       For simplicity, we assume sequential (synchronous) requests so chunks arrive in order.
       """
    #    file_path = os.path.join(OUTPUT_DIR, request.file_name)
    #    mode = 'ab' if os.path.exists(file_path) else 'wb'
    #    with open(file_path, mode) as f:
    #        f.write(request.chunk_data)
    #    print(f"Received chunk {request.chunk_index} for file '{request.file_name}'")
       return Benchmark_pb2.UploadChunkResponse()


def serve():
   server = grpc.server(
       futures.ThreadPoolExecutor(max_workers=10),
       options=[
           ('grpc.max_send_message_length', 100 * 1024 * 1024),
           ('grpc.max_receive_message_length', 100 * 1024 * 1024)
       ]
   )
   Benchmark_pb2_grpc.add_MusicUploadServiceServicer_to_server(MusicUploadServiceServicer(), server)
   server.add_insecure_port(SERVER_ADDRESS)
   server.start()
   print(f"Chunk upload server running on {SERVER_ADDRESS} ...")
   try:
       while True:
           time.sleep(86400)
   except KeyboardInterrupt:
       server.stop(0)


if __name__ == '__main__':
   serve()
