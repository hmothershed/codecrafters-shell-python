import sys
import os

def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")
     # Wait for user input
    paths = os.getenv("PATH").split(":")
    inp = input().split(" ")
    cmd = inp[0]
    builtins = {"exit": "exit", "echo": "echo", "type": "type"}
    commands = {}
    for path in paths:
        path = path + "/" if path[-1] != "/" else path
        try:
            for entry in os.listdir(path):
                if entry not in builtins:
                    commands.update({entry: path + entry})
        except FileNotFoundError:
            pass
    if cmd == "exit":
        exitval = 0 if not inp[1].isnumeric() else int(inp[1])
        exit(exitval)
    if cmd == "echo":
        print(" ".join(inp[1:]))
    if cmd == "type":
        outp = f"{inp[1]}: not found"
        if inp[1] in commands:
            outp = f"{inp[1]} is {commands[inp[1]]}"
        elif inp[1] in builtins:
            outp = f"{inp[1]} is a shell builtin"
        print(outp)
    if cmd not in commands and cmd not in builtins:
        print(f"{cmd}: command not found")
    if cmd in commands:
         os.system(" ".join(inp))


 
if __name__ == "__main__":
    while True:
        main()