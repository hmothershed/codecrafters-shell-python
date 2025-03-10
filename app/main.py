import sys
import shutil

builtin_cmds = {}

def command(func):
    builtin_cmds[func.__name__.split("_")[1]] = func
    return func

@command
def shell_exit(args):
    exit(int(args[0]))

@command
def shell_echo(args):
    sys.stdout.write(" ".join(args) + "\n")

@command
def shell_type(args):
    if args[0] in builtin_cmds:
        sys.stdout.write(f"{args[0]} is a shell builtin\n")
    elif path := shutil.which(args[0]):
        sys.stdout.write(f"{args[0]} is {path}\n")
    else:
        sys.stdout.write(f"{args[0]}: not found\n")

def main():
    while True:
        sys.stdout.write("$ ")
        command = input("")
        cmd, *args = command.split()
        if cmd in builtin_cmds:
            builtin_cmds[cmd](args)
        else:
            sys.stdout.write(f"{cmd}: command not found\n")
    return


if __name__ == "__main__":
    main()
