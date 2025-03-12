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
        if not inp:
            return  # ignore empty input
        tokens = shlex.split(inp)   # properly handle quoted strings
    except ValueError as e:
        print(f"Error parsing input: {e}")
        return
   
    
    
    # check for stdout redirection
    output_file = None
    error_file = None
    if ">" in tokens or "1>" in tokens:
        try:
            redirect_index = tokens.index(">") if ">" in tokens else tokens.index("1>")
            output_file = tokens[redirect_index + 1]    # get the file to write to
            tokens = tokens[:redirect_index]    # remove redirection part from command
        except IndexError:
            print("Syntax error: missing output file")
            return
    
    # check stderr redirection
    if "2>" in tokens:
        try:
            error_index = tokens.index("2>")
            error_file = tokens[error_index + 1]    # get the error file
            tokens = tokens[:error_index]   # remove redirection part from command
        except:
            print("Syntax error: missing error file")
            return
        
    if not tokens:
        return  # if only redirection was given, ignore it

    cmd = tokens[0]
    
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
    def handle_output(text):
        """Redirect output to file if needed, otherwise print."""
        if output_file:
            try:
                with open(output_file, "w") as f:
                    f.write(text + "\n")
            except IOError as e:
                print(f"Error: {e}")
        else:
            print(text)

    # Handle the exit command
    if cmd == "exit":
        # exitval = 0 if len(inp) == 1 else int(inp[1]) if inp[1].isnumeric() else 0
        # exit(exitval)
        exit(int(tokens[1]) if len(tokens) > 1 and tokens[1].isdigit() else 0)

    # Handle the echo command
    elif cmd == "echo":
        handle_output(" ".join(tokens[1:]))
        return

    # Handle the type command
    elif cmd == "type":
        if len(tokens) > 1:
            outp = f"{tokens[1]}: not found"
            if tokens[1] in commands:
                outp = f"{tokens[1]} is {commands[tokens[1]]}"
            elif tokens[1] in builtins:
                outp = f"{tokens[1]} is a shell builtin"
            handle_output(outp)
        return
    
    # Handle the pwd command (built-in)
    elif cmd == "pwd":
        handle_output(os.getcwd())
        return
    
    # Handle the cd command
    elif cmd == "cd":
        if len(tokens) < 2:
            print("cd: missing operand") # No path provided
        else:
            new_dir = tokens[1]

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
        return
                
    # Handle external commands
    if cmd in commands:
         # os.system(" ".join(inp))
         # os.execvp(cmd, inp)
         try:
            if output_file:
                stdout_target = open(output_file, "w")
            else:
                stdout_target = sys.stdout

            if error_file:
                error_dir = os.path.dirname(error_file)
                if not os.path.exists(error_dir):
                    os.makedirs(error_dir)
                    
                stderr_target = open(error_file, "w")
            else:
                stderr_target = sys.stderr

            subprocess.run(tokens, stdout=stdout_target, stderr=stderr_target)

            if output_file:
                stdout_target.close()
            if error_file:
                stderr_target.close()
            
         except FileNotFoundError:
             print(f"{cmd}: command not found")

    # If the command is not found in builtins or PATH, report it
    else:
        print(f"{cmd}: command not found")
 
if __name__ == "__main__":
    while True:
        main()