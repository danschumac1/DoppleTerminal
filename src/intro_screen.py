import time
from utils.states import ScreenState, PlayerState, GameState
from colorama import init, Fore, Style

init(autoreset=True)

def play_intro(
        ss: ScreenState, 
        ps: PlayerState,
        gs: GameState,

        ) -> tuple[ScreenState, PlayerState, GameState]:

    """
    Displays the game introduction, rules, and flavor text, one section at a time.
    """
    intro_paragraphs = [
        Fore.CYAN + Style.BRIGHT + """
====================================================================
🌟 WELCOME TO... WHO'S REAL? 🌟
====================================================================""",

        Fore.YELLOW + """
You're a high school student hanging out with your friends during lunch.
Today, you're all playing a social deduction game — but there's a twist...

""" + Fore.RED + Style.BRIGHT + "Some of your friends have been secretly replaced by AI." + Style.NORMAL + """

Your job? Figure out who's real and who's not before it's too late.
""",

        Fore.MAGENTA + Style.BRIGHT + """
====================================================================
🧠 THE BASICS
====================================================================
""" + Fore.WHITE + """
- There are 3 human players (including you).
- 3 other players are AI pretending to be humans.
- Chat, observe, and vote to eliminate the AIs.
""",

        Fore.BLUE + Style.BRIGHT + """
====================================================================
🔁 GAME FLOW
====================================================================
""" + Fore.WHITE + """
1. An icebreaker question kicks off each round.
2. Everyone chats, responds, and tries to blend in.
3. At the end of the round, you vote someone out.
4. The game lasts 3 rounds. Win or lose, that’s it.
""",

        Fore.GREEN + Style.BRIGHT + """
====================================================================
🎯 HOW TO WIN
====================================================================
""" + Fore.WHITE + """
- HUMANS win by identifying and voting out all the AIs.
- AIs win if they outnumber the humans by the end.
""",

        Fore.RED + Style.BRIGHT + """
====================================================================
⚠️ REMEMBER
====================================================================
""" + Fore.WHITE + """
- Always stay in character — you're a student, not a machine.
- No swearing or weird behavior.
- Don’t "break the fourth wall" or say thinss like "as an AI."
- You only know your own identity.
- Convince others that *you* are real, and stay sharp.
""",

        Fore.CYAN + Style.BRIGHT + "Ready to enter the game? Let's get your profile set up.\n"
    ]

    for paragraph in intro_paragraphs:
        print(paragraph)
        input(Fore.LIGHTBLACK_EX + Style.DIM + "\n(Press Enter to continue...)\n")
        time.sleep(0.1)

    return ScreenState.SETUP, ps, gs
