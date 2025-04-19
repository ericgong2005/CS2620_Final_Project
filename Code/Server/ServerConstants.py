# Number of seconds before a room times out due to inactivity
ROOM_TIMEOUT = 10

# Maximum size for grpc
MAX_GRPC_TRANSMISSION = 100 * 1024 * 1024 # 100 MB

# TimeSync Parameters
WAIT = 0.1
OFFSET_VARIANCE = 0.001 # If the offset differs by more than 1 ms, update
OFFSET_COUNTS = 10
DELAY_COUNTS = 100

# Music Parameters
MAX_TOLERANT_DELAY = 0.1 # Network delay cannot exceed 0.1 seconds
MAX_DISTRIBUTION_TIME = 1 # Predicted time needed to contact all clients
WAIT_MULTIPLIER = 2 # Give at least response time WAIT_MULTIPLIER * Delays
CONSTANT_PROCCESS_TIME = 0.1 # Add some padding time for processing

REACTION_TIME = 2 # 1 action per REACTION_TIME seconds, no actions in the last REACTION_TIME seconds of a song

MAX_SONG_QUEUE = 10 # Maximum number of allowed songs

# Multithreading
CLIENT_WORKERS = 2 # Number of worker threads for the client