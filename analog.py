import turtle
import time
import math

wn = turtle.Screen()
wn.bgcolor("white")
wn.setup(width=600, height=600)
wn.title("Analogue Clock")
wn.tracer(0)  

clock = turtle.Turtle()
clock.hideturtle()
clock.pensize(3)
clock.speed(0)

hour_hand = turtle.Turtle()
hour_hand.hideturtle()
hour_hand.pensize(6)
hour_hand.color("black")
hour_hand.speed(0)

minute_hand = turtle.Turtle()
minute_hand.hideturtle()
minute_hand.pensize(4)
minute_hand.color("blue")
minute_hand.speed(0)

second_hand = turtle.Turtle()
second_hand.hideturtle()
second_hand.pensize(2)
second_hand.color("red")
second_hand.speed(0)

def draw_clock_face():
    clock.penup()
    clock.goto(0, -210)
    clock.pendown()
    clock.pencolor("black")
    clock.fillcolor("white")
    clock.begin_fill()
    clock.circle(210)
    clock.end_fill()
    
    clock.penup()
    for i in range(12):
        angle = math.radians(i * 30)
        x = 190 * math.sin(angle)
        y = 190 * math.cos(angle)
        clock.goto(x, y)
        clock.setheading(90 - i * 30)
        clock.pendown()
        clock.forward(20)
        clock.penup()
    
    clock.goto(0, 0)
    clock.dot(10)

def draw_hour_hand(hour, minute):
    hour_hand.clear()
    hour_hand.penup()
    hour_hand.goto(0, 0)
    angle = math.radians(90 - ((hour % 12) * 30 + minute * 0.5))
    hour_hand.setheading(90 - ((hour % 12) * 30 + minute * 0.5))
    hour_hand.pendown()
    hour_hand.forward(100)
    hour_hand.penup()

def draw_minute_hand(minute):
    minute_hand.clear()
    minute_hand.penup()
    minute_hand.goto(0, 0)
    minute_hand.setheading(90 - minute * 6)
    minute_hand.pendown()
    minute_hand.forward(150)
    minute_hand.penup()

def draw_second_hand(second):
    second_hand.clear()
    second_hand.penup()
    second_hand.goto(0, 0)
    second_hand.setheading(90 - second * 6)
    second_hand.pendown()
    second_hand.forward(180)
    second_hand.penup()

def update_clock():
    # Get current time
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    second = current_time.tm_sec
    
    draw_hour_hand(hour, minute)
    draw_minute_hand(minute)
    draw_second_hand(second)
    
    wn.update()

draw_clock_face()

try:
    while True:
        update_clock()
        time.sleep(1)  
except:
    print("Clock closed")

wn.exitonclick()
