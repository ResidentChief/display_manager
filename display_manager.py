#!/usr/bin/python

# This script allows users to access Display Manager through the command line.

import sys
import os
import argparse
import pickle
import display_manager_lib as dm


class CommandSyntaxError(Exception):
    pass


def showHelp(command=None):
    """
    :param command: The command to print information for.
    """
    print("Display Manager, version 1.0.0")

    usage = {"help": "\n".join([
        "usage: display_manager.py {{ help | set | show | brightness | rotate | mirror | underscan }}",
        "",
        "Use any of the commands with \"help\" to get more information:",
        "    help       Show this help information.",
        "    set        Set the display configuration.",
        "    show       Show available display configurations.",
        "    brightness Show or set the current display brightness.",
        "    rotate     Show or set display rotation.",
        "    mirror     Set mirroring configuration.",
        "    underscan  Show or set the current display underscan.",
    ]), "set": "\n".join([
        "usage: display_manager.py set {{ help | closest | highest | exact }}",
        "    [-d display] [-w width] [-h height] [-d pixel depth] [-r refresh]",
        "    [--no-hidpi] [--only-hidpi]",
        "",
        "commands",
        "    help       Print this help information.",
        "    closest    Set the display settings to the supported resolution that is closest to the specified values.",
        "    highest    Set the display settings to the highest supported resolution.",
        "    exact      Set the display settings to the specified values if they are supported. If they are not, "
        "don\'t change the display.",
        "",
        "OPTIONS",
        "    -w width           Resolution width.",
        "    -h height          Resolution height.",
        "    -p pixel-depth     Pixel color depth (default: 32).",
        "    -r refresh         Refresh rate (default: 0).",
        "    -d display         Specify a particular display (default: main display).",
        "    --no-hidpi         Don\'t show HiDPI settings.",
        "    --only-hidpi       Only show HiDPI settings.",
    ]), "show": "\n".join([
        "usage: display_manager.py show {{ help | all | closest | highest | current | displays }}",
        "    [-d display] [-w width] [-h height] [-d pixel depth] [-r refresh]",
        "    [--no-hidpi] [--only-hidpi]",
        "",
        "commands",
        "    help       Print this help information.",
        "    all        Show all supported resolutions for the display.",
        "    closest    Show the closest matching supported resolution to the specified values.",
        "    highest    Show the highest supported resolution.",
        "    current    Show the current display configuration.",
        "    displays   List the current displays and their IDs.",
        "",
        "OPTIONS",
        "    -w width           Resolution width.",
        "    -h height          Resolution height.",
        "    -p pixel-depth     Pixel color depth (default: 32).",
        "    -r refresh         Refresh rate (default: 0).",
        "    -d display         Specify a particular display (default: main display).",
        "    --no-hidpi         Don\'t show HiDPI settings.",
        "    --only-hidpi       Only show HiDPI settings.",
        "",
    ]), "brightness": "\n".join([
        "usage: display_manager.py brightness {{ help | show | set [val] }}",
        "    [-d display]",
        "",
        "commands",
        "    help       Print this help information.",
        "    show       Show the current brightness setting(s).",
        "    set [val]  Sets the brightness to the given value. Must be between 0 and 1.",
        "",
        "OPTIONS",
        "    -d display         Specify a particular display (default: main display).",
    ]), "rotate": "\n".join([
        "usage: display_manager.py rotate {{ help | show | set [val] }}",
        "    [-d display]",
        "commands",
        "    help       Print this help information.",
        "    show       Show the current display rotation.",
        "    set [val]  Set the rotation to the given angle (in degrees). Must be a multiple of 90.",
        "",
        "OPTIONS",
        "    -d display         Specify a particular display (default: main display).",
    ]), "underscan": "\n".join([
        "usage: display_manager.py underscan {{ help | show | set [val] }}",
        "    [-d display]",
        "",
        "commands",
        "    help       Print this help information.",
        "    show       Show the current underscan setting(s).",
        "    set [val]  Sets the underscan to the given value. Must be between 0 and 1.",
        "OPTIONS",
        "    -d display         Specify a particular display (default: main display).",
    ]), "mirror": "\n".join([
        "usage: display_manager.py mirror {{ help | set | disable }}",
        "    [-d display] [-m display]",
        "",
        "commands",
        "    help       Print this help information.",
        "    set        Activate mirroring.",
        "    disable    Deactivate all mirroring.",
        "",
        "OPTIONS",
        "    -d display         Change mirroring settings for \"display\" (default: main display).",
        "    -m display         Set the display to mirror \"display\".",
    ])}

    if command in usage:
        print(usage[command])
    else:
        print(usage["help"])


