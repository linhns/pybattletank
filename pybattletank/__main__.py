import random


def init():
    return "init", random.randint(1, 10)


def processInput():
    while True:
        word = input("What is the magic number? ")
        if word == "quit":
            return None
        try:
            number = int(word)
            break
        except ValueError:
            print("Please type a number without decimals!")
            continue
    return number


def update(status, magic_number, player_number):
    if player_number is None:
        status = "end"
    elif player_number == magic_number:
        status = "win"
    elif magic_number < player_number:
        status = "lower"
    elif magic_number > player_number:
        status = "higher"
    return status, magic_number


def render(status, magic_number):
    if status == "win":
        print("This is correct! You win!")
    elif status == "end":
        print("Bye!")
    elif status == "lower":
        print("The magic number is lower")
    elif status == "higher":
        print("The magic number is higher")
    else:
        msg = f"Unexpected status: {status}"
        raise RuntimeError(msg)


def run():
    status, magic_number = init()
    while status not in ["win", "end"]:
        guess = processInput()
        status, magic_number = update(status, magic_number, guess)
        render(status, magic_number)


def main():
    run()


if __name__ == "__main__":
    main()
