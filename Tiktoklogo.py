import turtle

# Set up the screen
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("TikTok Inspired Logo")

# Set up the turtle
pen = turtle.Turtle()
pen.speed(10)
pen.width(3)
pen.hideturtle()

# Function to draw a circle with gradient effect
def draw_circle(color, radius, x, y):
    pen.penup()
    pen.goto(x, y - radius)
    pen.pendown()
    pen.color(color)
    pen.begin_fill()
    pen.circle(radius)
    pen.end_fill()

# Draw circles inspired by the TikTok logo colors
draw_circle("deepskyblue", 100, 0, 100)
draw_circle("hotpink", 80, -20, 120)
draw_circle("white", 60, 20, 80)

# Add your own creative twist here!

# Keep the window open
screen.mainloop()