import random
import string
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

def generate_password(length, use_upper, use_lower, use_digits, use_symbols):
    """
    Generate a random password based on user preferences.
    
    Parameters:
      - length: The total length of the password.
      - use_upper: Boolean indicating inclusion of uppercase letters.
      - use_lower: Boolean indicating inclusion of lowercase letters.
      - use_digits: Boolean indicating inclusion of digits.
      - use_symbols: Boolean indicating inclusion of punctuation/symbols.
    
    Returns:
      A randomly generated password as a string.
    """
    characters = ""
    if use_upper:
        characters += string.ascii_uppercase
    if use_lower:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    if not characters:
        raise ValueError("At least one character set must be selected!")

    # Ensure that the password contains at least one character from each selected set
    password_chars = []
    if use_upper:
        password_chars.append(random.choice(string.ascii_uppercase))
    if use_lower:
        password_chars.append(random.choice(string.ascii_lowercase))
    if use_digits:
        password_chars.append(random.choice(string.digits))
    if use_symbols:
        password_chars.append(random.choice(string.punctuation))

    # Check if the specified length is enough to include the mandatory characters
    if length < len(password_chars):
        raise ValueError("Password length is too short for the selected options.")

    # Fill the rest of the password length with random choices
    remaining_length = length - len(password_chars)
    password_chars.extend(random.choices(characters, k=remaining_length))
    random.shuffle(password_chars)
    return ''.join(password_chars)

def main():
    print(Fore.CYAN + Style.BRIGHT + "\nWelcome to the Password Generator!\n")
    
    # Get the desired password length from the user
    try:
        length = int(input(Fore.WHITE + "Enter desired password length (minimum 4 recommended): "))
    except ValueError:
        print(Fore.RED + "Invalid input. Using default length of 12.")
        length = 12

    # Ask user which character sets to include
    use_upper = input(Fore.WHITE + "Include uppercase letters? (yes/no): ").strip().lower() in ("yes", "y")
    use_lower = input(Fore.WHITE + "Include lowercase letters? (yes/no): ").strip().lower() in ("yes", "y")
    use_digits = input(Fore.WHITE + "Include digits? (yes/no): ").strip().lower() in ("yes", "y")
    use_symbols = input(Fore.WHITE + "Include symbols? (yes/no): ").strip().lower() in ("yes", "y")

    try:
        password = generate_password(length, use_upper, use_lower, use_digits, use_symbols)
        print(Fore.GREEN + "\nGenerated Password: " + Style.BRIGHT + password + "\n")
    except ValueError as e:
        print(Fore.RED + "\nError:", e)

if __name__ == '__main__':
    main()
