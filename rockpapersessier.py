import random

def rock_paper_scissors():
    """Plays a game of Rock, Paper, Scissors against the computer."""
    print("Welcome to Rock, Paper, Scissors!")

    options = ['rock', 'paper', 'scissors']

    while True: # Loop to allow playing again
        user_choice = input("Choose rock, paper, or scissors (or 'quit' to stop): ").lower()

        if user_choice == 'quit':
            print("Thanks for playing!")
            break # Exit the loop

        if user_choice not in options:
            print("Invalid choice. Please choose rock, paper, or scissors.")
            continue # Ask for input again
        

        

        computer_choice = random.choice(options)
        print(f"\nYou chose: {user_choice}")
        print(f"Computer chose: {computer_choice}\n")

        # Determine the winner
        if user_choice == computer_choice:
            print("It's a tie!")
        elif (user_choice == 'rock' and computer_choice == 'scissors') or \
             (user_choice == 'scissors' and computer_choice == 'paper') or \
             (user_choice == 'paper' and computer_choice == 'rock'):
            print("You win!")
        else:
            print("Computer wins!")

        print("-" * 20) # Separator for the next round

# --- Run the game ---
# rock_paper_scissors()