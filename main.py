import cmd, sys, os, pydot, jinja2, click
from os.path import join, dirname
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export
from classes import Game, Object, Location
class GamePlay(cmd.Cmd):
    def __init__(self, game: Game, game_mm):
        cmd.Cmd.__init__(self)
        self.game = game
        self.game_mm = game_mm
        self.intro = '\33[31m' + f"\t\t\t\t\t\tWelcome to {game.title}\n\n" + '\33[0m'
        self.intro += 'To start a new game type new, or to load a previously saved game, type load'
        self.started = False

    prompt = '\n-> '
    ruler = '-'
    file = None

    def do_go(self, arg):
        'Go certain direction'
        if self.started:
            self.game.change_location(arg)

    def do_look(self, arg):
        'Describe current location'
        if self.started:
            self.game.print_location(self.game.player.location)

    def do_exam(self, arg):
        'Describe an object'
        if self.started:
            self.game.print_object(arg)

    def do_inventory(self, arg):
        'List items in inventory'
        if self.started:
            self.game.print_inventory()

    def do_save(self, arg):
        'Save game'
        if self.started:
            jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(join(dirname(__file__),'template')),
                trim_blocks=True,
                lstrip_blocks=True)
            template = jinja_env.get_template('game.template.j2')
            with open(join(dirname(__file__),
                        "SavedGame.wi"), 'w') as f:
                f.write(template.render(game=self.game))

    def do_load(self, arg):
        'Load saved game'
        self.game = self.game_mm.model_from_file(join(dirname(__file__), 'SavedGame.wi'))
        intro = f"\n\t\t{self.game.intro}\n\n"
        intro += self.game.location_as_string(self.game.start)
        print(intro)

    def do_new(self, arg):
        'Start new game'
        self.started = True
        intro = f"\n\t\t{self.game.intro}\n\n"
        intro += self.game.location_as_string(self.game.start)
        print(intro)

    def do_exit(self, arg):
        'Leave the game'
        print("Are you sure?")
        responce = input("-> ")
        if responce.lower() == "yes" or responce.lower() == "y":
            sys.exit()

@click.command()
@click.option('--gamefile', default="game.wi", help="Full or relative path to the game file")
def main(gamefile):
    this_folder = dirname(os.path.abspath(__file__))

    player = Object(None, "player", None, None, None)

    type_builtins = {
        'player': player,
        'none' : Location(None, 'none', '', None, None),
        'destroyed' : Location(None, 'destroyed', '', None, None)
    }

    game_mm = metamodel_from_file(join(this_folder, 'grammar.tx'), classes=[Game, Object, Location], builtins = type_builtins)

    try:
        print(join(this_folder, gamefile))
        game: Game = game_mm.model_from_file(join(this_folder, gamefile))
    except:
        try:
            game: Game = game_mm.model_from_file(gamefile)
        except:
            print("The game file path is not valid :/")
            return

    game.initialize(player)

    game_play = GamePlay(game, game_mm)

    def docstring_parameter(*sub):
        def dec(obj):
            obj.__doc__ = obj.__doc__.format(*sub)
            return obj
        return dec

    def custom_factory(verb):
        @docstring_parameter(verb.description.text)
        def handle_custom_actions(self, attr):
            '{0}'
            self.game.handle_custom_actions(verb.name, attr)
        return handle_custom_actions

    for verb in game.verbs:
        function = custom_factory(verb)

        setattr(GamePlay, 'do_' + verb.name, function)

    dot_folder = join(this_folder, 'dotexport')

    if not os.path.exists(dot_folder):
        os.mkdir(dot_folder)
    metamodel_export(game_mm, join(dot_folder, 'grammar.dot'))
    (graph,) = pydot.graph_from_dot_file(join(dot_folder, 'grammar.dot'))
    graph.write_png(join(dot_folder, 'grammar.png'))

    model_export(game, join(dot_folder, 'game.dot'))
    (graph,) = pydot.graph_from_dot_file(join(dot_folder, 'game.dot'))
    graph.write_png(join(dot_folder, 'game.png'))

    game_play.cmdloop()

if __name__ == "__main__":
    main()