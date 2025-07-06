import random
import string # To get the alphabet easily

# --- Game Assets ---

# List of words for the game
WORDS = [
    "python", "javascript", "coding", "developer", "terminal", "algorithm",
    "binary", "software", "hardware", "database", "network", "function",
    "variable", "debugger", "compiler", "interface", "programming"
]

# ASCII art stages for the hangman
# Index corresponds to the number of incorrect guesses (0 incorrect = stage 0)
HANGMAN_PICS = [
    # Stage 0: 6 lives remaining (start)
    '''
      +---+
      |   |
          |
          |
          |
          |
    =========
    ''',
    # Stage 1: 5 lives remaining
    '''
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    ''',
    # Stage 2: 4 lives remaining
    '''
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    ''',
    
    # Stage 3: 3 lives remaining
    '''
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    ''',
    # Stage 4: 2 lives remaining
    '''
      +---+
      |   |
      O   |
     /|\  |
          |
          |
    =========
    ''',
    # Stage 5: 1 life remaining
    '''
      +---+
      |   |
      O   |
     /|\  |
     /    |
          |
    =========
    ''',
    # Stage 6: 0 lives remaining (lose)
    '''
      +---+
      |   |
      O   |
     /|\  |
     / \  |
          |
    =========
    '''
]

# --- Helper Functions ---

def choose_word(word_list):
    """Selects a random word from the provided list."""
    return random.choice(word_list).lower()

def display_game_state(lives_remaining, letters_guessed, word_display):
    """Prints the current hangman stage, guessed letters, and word progress."""
    # Calculate index for HANGMAN_PICS (inverted: 0 lives = last pic)
    stage_index = len(HANGMAN_PICS) - 1 - lives_remaining
    print(HANGMAN_PICS[stage_index])
    print(f"Lives remaining: {lives_remaining}")
    print(f"Guessed letters: {' '.join(sorted(letters_guessed))}")
    print(f"Word: {word_display}\n")

# --- Main Game Logic ---

def play_hangman():
    """Runs a single round of Hangman."""
    secret_word = choose_word(WORDS)
    lives = 6
    letters_guessed = set() # Use a set for fast checking of previous guesses
    # Set of unique letters in the secret word (helps determine win condition)
    word_letters_set = set(secret_word)

    print("=" * 30)
    print(" Welcome to Hangman! ")
    print("=" * 30)
    print(f"The word has {len(secret_word)} letters.")

    # --- Game Loop ---
    while lives > 0 and len(word_letters_set) > 0:
        # Create the display string (e.g., "_ _ p h _ n")
        word_display_list = []
        for letter in secret_word:
            if letter in letters_guessed:
                word_display_list.append(letter)
            else:
                word_display_list.append("_")
        word_display = " ".join(word_display_list)

        # Show the current state
        display_game_state(lives, letters_guessed, word_display)

        # --- Get Player Input ---
        guess = input("Guess a letter: ").lower()

        # --- Validate Input ---
        if len(guess) != 1 or guess not in string.ascii_lowercase:
            print("Invalid input. Please enter a single letter.")
            continue # Ask for input again

        if guess in letters_guessed:
            print(f"You already guessed '{guess}'. Try again.")
            continue # Ask for input again

        # --- Process Guess ---
        letters_guessed.add(guess) # Add the valid guess to our set

        if guess in word_letters_set:
            print(f"Good guess! '{guess}' is in the word.")
            word_letters_set.remove(guess) # Remove the correctly guessed letter
        else:
            print(f"Sorry, '{guess}' is not in the word.")
            lives -= 1

        print("-" * 20) # Separator between turns

    # --- End of Game ---
    if lives == 0:
        # Player lost - show final state
        display_game_state(lives, letters_guessed, " ".join(secret_word)) # Show the full word
        print("\nYOU LOST! ☠️")
        print(f"The word was: {secret_word}")
    else: # len(word_letters_set) must be 0
        # Player won - show final state (word will be fully revealed)
        word_display = " ".join(secret_word)
        display_game_state(lives, letters_guessed, word_display)
        print("\nCONGRATULATIONS! YOU WON! 🎉")
        print(f"You guessed the word: {secret_word}")

# --- Start the Game ---
if __name__ == "__main__":
    while True:
        play_hangman()
        play_again = input("\nDo you want to play again? (yes/no): ").lower()
        if not play_again.startswith('y'):
            print("Thanks for playing!")
            break
        print("\nStarting new game...\n")