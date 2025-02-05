import random
import time
from colorama import init, Fore, Style

class LuckWisher:
    MOTIVATIONAL_QUOTES = [
        "Believe in yourself and all that you are.",
        "Success is where preparation and opportunity meet.",
        "Every great dream begins with a dreamer.",
        "Your potential is limitless!",
        "Courage is not the absence of fear, but moving forward despite it."
        "{name}, your dreams are the blueprint of your destiny.",
        "Every challenge you face is just another stepping stone, {name}.",
        "{name}, success is not about perfection, it's about progress.",
        "Your potential has no limits, {name} - believe in yourself.",
        "{name}, the only impossible journey is the one you never start."
        "{name}, setbacks are just setups for spectacular comebacks.",
        "Resilience is your superpower, {name}.",
        "{name}, diamonds are formed under pressure - and so are you.",
        "Every obstacle is an opportunity in disguise, {name}.",
        "{name}, your resilience writes a story more powerful than any challenge."
        "{name}, courage isn't the absence of fear, but action despite it.",
        "Brave hearts like yours, {name}, change the world.",
        "Fear is temporary, {name}. Your determination is permanent.",
        "{name}, sometimes the bravest thing is believing in yourself.",
        "Your strength isn't measured by never falling, but by rising each time, {name}."
    ]

    GOOD_LUCK_MESSAGES = [
        "Sending positive vibes your way!",
        "You've got this! Believe in yourself.",
        "Wishing you success and happiness!",
        "May luck and hard work be your companions.",
        "Your journey is about to get amazing!"
        "{name}, growth happens outside your comfort zone.",
        "Your journey of self-improvement is your greatest adventure, {name}.",
        "{name}, personal growth is the best investment you'll ever make.",
        "Each day is a new chance to become a better version of yourself, {name}.",
        "{name}, your potential is like a seed - it grows with care and dedication."
    ]

    def __init__(self, name):
        init(autoreset=True)  # Initializing colorama for colored output
        self.name = name

    def generate_luck_wish(self):
        """Personalized and Motivational luck wish."""
        quote = random.choice(self.MOTIVATIONAL_QUOTES)
        message = random.choice(self.GOOD_LUCK_MESSAGES)

        print(Fore.CYAN + f"🌟 Luck Wish for {self.name} 🌟")
        print(Fore.GREEN + quote)
        print(Fore.YELLOW + message)

    def create_luck_ceremony(self):
        """Are you ready for a dramatic luck-wishing ceremony."""
        print(Fore.MAGENTA + f"\nPreparing a special luck ceremony for {self.name}...")

        for _ in range(1):
            print(Fore.BLUE + "✨ Charging luck energy... ✨")
            print(Fore.GREEN + "🪄 Shring Brhing Sravaling... 🪄")
            print(Fore.CYAN + "💫 Bhooth Bhavisya Vartamaan Badling... 💫")
            time.sleep(0.5)

        self.generate_luck_wish()

        print(Fore.RED + "\nLuck activated! Go conquer the world! 💪")

def main():
    print(Fore.MAGENTA + "Are you ready to experience the power of luck?")
    name = input(Fore.CYAN + "Here's my wishes for you, but do you want it? Please say yes 🥹 enter any of your nicknames 😉")

    luck_wisher = LuckWisher(name)
    luck_wisher.create_luck_ceremony()

if __name__ == "__main__":
    main()
