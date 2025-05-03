def simple_adventure():
    """A very basic text adventure game structure."""
    print("Welcome, brave adventurer!")
    print("You find yourself in a dark cave.")
    print("There are two passages: one LEFT and one RIGHT.")

    current_room = "cave"

    while True:
        if current_room == "cave":
            choice = input("Which way do you go? (LEFT/RIGHT): ").upper()
            if choice == "LEFT":
                print("\nYou walk down the left passage.")
                print("You see a glimmering treasure chest!")
                current_room = "treasure_room"
            elif choice == "RIGHT":
                print("\nYou walk down the right passage.")
                print("Oh no! A giant spider blocks your path.")
                current_room = "spider_room"
            else:
                print("Invalid direction. Try LEFT or RIGHT.")

        elif current_room == "treasure_room":
            print("You open the chest... It's full of gold! YOU WIN!")
            break # End the game

        elif current_room == "spider_room":
            action = input("What do you do? (FIGHT/FLEE): ").upper()
            if action == "FIGHT":
                print("\nThe spider is too strong! You lose.")
                break # End the game
            elif action == "FLEE":
                print("\nYou run back to the main cave.")
                current_room = "cave" # Go back to the previous room
            else:
                print("Invalid action. Try FIGHT or FLEE.")

        else:
            # Should not happen in this simple example, but good practice
            print("You seem to be lost in the void...")
            break

    print("\nGame Over. Thanks for playing!")

# --- Run the game ---
# simple_adventure()