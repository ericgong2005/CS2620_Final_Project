Time synchronization requirements:
 - Will need accurate shared time
 - Won't need very strict ordering of evernts, we can introduce orchestrated delays to make things work on the client end
 - NTP-like system (network time protocol) seems like a good choice
    - The client requests a time sync and records the amount of time needed for a response, this determines the delay
    - The client gets the server time on response and calculates the offset from its own clock to know the true server time
 - Process
    - The client sends request
    - The server responds with its actual time
    - delay = half of response time
    - offset = returned server time - (client time + delay)


Server setup:
 - One central process that forks off children that serve as the jam rooms
 - Each jam room has its own gRPC handler
 - central process has gRPC handler that allows for creation of new rooms and joining exisiting rooms
 - each child should have a dedicated time-sync gRPC (less chance of backlogs) and one for the rest of the music related things

Considerations:
 - Will need to determine how many rounds of syncing are necessary for accuracy. If it takes a long time, might want to orchestrate some sort of delay on the user end before the music starts (ie: force everyone to pick a song and then vote on a song, with minimum 10s delay for each)
 - The client can call the server's addsong,pausesong, etc, and the server will inform other clients using the client grpc addsong, pausesong, etc. There should thus be a direct correspondence for a lot of the RoomMusic and Client gRPC commands. The code handling each of the calls will be vastly different though!
 - Might be nice to have a list of all online users and what room they are in, maintained in ServerLobby
 - Ensure that all room names are prepended with "Room: " for clarity
 - If a room has no people for a certain period of time, kill it
 - If a user is inactive for a while, ping the user's current state, if no response, remove it from the active list


GRPC specs:
 - ServerLobby:
    - JoinLobby: Delcares a client to be online (unique username, nonpersistent)
    - GetRooms: Should return a list of room names (all names must be different) and room addresses
    - JoinRoom: ServerRoom informs ServerLobby someone has joined
    - LeaveRoom: either ServerRoom or Client informs Serverlobby that client has returned to lobby
    - StartRoom: Starts a new room, still needs a separate joinroom request
 - ServerRoom:
    - RoomTime:
        - TimeSync: client passes its clock time, calculated offset and calculated delay (-1 if never calculated yet)
    - RoomMusic:
        - KillRoom
        - CurrentState
        - AddSong
        - DeleteSong
        - PauseSong
        - MovePosition
 - Client:
    - CurrentState
    - AddSong
    - DeleteSong
    - PauseSong
    - MovePosition