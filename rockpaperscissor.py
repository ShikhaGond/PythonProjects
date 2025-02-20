import random

def get_computer_choice():
    """Randomly select the computer's move."""
    choices = ['rock', 'paper', 'scissors']
    return random.choice(choices)

def determine_winner(user_choice, computer_choice):
    """Determine the outcome of the game."""
    if user_choice == computer_choice:
        return "It's a tie!"
    elif (user_choice == 'rock' and computer_choice == 'scissors') or \
         (user_choice == 'paper' and computer_choice == 'rock') or \
         (user_choice == 'scissors' and computer_choice == 'paper'):
        return "You win!"
    else:
        return "Computer wins!"

def play_game():
    """Main game loop."""
    print("Welcome to Rock, Paper, Scissors!")
    while True:
        user_input = input("Choose rock, paper, or scissors (or type 'quit' to exit): ").lower()
        if user_input == 'quit':
            print("Thanks for playing!")
            break
        if user_input not in ['rock', 'paper', 'scissors']:
            print("Invalid input. Please try again.\n")
            continue

        computer_choice = get_computer_choice()
        print(f"Computer chose: {computer_choice}")
        result = determine_winner(user_input, computer_choice)
        print(result + "\n")

if __name__ == '__main__':
    play_game()
