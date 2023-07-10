from biosim import World

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--years", type=int, default=500)
    args = parser.parse_args()
    print(args)
    World().start(args.years)
