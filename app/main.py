import sys
import os
import shlex
import subprocess
import readline

# track previous tab press state
previous_text = None
tab_press_count = 0

def get_executables():
    """Retrieve a list of executable commands from PATH"""
    executables = set()
    paths = os.getenv("PATH", "").split(":")

    for path in paths:
        if os.path.isdir(path):
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.access(full_path, os.X_OK) and not os.path.isdir(full_path):
                    executables.add(entry)
    return executables

def find_longest_common_prefix(options, text):
    """Find the longes common prefix among matching options"""
    if not options:
        return text
    prefix = options[0]
    for option in options[1:]:
        i = 0
        while i < len(prefix) and i < len(option) and prefix[i] == option[i]:
            i += 1
        prefix = prefix[:i]     # trim prefix to common match
    return prefix if prefix.startswith(text) else text

def completer(text, state):
    """Autocomplete built-in commands and executables"""
    global previous_text, tab_press_count
    builtins = {"exit", "echo", "type", "pwd", "cd"}

    executables = get_executables()
    options = sorted([cmd for cmd in builtins | executables if cmd.startswith(text)])

    if state == 0:
        if text == previous_text:
            tab_press_count += 1
        else:
            tab_press_count = 1     # reset count for new input
        previous_text = text    # store current input

        if len(options) > 1:
            common_prefix = find_longest_common_prefix(options, text)
            # if common prefix extends beyond user input, complete to it
            if common_prefix != text:
                return common_prefix
            
            if tab_press_count == 1:
                print("\a", end="", flush=True)     # ring bell for first <TAB>
                return None
            elif tab_press_count == 2:
                print("\n" + "  ".join(options))     # print matches on second<TAB>
                print(f"$ {text}", end="", flush=True)     # display prompt again
                tab_press_count = 0     # reset counter
                return None
            
    return options[state] + " " if state < len(options) else None


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
    
    # check for stdout/stderr redirection and append
    output_file = None
    error_file = None
    append_mode = False

    # redirect stdout
    if ">" in tokens or "1>" in tokens:
        try:
            redirect_index = tokens.index(">") if ">" in tokens else tokens.index("1>")
            output_file = tokens[redirect_index + 1]    # get the file to write to
            tokens = tokens[:redirect_index]    # remove redirection part from command
        except IndexError:
            print("Syntax error: missing output file")
            return
    
    # append stdout
    elif ">>" in tokens or "1>>" in tokens:
        try:
            redirect_index = tokens.index(">>") if ">>" in tokens else tokens.index("1>>")
            output_file = tokens[redirect_index + 1]
            append_mode = True
            tokens = tokens[:redirect_index]
        except IndexError:
            print("Syntax error: missing output file")
            return

    # redirect stderr
    if "2>" in tokens:
        try:
            redirect_index = tokens.index("2>")
            error_file = tokens[redirect_index + 1]
            tokens = tokens[:redirect_index]
        except IndexError:
            print("Syntax error: missing error file", file=sys.stderr)
            return
    
    # append stderr
    elif "2>>" in tokens:
        try:
            redirect_index = tokens.index("2>>")
            error_file = tokens[redirect_index + 1]
            append_mode = True
            tokens = tokens[:redirect_index]
        except IndexError:
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
    
    # Built-in commands
    def handle_output(text):
        """Redirect output to file if needed, otherwise print."""
        if output_file:
            try:
                # make sure directory exists before writing
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                # check if append mode is active
                mode = "a" if append_mode else "w"
                with open(output_file, mode) as f:
                    f.write(text + "\n")
            except IOError as e:
                print(f"Error: {e}", file=sys.stderr)
        else:
            print(text)

    def handle_error(error_text):
        """Redirect error output to file if needed, otherwise print to stderr"""
        if error_file:
            try:
                # make sure directory exists before writing
                os.makedirs(os.path.dirname(error_file), exist_ok=True)
                mode = "a" if append_mode else "w"
                with open(error_file, mode) as f:
                    f.write(error_text + "\n")
            except IOError as e:
                print(f"Error: {e}", file=sys.stderr)
        else:
            print(error_text, file=sys.stderr)

    # Handle the exit command
    if cmd == "exit":
        # exitval = 0 if len(inp) == 1 else int(inp[1]) if inp[1].isnumeric() else 0
        # exit(exitval)
        exit(int(tokens[1]) if len(tokens) > 1 and tokens[1].isdigit() else 0)

    # Handle the echo command
    elif cmd == "echo":
        message = " ".join(tokens[1:])

        if error_file:
            try:
                os.makedirs(os.path.dirname(error_file), exist_ok=True)
                open(error_file, "w").close()
            except IOError as e:
                print(f"Error: {e}", file=sys.stderr)

        handle_output(message)
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
            handle_error("cd: missing operand") # No path provided
        else:
            new_dir = tokens[1]

            # Home directory
            if new_dir == "~":
                new_dir = os.path.expanduser("~")

            if os.path.isabs(new_dir): # Ensure absolute path
                try:
                    os.chdir(new_dir)
                except FileNotFoundError:
                    handle_error(f"cd: {new_dir}: No such file or directory")
                except NotADirectoryError:
                    handle_error(f"cd: {new_dir}: Not a directory")
                except PermissionError:
                    handle_error(f"cd: {new_dir}: Permission denied")
            else:   # Relative Path
                try: # Join the relative path with the current working directory
                    os.chdir(os.path.join(os.getcwd(), new_dir))
                except FileNotFoundError:
                    handle_error(f"cd: {new_dir}: No such file or directory")
                except NotADirectoryError:
                    handle_error(f"cd: {new_dir}: Not a directory")
                except PermissionError:
                    handle_error(f"cd: {new_dir}: Permission denied")
        return
  
    # Handle external commands
    if cmd in commands:
        try:
            mode = "a" if append_mode else "w"
            out_f = open(output_file, mode) if output_file else None
            err_f = open(error_file, mode) if error_file else None
            
            subprocess.run(tokens, stdout=out_f if out_f else sys.stdout, stderr=err_f if err_f else sys.stderr, text=True)

            if out_f:
                out_f.close()
                return
            if err_f:
                err_f.close()
                return
        except FileNotFoundError:
            handle_error(f"{cmd}: command not found")
        return

    # If the command is not found in builtins or PATH, report it
    else:
        print(f"{cmd}: command not found")


if __name__ == "__main__":
    # set up readline for tab completion
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    while True:
        main()