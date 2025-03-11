import sys
import os

def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")

    # Wait for user input
    inp = input().split(" ")
    cmd = inp[0]
    
    builtins = {"exit": "exit", "echo": "echo", "type": "type", "pwd": "pwd", "cd": "cd"}
    commands = {}

    # Get the PATH environment variable and split it into directories
    paths = os.getenv("PATH").split(":")

    # Iterate over the paths and collect commands
    for path in paths:
        if not path.endswith("/"):
            path += "/"
        try:
            for entry in os.listdir(path):
                if entry not in builtins and entry not in commands:
                    commands[entry] = path + entry
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
    
    # Handle the cd command
    if cmd == "cd":
        if len(inp) < 2:
            print("cd: missing operand") # No path provided
        else:
            new_dir = inp[1]

            # Home directory
            if new_dir == "~":
                new_dir = os.path.expanduser("~")

            if os.path.isabs(new_dir): # Ensure absolute path
                try:
                    os.chdir(new_dir)
                except FileNotFoundError:
                    print(f"cd: {new_dir}: No such file or directory")
                except NotADirectoryError:
                    print(f"cd: {new_dir}: Not a directory")
                except PermissionError:
                    print(f"cd: {new_dir}: Permission denied")
            else:   # Relative Path
                try: # Join the relative path with the current working directory
                    os.chdir(os.path.join(os.getcwd(), new_dir))
                except FileNotFoundError:
                    print(f"cd: {new_dir}: No such file or directory")
                except NotADirectoryError:
                    print(f"cd: {new_dir}: Not a directory")
                except PermissionError:
                    print(f"cd: {new_dir}: Permission denied")

    # If the command is not found in builtins or PATH, report it
    elif cmd not in commands and cmd not in builtins:
        print(f"{cmd}: command not found")
    
    # Handle external commands
    if cmd in commands:
         os.system(" ".join(inp))
    


 
if __name__ == "__main__":
    while True:
        main()