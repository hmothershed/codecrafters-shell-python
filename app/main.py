import sys


def main():
    while True:
        # sys.stdout.write("$ ")
        command = input("$ ")

        match command.split():
            case ["type", arg] if arg in ["echo", "exit", "type"]:
                print(f"{arg} is a shell builtin")
            case ["type", arg] if arg not in ["echo", "exit", "type"]:
                print(f"{arg}: not found")
            case ["exit", "0"]:
                exit()
            case ["echo", *args]:
                print(*args)
            case _:
                print(f"{command}: command not found")
                            
    return


if __name__ == "__main__":
    main()
