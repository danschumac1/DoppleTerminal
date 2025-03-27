from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.shortcuts import print_formatted_text

def main():
    print_formatted_text(ANSI("\x1b[33m=== Welcome to the Game ===\x1b[0m"))  # Yellow
    print_formatted_text(ANSI("\x1b[34mMario\x1b[0m: Hey there!"))  # Blue
    print_formatted_text(ANSI("\x1b[35mLuigi\x1b[0m: Let's-a go!"))  # Magenta

    user_color = "\x1b[32m"  # Green
    user_name = "You"

    while True:
        user_input = prompt(ANSI(f"{user_color}{user_name}\x1b[0m: "))
        if user_input.strip().lower() == "exit":
            break
        print_formatted_text(ANSI(f"{user_color}{user_name}\x1b[0m: {user_input}"))

if __name__ == "__main__":
    main()
