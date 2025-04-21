import turtle
import random

# --- Configuration ---
INITIAL_TRUNK_LENGTH = 100  # Pixels for the main trunk
MIN_BRANCH_LENGTH = 7      # Stop drawing branches smaller than this
ANGLE_BASE = 25            # Base angle for branching (degrees)
ANGLE_VARIATION = 10       # How much the angle can randomly vary
LENGTH_REDUCTION = 0.75    # Factor to shorten the next branch (e.g., 0.75 means 75% of current length)
INITIAL_PEN_WIDTH = 10     # Starting thickness of the trunk
LEAF_SIZE = 5              # Size of the leaf dots
TRUNK_COLOR = "#5C3A21"     # A brown color for the trunk/branches
LEAF_COLOR = "#2E8B57"      # SeaGreen for the leaves
BACKGROUND_COLOR = "skyblue"

# --- Recursive Tree Function ---
def draw_tree(t, branch_len, angle_base, angle_variation, length_reduction, min_len, pen_width):
    """
    Recursively draws a branch of the tree.

    Args:
        t: The turtle object.
        branch_len: The length of the current branch segment.
        angle_base: The base angle for splitting.
        angle_variation: Random variation added/subtracted from the base angle.
        length_reduction: Factor by which to reduce length for sub-branches.
        min_len: The minimum length for a branch to be drawn.
        pen_width: The initial pen width (used for scaling).
    """
    # --- Base Case: Branch is too short, draw a 'leaf' ---
    if branch_len < min_len:
        original_color = t.pencolor() # Remember current color
        t.pencolor(LEAF_COLOR)
        t.dot(LEAF_SIZE)
        t.pencolor(original_color) # Restore color
        return # Stop recursion for this branch

    # --- Draw the current branch segment ---
    # Set pen size - make branches thinner as they get shorter
    current_pen_width = max(1, int(pen_width * (branch_len / INITIAL_TRUNK_LENGTH)))
    t.pensize(current_pen_width)
    t.pencolor(TRUNK_COLOR)

    t.forward(branch_len)

    # --- Recursive Step: Draw two smaller branches ---
    # Store current position and heading before branching
    current_pos = t.position()
    current_heading = t.heading()

    # Calculate random angles for the two sub-branches
    angle1 = angle_base + random.uniform(-angle_variation, angle_variation)
    angle2 = angle_base + random.uniform(-angle_variation, angle_variation)
    next_len = branch_len * length_reduction

    # == Draw Right Branch ==
    t.right(angle1)
    draw_tree(t, next_len, angle_base, angle_variation, length_reduction, min_len, pen_width)

    # == Draw Left Branch ==
    # Return turtle to the fork point and heading *before* drawing the left branch
    t.penup()
    t.goto(current_pos)
    t.setheading(current_heading)
    t.pendown()

    t.left(angle2)
    draw_tree(t, next_len, angle_base, angle_variation, length_reduction, min_len, pen_width)

    # == Return to Parent Branch Start ==
    # Go back to the fork point *after* drawing both branches
    t.penup()
    t.goto(current_pos)
    t.setheading(current_heading)
    # Move turtle back down the segment *it just drew* to position it correctly for the calling function
    # Set pen size and color again in case they were changed by leaf drawing
    t.pensize(current_pen_width)
    t.pencolor(TRUNK_COLOR)
    t.backward(branch_len)
    # Keep pen up, the caller will handle pen down if needed


# --- Main Execution ---
if __name__ == "__main__":
    # Setup Screen
    screen = turtle.Screen()
    screen.setup(width=800, height=600)
    screen.bgcolor(BACKGROUND_COLOR)
    screen.title("Recursive Tree with Turtle")
    screen.tracer(0) # Turn off screen updates for faster drawing

    # Setup Turtle
    my_turtle = turtle.Turtle()
    my_turtle.hideturtle() # Make the turtle icon invisible
    my_turtle.penup()
    # Position the turtle at the bottom center
    my_turtle.goto(0, -screen.window_height() // 2.5)
    my_turtle.pendown()
    my_turtle.setheading(90) # Point the turtle straight up
    my_turtle.pencolor(TRUNK_COLOR)
    my_turtle.pensize(INITIAL_PEN_WIDTH)

    # Start Drawing the Tree
    print("Drawing tree... please wait.")
    draw_tree(my_turtle,
              INITIAL_TRUNK_LENGTH,
              ANGLE_BASE,
              ANGLE_VARIATION,
              LENGTH_REDUCTION,
              MIN_BRANCH_LENGTH,
              INITIAL_PEN_WIDTH)
    print("Drawing complete!")

    # Update the screen to show the final drawing
    screen.update()

    # Keep the window open until clicked
    screen.exitonclick()