# CS2620 Final Project
Usage: All code can be run from the Code directory using commands from the Makefile:
 - `make grpc`: Compiles the GRPC proto files
 - `make clean`: removes __pycache__ folders and the GRPC generated files
 - `make Server <port>`: starts ServerLobby.py on the specified port, using the public hostname of the current device by default
 - `make Client <addr>`: starts ClientGUI.py, connecting to server specified by `addr`
 - `make ClientTerminal <addr>`: starts ClientTerminal.py, connecting to server specified by `addr`


 You must use `brew install --cask vlc` to install the vlc media player
 
 You must also create a virtual environment using the command
 ```
 $ python -m venv .venv
 ```

Then activate the virtual environment using
```
$ source .venv/bin/activate
```

and then pip install the requirements using
```
$ pip install -r requirements.txt
```

and to deactivate use
```
$ deactivate
```