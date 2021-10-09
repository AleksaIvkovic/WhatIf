import cmd, sys, os, pydot, jinja2
from os.path import join, dirname
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export
from classes import Game, Object, Location
class GamePlay(cmd.Cmd):
    def __init__(self, game: Game, game_mm):
        cmd.Cmd.__init__(self)
        self.game = game
        self.game_mm = game_mm
        intro = '\33[31m' + f"\t\t\t\t\t\tWelcome to {game.title}\n\n" + '\33[0m'
        intro += self.game.location_as_string(self.game.start)
        self.intro = intro

    prompt = '\n-> '
    ruler = '-'
    file = None

    def do_go(self, arg):
        'Go certain direction'
        self.game.change_location(arg)

    def do_look(self, arg):
        'Describe current location'
        self.game.print_location(self.game.player.location)

    def do_inventory(self, arg):
        'List items in inventory'
        pass
        self.game.print_inventory()

    def do_save(self, arg):
        'Save game'
        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(join(dirname(__file__),'template')),
            trim_blocks=True,
            lstrip_blocks=True)
        template = jinja_env.get_template('game.template.j2')
        with open(join(dirname(__file__),
                      "SavedGame.wi"), 'w') as f:
            f.write(template.render(game=self.game))
        pass

    def do_load(self, arg):
        'Load saved game'
        self.game = self.game_mm.model_from_file(join(dirname(__file__), 'SavedGame.wi'))

    def do_exit(self, arg):
        'Leave the game'
        print("Are you sure?")
        responce = input("-> ")
        if responce.lower() == "yes" or responce.lower() == "y":
            sys.exit()

def main():
    this_folder = dirname(__file__)

    player = Object(None, "player", None, None)

    type_builtins = {
        'player': player,
    }

    game_mm = metamodel_from_file(join(this_folder, 'grammar.tx'), classes=[Game, Object, Location], builtins = type_builtins)

    game: Game = game_mm.model_from_file(join(this_folder, 'game.wi'))

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