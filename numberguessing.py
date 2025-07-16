import random

def number_guessing_game():
    """Plays a simple number guessing game."""
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")

    secret_number = random.randint(1, 100)
    attempts = 0
    max_attempts = 10 # You can change this for difficulty

    while attempts < max_attempts:
        try:
            guess = int(input(f"Attempt {attempts + 1}/{max_attempts}. Enter your guess: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue # Skip the rest of this loop iteration

            
        attempts += 1

        if guess < secret_number:
            print("Too low!")
        elif guess > secret_number:
            print("Too high!")
        else:
            print(f"Congratulations! You guessed the number {secret_number} in {attempts} attempts!")
            return # Exit the function on success

    # If the loop finishes without guessing correctly
    print(f"Sorry, you've run out of attempts. The number was {secret_number}.")

# --- Run the game ---
# number_guessing_game()