import random
from colorama import init, Fore, Style

# Initializing colorama
init(autoreset=True)

def scramble_word(word):
    """Scrambles the letters of the word."""
    word_letters = list(word)
    random.shuffle(word_letters)
    scrambled = ''.join(word_letters)
    # Ensuring that the scrambled word isn't the same as the original
    while scrambled == word:
        random.shuffle(word_letters)
        scrambled = ''.join(word_letters)
    return scrambled

def select_level():
    """Allows the user to select a difficulty level."""
    levels = {
        "easy": ["cat", "dog", "bird", "tree", "moon", "star"],
        "medium": ["python", "orange", "banana", "school", "planet", "guitar"],
        "hard": ["programming", "algorithm", "encyclopedia", "microprocessor", "metamorphosis"]
    }
    
    while True:
        print(Fore.YELLOW + "\nChoose a difficulty level:")
        print(Fore.YELLOW + "1. Easy\n2. Medium\n3. Hard")
        level_input = input(Fore.WHITE + "Enter your choice (easy/medium/hard): ").strip().lower()
        if level_input in levels:
            return level_input, levels[level_input]
        else:
            print(Fore.RED + "Invalid choice. Please select from Easy, Medium, or Hard.")

def play_game():
    """Runs one round of the word puzzle game."""
    # Header
    print(Fore.CYAN + "\n*************************************")
    print(Fore.GREEN + "         Word Puzzle Game!")
    print(Fore.CYAN + "*************************************\n")
    
    # Selecting difficulty level and word list based on user choice
    level, word_list = select_level()
    
    # Choosing and scrambling a random word from the chosen level
    word = random.choice(word_list)
    scrambled = scramble_word(word)
    
    print(Fore.MAGENTA + f"\nUnscramble the letters to form a valid word. (Level: {level.title()})")
    print(Fore.BLUE + f"Scrambled word: {Style.BRIGHT}{scrambled}\n")
    
    guess = input(Fore.WHITE + "Your guess: ").strip().lower()
    
    if guess == word:
        print(Fore.GREEN + "\nCongratulations! You guessed it right!")
    else:
        print(Fore.RED + f"\nSorry, the correct word was '{word}'.")

def main():
    """Main function to run the game loop."""
    while True:
        play_game()
        again = input(Fore.WHITE + "\nDo you want to play again? (yes/no): ").strip().lower()
        if again != "yes":
            print(Fore.CYAN + "\nThank you for playing! Goodbye!\n")
            break

if __name__ == "__main__":
    main()
