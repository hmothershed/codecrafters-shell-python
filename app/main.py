import sys
import os

supported_commands = ["echo", "exit", "type"]
 
def find_command_in_path(command):
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for dir in path_dirs:
        path = os.path.join(dir, command)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None
 
def echo(data: list):
    print(" ".join(data))
 
def exit_cmd(data: list):
    exit(int(data[0]))
 
def type_cmd(data: list):
    if data[0] in supported_commands:
        print(f"{data[0]} is a shell builtin")
    elif path := find_command_in_path(data[0]):
        print(f"{data[0]} is {path}")
    else:
        print(f"{data[0]} not found")
 
def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
         # Wait for user input
        command, *data = input().split(" ")
        if command == "exit":
            exit_cmd(data)
        elif command == "echo":
            echo(data)
        elif command == "type":
            type_cmd(data)
        elif path := find_command_in_path(command):

            os.system(f"{path} {' '.join(data)}")
        else:
            print(f"{command}: command not found")
 
if __name__ == "__main__":
    main()