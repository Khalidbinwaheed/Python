import turtle
import random

# Set up the screen
screen = turtle.Screen()
screen.bgcolor("black")

# Create turtle
star = turtle.Turtle()
star.speed(0)
star.hideturtle()

colors = ["red", "yellow", "blue", "green", "purple", "orange", "cyan", "magenta"]

def draw_star(size):
    for i in range(5):
        star.color(random.choice(colors))
        star.forward(size)
        star.right(144)

star.penup()
star.goto(0, -100)
star.pendown()

for i in range(5):
    draw_star(200 - i*30)
    star.right(72)

turtle.done()