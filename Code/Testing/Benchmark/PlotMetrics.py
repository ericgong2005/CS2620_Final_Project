import pandas as pd
import matplotlib.pyplot as plt

# Path to the CSV log file.
LOG_FILE = "upload_log.csv"

# Read the CSV file using pandas.
df = pd.read_csv(LOG_FILE)

# --- Graph 1: Upload Time vs File Size ---
plt.figure()
plt.scatter(df['file_size_mb'], df['upload_time'], color='blue')
plt.xlabel("File Size (MB)")
plt.ylabel("Upload Time (s)")
plt.title("Upload Time vs File Size")
plt.grid(True)
plt.savefig("upload_time_vs_file_size.png")
plt.show()

# --- Graph 2: Upload Time vs Song Duration ---
plt.figure()
plt.scatter(df['duration'], df['upload_time'], color='green')
plt.xlabel("Song Duration (s)")
plt.ylabel("Upload Time (s)")
plt.title("Upload Time vs Song Duration")
plt.grid(True)
plt.savefig("upload_time_vs_duration.png")
plt.show()
