.PHONY: grpc

grpc:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. client/Client.proto 
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. server/ServerLobby.proto 
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. server/ServerRoomMusic.proto 
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. server/ServerRoomTime.proto