def parse(parseList):
    """
    Parse the user command-line input.
    :return: A parser that has parsed all command-line arguments passed in.
    """
    parser = argparse.ArgumentParser(add_help=False)
    primary = parser.add_subparsers(dest="primary")

    pSet = primary.add_parser("set", add_help=False)
    pSet.add_argument(
        "secondary",
        choices=["help", "closest", "highest", "exact"],
        nargs="?",
        default="closest"
    )

    pShow = primary.add_parser("show", add_help=False)
    pShow.add_argument(
        "secondary",
        choices=["help", "all", "closest", "highest", "current", "displays"],
        nargs="?",
        default="all"
    )

    for p in [pSet, pShow]:
        p.add_argument("-w", "--width", type=int)
        p.add_argument("-h", "--height", type=int)
        p.add_argument("-p", "--pixel-depth", type=float, default=32)
        p.add_argument("-r", "--refresh", type=float, default=0)
        p.add_argument("--no-hidpi", action="store_true")
        p.add_argument("--only-hidpi", action="store_true")

    pBrightness = primary.add_parser("brightness", add_help=False)
    pBrightness.add_argument("secondary", choices=["help", "show", "set"])
    pBrightness.add_argument("brightness", type=float, nargs="?", default=1)

    pRotate = primary.add_parser("rotate", add_help=False)
    pRotate.add_argument("secondary", choices=["help", "set", "show"], nargs="?", default="show")
    pRotate.add_argument("rotation", type=int, nargs="?", default=0)

    pMirror = primary.add_parser("mirror", add_help=False)
    pMirror.add_argument("secondary", choices=["help", "set", "disable"])
    pMirror.add_argument("-m", "--mirror", type=int)

    pUnderscan = primary.add_parser("underscan", add_help=False)
    pUnderscan.add_argument("secondary", choices=["help", "show", "set"])
    pUnderscan.add_argument("underscan", type=float, nargs="?", default=1)

    for p in [pSet, pShow, pBrightness, pRotate, pMirror, pUnderscan]:
        p.add_argument("-d", "--display", type=int, default=dm.getMainDisplay().displayID)

    pHelp = primary.add_parser("help", add_help=False)
    pHelp.add_argument(
        "secondary",
        choices=["set", "show", "brightness", "rotate", "underscan", "mirror"],
        nargs="?",
        default=None
    )

    # argparse shows its own error message and exits when there's been a parsing error.
    # We want to show our error, and not theirs. Hence:
    try:
        with open(os.devnull, "w") as nowhere:
            sys.stderr = nowhere
            sys.stdout = nowhere
            args = parser.parse_args(parseList)
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__
    except SystemExit:
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__
        raise CommandSyntaxError
    return args


def getCommand(commandString):
    """
    Transforms input string into a Command.
    :returns: The resulting Command.
    """
    if commandString == "":
        return None

    parseList = []
    for element in commandString.split():
        parseList.append(element)
    args = parse(parseList)

    if args.primary == "help":  # run help (default)
        showHelp(command=args.secondary)
        sys.exit(0)

    if args.secondary == "help" or hasattr(args, "help"):  # secondary-specific help
        showHelp(command=args.primary)
        sys.exit(0)

    def hidpi():
        hidpiVal = 0  # show all modes (default)
        if args.only_hidpi or args.no_hidpi:
            if not (args.only_hidpi and args.no_hidpi):  # If they didn't give contrary instructions, proceed.
                if args.no_hidpi:
                    hidpiVal = 1  # do not show HiDPI modes
                elif args.only_hidpi:
                    hidpiVal = 2  # show only HiDPI modes
        return hidpiVal

    command = None
    if args.primary == "set":
        command = dm.Command(
            args.primary,
            args.secondary,
            width=args.width,
            height=args.height,
            depth=args.pixel_depth,
            refresh=args.refresh,
            displayID=args.display,
            hidpi=hidpi()
        )
    elif args.primary == "show":
        command = dm.Command(
            args.primary,
            args.secondary,
            width=args.width,
            height=args.height,
            depth=args.pixel_depth,
            refresh=args.refresh,
            displayID=args.display,
            hidpi=hidpi()
        )
    elif args.primary == "brightness":
        command = dm.Command(
            args.primary,
            args.secondary,
            brightness=args.brightness,
            displayID=args.display
        )
    elif args.primary == "rotate":
        command = dm.Command(
            args.primary,
            args.secondary,
            angle=args.rotation,
            displayID=args.display
        )
    elif args.primary == "mirror":
        command = dm.Command(
            args.primary,
            args.secondary,
            mirrorDisplayID=args.mirror,
            displayID=args.display
        )
    elif args.primary == "underscan":
        command = dm.Command(
            args.primary,
            args.secondary,
            underscan=args.underscan,
            displayID=args.display
        )

    return command


def main():
    """
    Called on execution. Parses input and calls Display Manager.
    """
    args = sys.argv[1:]

    # Exit if the user didn't provide any arguments
    if len(args) < 1:
        showHelp()
        sys.exit(1)

    try:
        # Run the args as only one command
        command = getCommand(" ".join(args))
        command.run()
    except CommandSyntaxError:
        try:
            # Run the args as multiple commands
            commands = dm.CommandList()
            for commandString in args:
                command = getCommand(commandString)
                if command:
                    commands.addCommand(command)
            commands.run()
        except CommandSyntaxError:
            # User entered invalid command(s)
            showHelp()
            sys.exit(1)


if __name__ == "__main__":
    main()
