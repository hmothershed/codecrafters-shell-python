import sys
import os
import shlex
import subprocess

def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")
    sys.stdout.flush()  # ensure the prompt appears immediately

    try: 
        # Wait for user input
        inp = input().strip()
        tokens = shlex.split(inp)   # properly handle quoted strings
    except ValueError as e:
        print(f"Error parsing input: {e}")
        return
   
    if not tokens:
        return  # ignore empty input
    
    # Check for output redirection
    if ">" in tokens or "1>" in tokens:
        try:
            redirect_index = tokens.index(">") if ">" in tokens else tokens.index("1>")
            command_part = tokens[:redirect_index]
            output_file = tokens[redirect_index + 1]

            if not command_part or not output_file:
                print("Syntax error: missing command or output file")
                return
        except IndexError:
            print("Syntax error: missing output file")
            return
    else:
        command_part = tokens
        output_file = None


    cmd = command_part[0]
    
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
    
    # Built=in commands
    def handle_builtin_output(output_text):
        """Redirect output to file if needed, otherwise print."""
        if output_file:
            with open(output_file, "w") as f:
                f.write(output_text + "\n")
        else:
            print(output_text)

    # Handle the exit command
    if cmd == "exit":
        # exitval = 0 if len(inp) == 1 else int(inp[1]) if inp[1].isnumeric() else 0
        # exit(exitval)
        exit(int(command_part[1]) if len(command_part) > 1 and command_part[1].isdigit() else 0)

    # Handle the echo command
    elif cmd == "echo":
        handle_builtin_output(" ".join(command_part[1:]))

    # Handle the type command
    elif cmd == "type":
        if len(command_part) > 1:
            outp = f"{command_part[1]}: not found"
            if command_part[1] in commands:
                outp = f"{command_part[1]} is {commands[command_part[1]]}"
            elif command_part[1] in builtins:
                outp = f"{command_part[1]} is a shell builtin"
            handle_builtin_output(outp)

    # Handle the pwd command (built-in)
    elif cmd == "pwd":
        handle_builtin_output(os.getcwd())
    
    # Handle the cd command
    elif cmd == "cd":
        if len(command_part) < 2:
            print("cd: missing operand") # No path provided
        else:
            new_dir = command_part[1]

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
         # os.system(" ".join(inp))
         # os.execvp(cmd, inp)
         with open(output_file, "w") if output_file else sys.stdout as f:
             subprocess.run(command_part, stdout=f, stderr=sys.stderr)
    
 
if __name__ == "__main__":
    while True:
        main()