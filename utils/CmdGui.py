from time import sleep
import os

def status_msg( string, newLine=False,sleepTime=1):
    print(string, end="", flush=True)
    sleep(sleepTime)
    print("\r", end="", flush=True)
    if newLine:
        print()

def menu( title, options, backmsg, margin=0):
    response = -1
    while response not in range(0, len(options)+1):
        clear()
        width = len(title)
        options_string = ""
        for option in options:
            if (width < (len(option)+4)):
                width = (len(option)+4)
        width += margin
        output = "╔"
        for i in range(width):
            output += "═"
        output += "╗\n║"
        offset = int(width / 2 - len(title) / 2)
        for i in range(offset):
            output += " "
        output += title
        for i in range(offset+len(title), width):
            output += " "
        output += "║\n╠"
        for i in range(width):
            output += "═"
        output += "╣\n"

        op_number = 1
        for option in options:
            output += "║"
            for i in range(int(margin/2)):
                output += " "
            output += f"({op_number}) {option}"
            op_number += 1
            for i in range(int(width - (margin/2 + len(option)+4))):
                output += " "
            output += "║\n"

        output += "║"
        for i in range(int(margin / 2)):
            output += " "
        output += f"(0) {backmsg}"
        for i in range(int(width - (margin/2 + len(backmsg)+4))):
            output += " "
        output += "║\n╚"
        for i in range(width):
            output += "═"
        output += "╝"
        print(output)
        try:
            if response not in range(0, len(options)+1) and response != -1:
                response = int(input("Invalid option enter a new one: "))
            else:
                response = int(input("Enter your option: "))
        except ValueError:
            response = -2

    return response

def progress( label, progress, afterLabel="", width=50):
    output = f"\r{label} ["
    bars = int((progress*width)/100)
    for i in range(bars):
        output += "■"
    for i in range(bars, width-1):
        output += " "
    output += f"] {afterLabel}"
    print(output, end="")

def clear():
    os.system('cls')

def pause():
    input("Press ENTER key to continue...")

def header(title, margin=0):
    width = len(title) + margin

    output = "╔"
    for i in range(width):
        output += "═"
    output += "╗\n║"
    offset = int(width / 2 - len(title) / 2)
    for i in range(offset):
        output += " "
    output += title
    for i in range(offset+len(title), width):
        output += " "
    output += "║\n╚"
    for i in range(width):
        output += "═"
    output += "╝"
    print(output)

