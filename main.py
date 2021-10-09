import cmd, sys, os, pydot, jinja2
from os.path import join, dirname
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export
from classes import Game, Location, Connection, Object, State, Action, Change, Condition, Conditions, DescribeConditions, Description, Message

# class Game(object):

#     def __init__(self, title, start, end, locations, objects, connections):
#         self.objects = objects
#         self.locations = locations
#         self.connections = connections
#         self.current_section = start
#         self.end = end
#         self.title = title
#         self.load_location_connections()
#         self.load_location_objects()
#         self.inventory = {}
#         self.load_inventory()


                    
#     def load_location_objects(self):
#         for location in self.locations:
#             for obj in self.objects:
#                 if obj.location == location and not obj.pickedUp:
#                     location.objects[obj.name] = obj              

#     def load_inventory(self):
#         for obj in self.objects:
#             if obj.canBePickedUp and obj.pickedUp:
#                 self.inventory[obj.name] = obj

#     def isUnlocked(self, obj: Object):
#         return (obj.canBeLocked and not obj.locked) or not obj.canBeLocked

#     def isOpened(self, obj: Object):
#         return (obj.canBeOpened and obj.opened) or not obj.canBeOpened

#     def isNotPickedUp(self, obj: Object):
#         return (obj.canBePickedUp and not obj.pickedUp) or not obj.canBePickedUp

#     def describe(self, obj = ""):
#         if obj == "":
#             print(self.current_section)
#         else:
#             if obj in self.current_section.objects:
#                 if self.isNotPickedUp(self.current_section.objects[obj]):
#                     print(self.current_section.objects[obj])
#                     if self.isUnlocked(self.current_section.objects[obj]):
#                         if self.isOpened(self.current_section.objects[obj]):
#                             for temp in self.objects:
#                                 if temp.containedObject and temp.containedObject.name == obj:
#                                     if self.isNotPickedUp(temp):
#                                         self.describe(temp.name)
#             elif obj in self.inventory:
#                 print(self.inventory[obj])
#             else:
#                 for temp in self.objects:
#                     if obj == temp.name:
#                         if temp.containedObject.location == self.current_section:
#                             if self.isNotPickedUp(temp.containedObject):
#                                 if self.isUnlocked(temp.containedObject):
#                                     if self.isOpened(temp.containedObject):
#                                         print(f"{temp}")
#                                         return
#                 print("That object doesn't exist")

#     def set_section(self, direction: str):
#         if direction.capitalize() in self.current_section.connections:
#             if self.current_section.connections[direction.capitalize()].toL.blocker == None or \
#                 self.current_section.connections[direction.capitalize()].toL.blocker.name in self.inventory:
#                 self.current_section = self.current_section.connections[direction.capitalize()].toL
#                 print(self.current_section)
#             else:
#                 print(f"The door is blocked, you need to aquire {self.current_section.connections[direction.capitalize()].toL.blocker.name} ")
#         else:
#             print("There is nothing in that direction")
#         if self.current_section == self.end:
#             print("YOU FINISHED THE GAME, CONGRATS!!!")
    
#     def list_inventory(self):
#         for key in self.inventory:
#             print(self.inventory[key])

#     def pick_an_object(self, obj):
#         if obj in self.current_section.objects:
#             if self.isNotPickedUp(self.current_section.objects[obj]) and self.current_section.objects[obj].canBePickedUp:
#                 self.current_section.objects[obj].pickedUp = True
#                 self.current_section.objects[obj].location = None
#                 self.inventory[obj] = self.current_section.objects[obj]
#                 self.current_section.objects.pop(obj)
#                 print(f"{self.inventory}\n")
#             else:
#                 print(f"{obj} cannot be picked up\n")
#         else:
#             for temp in self.objects:
#                 if obj == temp.name:
#                     if temp.containedObject.location == self.current_section:
#                         if self.isNotPickedUp(temp.containedObject):
#                             if self.isUnlocked(temp.containedObject):
#                                 if self.isOpened(temp.containedObject):
#                                     if self.isNotPickedUp(temp) and temp.canBePickedUp:
#                                         temp.pickedUp = True
#                                         self.inventory[obj] = temp
#                                         return
#                                     else:
#                                         print(f"{obj} cannot be picked up\n")
#             print("That object doesn't exist in this location")

