.PHONY: grpc

grpc:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ServerLobby.proto 
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ServerRoomMusic.proto 
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ServerRoomTime.proto

