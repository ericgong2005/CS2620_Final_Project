# CS2620 Final Project
Usage: All code can be run from the Code directory using commands from the Makefile:
 - `make grpc`: Compiles the GRPC proto files
 - `make clean`: removes __pycache__ folders and the GRPC generated files
 - `make Server <addr>`: starts ServerLobby.py on the specified address `addr`
 - `make Client <addr>`: starts ClientGUI.py, connecting to server specified by `addr`
 - `make ClientTerminal <addr>`: starts ClientTerminal.py, connecting to server specified by `addr`