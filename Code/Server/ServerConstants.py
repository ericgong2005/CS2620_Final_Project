# Number of seconds before a room or user times out
ROOM_TIMEOUT = 1

# Maximum size for grpc
MAX_GRPC_TRANSMISSION = 200 * 1024 * 1024 # 200 MB
MAX_GRPC_OPTION = [('grpc.max_send_message_length', MAX_GRPC_TRANSMISSION),
                   ('grpc.max_receive_message_length', MAX_GRPC_TRANSMISSION)]

# TimeSync Parameters
WAIT = 0.1
OFFSET_VARIANCE = 0.005 # If the offset differs by more than 5 ms, update
OFFSET_COUNTS = 10
DELAY_COUNTS = 100

# Music Parameters
MAX_TOLERANT_DELAY = 0.1 # Network delay cannot exceed 0.1 seconds
MAX_DISTRIBUTION_TIME = 1 # Predicted time needed to contact all clients
WAIT_MULTIPLIER = 2 # Give at least response time WAIT_MULTIPLIER * Delays
CONSTANT_PROCCESS_TIME = 0.1 # Add some padding time for processing

REACTION_TIME = 0.5 # 1 action per REACTION_TIME seconds, no actions in the last REACTION_TIME seconds of a song

MAX_SONG_QUEUE = 10 # Maximum number of allowed songs
SONG_QUEUE_UPDATE = 1 # Time for song queue updates

# Multithreading
CLIENT_WORKERS = 2 # Number of worker threads for the client
ROOM_WORKERS = 5 # Number of Workers for the ServerRoom Music