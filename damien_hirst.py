#Day 18 of Udemy 100 Days of Code Challenge
import turtle as t
import random
# The Commented Portion is essentially How I extracted colours from a Hirst Spot Painting Image (.jpg/.png format)
    #import colorgram
    #color = colorgram.extract("hets.jpg", 30)
    # rgb_colors = []
    # for c in color:
    #     r = c.rgb.r
    #     g = c.rgb.g
    #     b = c.rgb.b
    #     rgx = (r,g,b)
    #     rgb_colors.append(rgx)

    # print(rgb_colors)

t.colormode(255)
timmy = t.Turtle()
timmy.speed("fast")
rgb_colors = [
    (198, 13, 32),
    (248, 236, 25),
    (40, 76, 188),
    (39, 216, 69),
    (238, 227, 5),
    (227, 159, 49),
    (29, 40, 154),
    (212, 76, 15),
    (17, 153, 17),
    (241, 36, 161),
    (195, 16, 12),
    (223, 21, 120),
    (68, 10, 31),
    (61, 15, 8),
    (223, 141, 206),
    (11, 97, 62),
    (219, 159, 11),
    (54, 209, 229),
    (19, 21, 49),
    (238, 157, 216),
    (79, 74, 212),
    (10, 228, 238),
    (73, 212, 168),
    (93, 233, 198),
    (65, 231, 239),
    (217, 88, 51)
]

timmy.setheading(225)
timmy.hideturtle()
timmy.penup()
timmy.forward(250)
timmy.setheading(0)
num_dot = 100

for dot_num in range(1, num_dot + 1):
    timmy.dot(20, random.choice(rgb_colors))
    timmy.forward(50)
    if dot_num % 10 == 0:
        timmy.left(90)
        timmy.forward(50)
        timmy.left(90)
        timmy.forward(500)
        timmy.right(180)

my_screen = t.Screen()
my_screen.exitonclick()