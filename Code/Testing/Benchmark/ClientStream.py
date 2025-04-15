import time
import grpc
import os
import csv
from mutagen import File as MutagenFile


# Import the generated gRPC modules.
from Testing.Benchmark.BenchmarkGRPC import Benchmark_pb2, Benchmark_pb2_grpc


# Configuration
SERVER_ADDRESS = 'localhost:50051'
# Adjust path based on your structure: Music folder is one level up from Code folder.
MUSIC_DIR = "../Music"
LOG_FILE = "chunk_upload_log.csv"  # CSV file to log metrics


def upload_chunks_for_duration(file_path, chunk_duration):
   """
   For the given file at file_path and chunk_duration (in seconds), split the file into chunks,
   upload each chunk via gRPC, and measure total upload time and the maximum chunk time.
   Returns: (total_time, max_chunk_time)
   """
   file_name = os.path.basename(file_path)
   # Read the complete file as bytes.
   with open(file_path, 'rb') as f:
       audio_bytes = f.read()
   total_file_size = len(audio_bytes)
  
   # Obtain the file's duration (in seconds) using mutagen.
   meta = MutagenFile(file_path)
   total_duration = meta.info.length if meta and meta.info else None
   if not total_duration:
       raise ValueError(f"Could not determine duration for {file_path}")
  
   # Calculate approximate bytes per second and determine chunk size.
   bytes_per_sec = total_file_size / total_duration
   chunk_size = int(bytes_per_sec * chunk_duration)
  
   # Split the audio bytes into consecutive chunks.
   chunks = [audio_bytes[i: i + chunk_size] for i in range(0, total_file_size, chunk_size)]
  
   # Prepare the gRPC channel (with increased limits).
   options = [
       ('grpc.max_send_message_length', 100 * 1024 * 1024),
       ('grpc.max_receive_message_length', 100 * 1024 * 1024)
   ]
   channel = grpc.insecure_channel(SERVER_ADDRESS, options=options)
   stub = Benchmark_pb2_grpc.MusicUploadServiceStub(channel)
  
   total_time = 0.0
   max_chunk_time = 0.0
  
   for idx, chunk in enumerate(chunks):
       request = Benchmark_pb2.UploadChunkRequest(
           file_name=file_name,
           chunk_data=chunk,
           chunk_index=idx
       )
       start_time = time.perf_counter()
       _ = stub.UploadChunk(request)
       chunk_time = time.perf_counter() - start_time
       total_time += chunk_time
       max_chunk_time = max(max_chunk_time, chunk_time)
  
   return total_time, max_chunk_time


def run_chunked_upload_tests_all_files():
   """
   Iterates over every audio file in MUSIC_DIR.
   For each file, tests chunk durations from 1 to 30 seconds.
   Logs results (file_name, chunk_duration, total_time, max_chunk_time) into a CSV file.
   """
   # Write CSV header.
   with open(LOG_FILE, 'w', newline='') as csvfile:
       writer = csv.writer(csvfile)
       writer.writerow(["file_name", "chunk_duration", "total_time", "max_chunk_time"])
  
   for file in os.listdir(MUSIC_DIR):
       if file.lower().endswith(('.mp3', '.wav', '.flac', '.aac')):
           file_path = os.path.join(MUSIC_DIR, file)
           for n in range(1, 31):
               try:
                   total_time, max_time = upload_chunks_for_duration(file_path, n)
                   with open(LOG_FILE, 'a', newline='') as csvfile:
                       writer = csv.writer(csvfile)
                       writer.writerow([file, n, total_time, max_time])
                   print(f"File: {file}, Chunk Duration: {n}s, Total Time = {total_time:.4f}s, Max Chunk Time = {max_time:.4f}s")
               except Exception as e:
                   print(f"Error processing {file} for chunk duration {n}s: {e}")


if __name__ == '__main__':
   run_chunked_upload_tests_all_files()



