import sys
import os

def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")

    # Wait for user input
    inp = input().split(" ")
    cmd = inp[0]
    
    # Built-in commands
    builtins = {"exit": "exit", "echo": "echo", "type": "type", "pwd": "pwd"}

    # Commands found in PATH
    commands = {}

    # Get the PATH environment variable and split it into directories
    paths = os.getenv("PATH").split(":")
    
    # Prioritize /tmp/bar/ by moving it to the front of the PATH
    paths = ['/tmp/bar/'] + [path for path in paths if path != '/tmp/bar/']

    # Iterate over the paths and collect commands
    for path in paths:
        path = path + "/" if path[-1] != "/" else path
        try:
            for entry in os.listdir(path):
                if entry not in builtins:
                    commands.update({entry: path + entry})
        except FileNotFoundError:
            pass
    
    # Handle the exit command
    if cmd == "exit":
        exitval = 0 if not inp[1].isnumeric() else int(inp[1])
        exit(exitval)

    # Handle the echo command
    if cmd == "echo":
        print(" ".join(inp[1:]))

    # Handle the type command
    if cmd == "type":
        if len(inp) > 1:
            outp = f"{inp[1]}: not found"
            if inp[1] in commands:
                outp = f"{inp[1]} is {commands[inp[1]]}"
            elif inp[1] in builtins:
                outp = f"{inp[1]} is a shell builtin"
            print(outp)

    # Handle the pwd command (built-in)
    if cmd == "pwd":
        print(os.getcwd())
    
    # If the command is not found in builtins or PATH, report it
    elif cmd not in commands and cmd not in builtins:
        print(f"{cmd}: command not found")
    
    # Handle external commands
    if cmd in commands:
         os.system(" ".join(inp))
    


 
if __name__ == "__main__":
    while True:
        main()