#     def drop_an_object(self, obj):
#         if obj in self.inventory:
#             self.inventory[obj].location = self.current_section
#             self.inventory[obj].pickedUp = False
#             self.inventory[obj].containedObject = None
#             self.current_section.objects[obj] = self.inventory[obj]
#             self.inventory.pop(obj)
#         else:
#             print(f"{obj} cannot be droped because it isn't in the inventory")

#     def unlock_an_object(self, obj):
#         if obj in self.current_section.objects:
#             if self.current_section.objects[obj].canBeLocked and self.current_section.objects[obj].locked:
#                 self.current_section.objects[obj].locked = False
#                 print(f"{obj} is unlocked")
#             else:
#                 print(f"{obj} cannot be unlocked or is allready unlocked")
#         elif obj in self.inventory:
#             if self.inventory[obj].canBeLocked and self.inventory[obj].locked:
#                 self.inventory[obj].locked = False
#                 print(f"{obj} is unlocked")
#             else:
#                 print(f"{obj} cannot be unlocked or is allready unlocked")
#         else:
#             for temp in self.objects:
#                 if obj == temp.name:
#                     if temp.containedObject.location == self.current_section:
#                         if (temp.containedObject.canBeLocked and not temp.containedObject.locked) or not temp.containedObject.canBeLocked:
#                             if (temp.containedObject.canBeOpened and temp.containedObject.opened) or not temp.containedObject.canBeOpened:
#                                 if not temp.pickedUp:
#                                     if temp.canBeLocked and temp.locked:
#                                         temp.locked = False
#                                         print(f"{obj} is unlocked")
#                                     else:
#                                         print(f"{obj} cannot be unlocked or is allready unlocked")
#             print("That object doesn't exist")  

#     def open_an_object(self, obj):
#         if obj in self.current_section.objects:
#             if self.isUnlocked(self.current_section.objects[obj]):
#                 if self.current_section.objects[obj].canBeOpened and not self.current_section.objects[obj].opened:
#                     self.current_section.objects[obj].opened = True
#                     print(f"{obj} is opened")
#                 else:
#                     print(f"{obj} cannot be opened or is allready opened")
#             else:
#                 print(f"{obj} is locked")
#         elif obj in self.inventory:
#             if self.isUnlocked(self.inventory[obj]):
#                 if self.inventory[obj].canBeOpened and self.inventory[obj].opened:
#                     self.inventory[obj].opened = True
#                     print(f"{obj} is opened")
#                 else:
#                     print(f"{obj} cannot be opened or is allready opened")
#             else:
#                 print(f"{obj} is locked")
#         else:
#             for temp in self.objects:
#                 if obj == temp.name and temp.containedObject.location == self.current_section:
#                     if self.isUnlocked(temp.containedObject):
#                         if self.isOpened(temp.containedObject):
#                             if self.isUnlocked(temp):
#                                 if temp.canBeOpened and not temp.opened:
#                                     temp.opened = True
#                                     print(f"{obj} is opened")
#                                 else:
#                                     print(f"{obj} cannot be opened or is allready opened")
#                             else:
#                                 print(f"{obj} is locked")
#             print("That object doesn't exist")    

class GamePlay(cmd.Cmd):
    def __init__(self, game: Game, game_mm):
        cmd.Cmd.__init__(self)
        self.game = game
        self.game_mm = game_mm
        self.intro = '\33[31m' + f"\t\t\t\t\t\tWelcome to {game.title}\n" + '\33[0m'

    # intro = 'Welcome to new game\n'
    prompt = '\n-> '
    ruler = '-'
    file = None

    def do_go(self, arg):
        'Go certain direction'
        self.game.change_location(arg)

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

    game_mm = metamodel_from_file(join(this_folder, 'grammar.tx'), classes=[Game, Location, Connection, \
        Object, State, Action, Change, Condition, Conditions, DescribeConditions, Description, Message], builtins = type_builtins)

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