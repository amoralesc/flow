import os, argparse, sys

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from components.grid import Grid as Grid
from components.solver import Solver as Solver
from components import eventmanager, model, controller, view
from utils import config, utils


def main(args):
    try:
        levels = utils.load_grid_config(os.path.join(config.DATA_DIR, "levels.json"))
    except Exception as e:
        print(e)
        sys.exit(1)

    grid_config = None
    if args.file:
        try:
            grid_config = utils.load_grid_config(args.file)
        except Exception as e:
            print(e)
            sys.exit(1)
    elif args.level:
        if args.level < 1 or args.level > len(levels):
            print("Level not found, please choose a level between 1 and", len(levels))
            sys.exit(1)
        grid_config = levels[args.level - 1]
    elif args.random:
        if args.rows and args.cols and args.points:
            try:
                grid_config = Grid.create_random_config(
                    args.rows, args.cols, args.points
                )
            except Exception as e:
                print("Can't create random grid:", e)
                sys.exit(1)
        else:
            print("Random grid needs rows, cols and points")
            sys.exit(1)

    grid = Grid.from_config(grid_config)
    print("Loaded configuration correctly\n")

    if args.solve:
        solver = Solver(grid)
        print("The solver is looking for a solution, this might take a while...\n")
        found_solution = solver.solve(args.debug)
        if found_solution:
            print("The solver found a solution!\n")
        else:
            print("The solver couldn't find a solution...\n")
            grid.restart()

    event_manager = eventmanager.EventManager()
    gamemodel = model.GameEngine(event_manager, grid)
    gamecontroller = controller.GameController(event_manager, gamemodel)
    gameview = view.GameView(event_manager, gamemodel)
    gamemodel.run()


if __name__ == "__main__":
    # Args parser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s",
        "--solve",
        help="attempt to solve the grid",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="debug mode (prints the solver actions)",
        action="store_true",
        default=False,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="path to a grid config file", type=str)
    group.add_argument("-l", "--level", help="level number of default levels", type=int)
    group.add_argument(
        "-r",
        "--random",
        help="randomize a grid. If used, the next args should be: rows, cols, points",
        action="store_true",
    )
    parser.add_argument(
        "rows", help="number of rows of the random grid", type=int, nargs="?"
    )
    parser.add_argument(
        "cols", help="number of cols of the random grid", type=int, nargs="?"
    )
    parser.add_argument(
        "points", help="quantity of points of the random grid", type=int, nargs="?"
    )

    args = parser.parse_args()
    main(args)
