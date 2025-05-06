import random
import time

def clear_screen():
    # This function creates some space to simulate clearing the screen
    print("\n" * 5)

def display_welcome():
    """Display welcome message and game instructions"""
    print("=" * 60)
    print("WELCOME TO THE ANIMAL QUIZ GAME!")
    print("=" * 60)
    print("\nTest your knowledge about the animal kingdom!")
    print("You have 3 chances to answer each question correctly.")
    print("Each correct answer earns you 1 point.")
    print("\nLet's see how much you know about animals!\n")
    input("Press Enter to start the quiz... ")
    clear_screen()

def get_player_name():
    """Get the player's name"""
    while True:
        name = input("\nPlease enter your name: ").strip()
        if name:
            return name
        print("Please enter a valid name.")

def ask_question(question, correct_answer, attempts=3):
    """Ask a question and check if the answer is correct"""
    print("\n" + question)
    
    for attempt in range(attempts):
        attempts_left = attempts - attempt
        if attempts_left < attempts:
            print(f"\nYou have {attempts_left} {'attempts' if attempts_left > 1 else 'attempt'} left.")
        
        answer = input("Your answer: ").strip().lower()
        
        if answer == correct_answer.lower():
            print("\n✅ Correct! Well done!")
            return True
        else:
            if attempts_left > 1:
                print("❌ That's not right. Try again!")
            else:
                print(f"\n❌ Sorry, that's not correct. The correct answer is '{correct_answer}'.")
    
    return False

def run_quiz():
    """Run the main quiz game"""
    # List of questions and answers
    questions = [
        ("What is the largest land animal?", "elephant"),
        ("Which bird can fly backwards?", "hummingbird"),
        ("What animal is known as the 'ship of the desert'?", "camel"),
        ("What is a group of lions called?", "pride"),
        ("Which animal has black and white stripes?", "zebra"),
        ("What is the fastest land animal?", "cheetah"),
        ("Which animal is known for its ability to change color?", "chameleon"),
        ("What is a baby kangaroo called?", "joey"),
        ("Which animal is known as the king of the jungle?", "lion"),
        ("What is the only mammal capable of true flight?", "bat"),
        ("What is the largest species of shark?", "whale shark"),
        ("Which animal is known for its long neck?", "giraffe"),
        ("What is the largest species of penguin?", "emperor penguin"),
        ("What animal is known for its intelligence and ability to use tools?", "octopus"),
        ("What animal is known for its ability to mimic human speech?", "parrot"),
        ("What is the only marsupial native to North America?", "opossum"),
        ("What animal is known for its long ears and strong hind legs?", "rabbit"),
        ("What animal is known for its ability to glide through the air?", "flying squirrel"),
        ("What animal is known for its ability to swim long distances?", "dolphin"),
        ("What animal is known for its ability to live in extreme conditions?", "tardigrade"),
        ("What animal is known for its ability to regenerate lost limbs?", "axolotl"),
        ("What animal is known for its ability to produce electricity?", "electric eel"),
        ("What animal is known for its ability to produce silk?", "silkworm")
    ]
    
    # Shuffle questions for a new experience each time
    random.shuffle(questions)
    
    # Number of questions to ask
    num_questions = min(5, len(questions))
    
    # Select questions for this round
    selected_questions = questions[:num_questions]
    
    player_name = get_player_name()
    display_welcome()
    
    print(f"\nAlright {player_name}, let's test your animal knowledge!")
    time.sleep(1)
    
    score = 0
    question_num = 1
    
    for question, answer in selected_questions:
        print(f"\nQuestion {question_num}/{num_questions}")
        if ask_question(question, answer):
            score += 1
        
        question_num += 1
        time.sleep(1)
    
    # Calculate percentage score
    percentage = (score / num_questions) * 100
    
    # Display final results
    clear_screen()
    print("=" * 60)
    print(f"QUIZ COMPLETED! Final Results for {player_name}")
    print("=" * 60)
    print(f"\nYou scored {score} out of {num_questions} ({percentage:.1f}%)")
    
    # Provide feedback based on score
    if percentage >= 80:
        print("\nExcellent job! You're an animal expert! 🏆")
    elif percentage >= 60:
        print("\nGood job! You know quite a bit about animals! 🎉")
    elif percentage >= 40:
        print("\nNot bad! You have some animal knowledge. 👍")
    else:
        print("\nKeep learning about animals! You'll do better next time. 📚")
    
    # Ask if player wants to play again
    play_again = input("\nWould you like to play again? (yes/no): ").strip().lower()
    return play_again in ["yes", "y"]

def main():
    """Main function to start the game"""
    while True:
        if not run_quiz():
            print("\nThank you for playing the Animal Quiz Game! Goodbye! 👋")
            break

if __name__ == "__main__":
    main()