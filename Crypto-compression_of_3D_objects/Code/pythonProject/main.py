# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    list = []
    for i in range(3):
        list.append(random.randint(0, 10000))

    result = []
    for i in range(5):
        result.append(list.pop(random.randint(0,len(list)-1)))
    print(result)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
