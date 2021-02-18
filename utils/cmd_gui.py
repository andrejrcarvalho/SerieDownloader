from time import sleep
import os,sys

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
        for i in range(len(options)):
            opt_len = len(f"({i+1})\t{options[i]}".expandtabs())
            if (width < opt_len):
                width = opt_len
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
            opt_string = f"({op_number})\t{option}".expandtabs()
            output += opt_string
            op_number += 1
            for i in range(int(width - (margin/2 + len(opt_string)))):
                output += " "
            output += "║\n"

        output += "║"
        for i in range(int(margin / 2)):
            output += " "
        exit_string = f"(0)\t{backmsg}".expandtabs()
        output += exit_string
        for i in range(int(width - (margin/2 + len(exit_string)))):
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
    if (sys.platform.startswith("linux")):
        os.system('clear')
    else:
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

