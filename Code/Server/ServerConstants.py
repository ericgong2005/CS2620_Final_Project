# Number of seconds before a room times out due to inactivity
ROOM_TIMEOUT = 30

# Maximum size for grpc
MAX_GRPC_TRANSMISSION = 100 * 1024 * 1024 # 100 MB

# TimeSync Parameters
WAIT = 0.5
MAX_OFFSET_VARIANCE = 10**(-8) # Variance of 10ns
MAX_REPEATS = 10
COUNTS = 10

# Music Parameters
MAX_TOLERANT_DELAY = 0.1 # Network delay cannot exceed 0.1 seconds
MAX_DISTRIBUTION_TIME = 1 # Predicted time needed to contact all clients
WAIT_MULTIPLIER = 2 # Give at least response time WAIT_MULTIPLIER * Delays
CONSTANT_PROCCESS_TIME = 0.1 # Add some padding time for processing