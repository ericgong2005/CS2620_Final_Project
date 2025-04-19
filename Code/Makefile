TARGETS = grpc clean Server Client ClientTerminal ServerRoom ClientPlayer

.PHONY: $(TARGETS)

ARGS := $(filter-out $(TARGETS), $(MAKECMDGOALS))

grpc:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. Client/ClientGRPC/Client.proto
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. Server/ServerLobbyGRPC/ServerLobby.proto 
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. Server/ServerRoomGRPC/ServerRoomMusic.proto 
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. Server/ServerRoomGRPC/ServerRoomTime.proto 
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. Testing/Benchmark/BenchmarkGRPC/Benchmark.proto 

clean:
	@echo "Removing __pycache__"
	-find . -type d -name '__pycache__' -exec rm -rf {} +
	@echo "Removing gRPC generated files"
	-find . -type f -name "*_pb2.py" -delete
	-find . -type f -name "*_pb2_grpc.py" -delete
	@echo "Removing Client generated files"
	-find . -type d -name 'Client_*' -exec rm -rf {} +
	make grpc

Server:
	python -m Server.ServerLobby $(ARGS)

Client:
	python -m Client.ClientGUI $(ARGS)

ClientTerminal:
	python -m Client.ClientTerminal $(ARGS)

ServerRoom:
	@echo "Note this should only be used for testing..."
	python -m Server.ServerRoom $(ARGS)

ClientPlayer:
	@echo "Note this should only be used for testing..."
	python -m Client.ClientPlayer

%:
	@echo "Unrecognised Command"