def main() -> int:
    x: int   = 0
    while x < 100:
        if x % 5 == 0 and x % 3 == 0:
            print("Fizzbuzz\n")
        elif x % 3 == 0:
            print("Fizz\n")
        elif x % 5 == 0:
            print("Buzz\n")
        else:
            print("%d\n", x)
        x += 1