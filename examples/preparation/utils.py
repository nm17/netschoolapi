import rich.console

console = rich.console.Console(no_color=True, width=80)


def pprint(object_):
    console.print(object_)
