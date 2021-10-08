import cmd, sys
from os.path import join, dirname
from textx import metamodel_from_file
import jinja2

opposite_direction = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
    "NW": "SE",
    "SE": "NW",
    "NE": "SW",
    "SW": "NE"
}

class Object(object):
    def __init__(self, parent, name, description, location, canBePickedUp, canBeOpened, canBeLocked, containedObject, pickedUp = False, opened = False, locked = True):
        self.parent = parent
        self.name = name
        self.description = description
        self.location = location
        self.canBePickedUp = canBePickedUp
        self.pickedUp = pickedUp
        self.canBeOpened = canBeOpened
        self.opened = opened
        self.canBeLocked = canBeLocked
        self.locked = locked
        self.containedObject = containedObject

    def __str__(self):
        return self.description

class Connection(object):
    def __init__(self, parent, fromL, direction, toL):
        self.parent = parent
        self.fromL = fromL
        self.toL = toL
        self.direction = direction

class Location(object):
    def __init__(self, parent, name, description, blocker):
        self.parent = parent
        self.name = name
        self.description = description
        self.blocker = blocker
        self.objects = {}
        self.connections = {}

    def __str__(self):
        desc = f"\t{self.description}"
        if len(self.objects) > 0:
            desc += "\n\nYou can see "
        for key in self.objects:
            desc += f"{self.objects[key]}, "
        if len(self.connections) > 0:
            desc += "\n\nExists are "
        for key in self.connections:
            desc += f"{key}, "
        return desc

class Game(object):

    def __init__(self, title, start, end, locations, objects, connections):
        self.objects = objects
        self.locations = locations
        self.connections = connections
        self.current_section = start
        self.end = end
        self.title = title
        self.load_location_connections()
        self.load_location_objects()
        self.inventory = {}
        self.load_inventory()

    def load_location_connections(self):
        for location in self.locations:
            for connection in self.connections:
                if(connection.fromL == location):
                    location.connections[connection.direction] = connection
                elif(connection.toL == location):
                    new_connection = Connection(connection.parent, connection.fromL, connection.direction, connection.toL)
                    new_connection.toL = connection.fromL
                    new_connection.fromL = connection.toL
                    new_connection.direction = opposite_direction[connection.direction]
                    location.connections[new_connection.direction] = new_connection
                    
    def load_location_objects(self):
        for location in self.locations:
            for obj in self.objects:
                if obj.location == location and not obj.pickedUp:
                    location.objects[obj.name] = obj              

    def load_inventory(self):
        for obj in self.objects:
            if obj.canBePickedUp and obj.pickedUp:
                self.inventory[obj.name] = obj

    def isUnlocked(self, obj: Object):
        return (obj.canBeLocked and not obj.locked) or not obj.canBeLocked

    def isOpened(self, obj: Object):
        return (obj.canBeOpened and obj.opened) or not obj.canBeOpened

    def isNotPickedUp(self, obj: Object):
        return (obj.canBePickedUp and not obj.pickedUp) or not obj.canBePickedUp

    def describe(self, obj = ""):
        if obj == "":
            print(self.current_section)
        else:
            if obj in self.current_section.objects:
                if self.isNotPickedUp(self.current_section.objects[obj]):
                    print(self.current_section.objects[obj])
                    if self.isUnlocked(self.current_section.objects[obj]):
                        if self.isOpened(self.current_section.objects[obj]):
                            for temp in self.objects:
                                if temp.containedObject and temp.containedObject.name == obj:
                                    if self.isNotPickedUp(temp):
                                        self.describe(temp.name)
            elif obj in self.inventory:
                print(self.inventory[obj])
            else:
                for temp in self.objects:
                    if obj == temp.name:
                        if temp.containedObject.location == self.current_section:
                            if self.isNotPickedUp(temp.containedObject):
                                if self.isUnlocked(temp.containedObject):
                                    if self.isOpened(temp.containedObject):
                                        print(f"{temp}")
                                        return
                print("That object doesn't exist")

    def set_section(self, direction: str):
        if direction.capitalize() in self.current_section.connections:
            if self.current_section.connections[direction.capitalize()].toL.blocker == None or \
                self.current_section.connections[direction.capitalize()].toL.blocker.name in self.inventory:
                self.current_section = self.current_section.connections[direction.capitalize()].toL
                print(self.current_section)
            else:
                print(f"The door is blocked, you need to aquire {self.current_section.connections[direction.capitalize()].toL.blocker.name} ")
        else:
            print("There is nothing in that direction")
        if self.current_section == self.end:
            print("YOU FINISHED THE GAME, CONGRATS!!!")
    
    def list_inventory(self):
        for key in self.inventory:
            print(self.inventory[key])

    def pick_an_object(self, obj):
        if obj in self.current_section.objects:
            if self.isNotPickedUp(self.current_section.objects[obj]) and self.current_section.objects[obj].canBePickedUp:
                self.current_section.objects[obj].pickedUp = True
                self.current_section.objects[obj].location = None
                self.inventory[obj] = self.current_section.objects[obj]
                self.current_section.objects.pop(obj)
                print(f"{self.inventory}\n")
            else:
                print(f"{obj} cannot be picked up\n")
        else:
            for temp in self.objects:
                if obj == temp.name:
                    if temp.containedObject.location == self.current_section:
                        if self.isNotPickedUp(temp.containedObject):
                            if self.isUnlocked(temp.containedObject):
                                if self.isOpened(temp.containedObject):
                                    if self.isNotPickedUp(temp) and temp.canBePickedUp:
                                        temp.pickedUp = True
                                        self.inventory[obj] = temp
                                        return
                                    else:
                                        print(f"{obj} cannot be picked up\n")
            print("That object doesn't exist in this location")

    def drop_an_object(self, obj):
        if obj in self.inventory:
            self.inventory[obj].location = self.current_section
            self.inventory[obj].pickedUp = False
            self.inventory[obj].containedObject = None
            self.current_section.objects[obj] = self.inventory[obj]
            self.inventory.pop(obj)
        else:
            print(f"{obj} cannot be droped because it isn't in the inventory")

    def unlock_an_object(self, obj):
        if obj in self.current_section.objects:
            if self.current_section.objects[obj].canBeLocked and self.current_section.objects[obj].locked:
                self.current_section.objects[obj].locked = False
                print(f"{obj} is unlocked")
            else:
                print(f"{obj} cannot be unlocked or is allready unlocked")
        elif obj in self.inventory:
            if self.inventory[obj].canBeLocked and self.inventory[obj].locked:
                self.inventory[obj].locked = False
                print(f"{obj} is unlocked")
            else:
                print(f"{obj} cannot be unlocked or is allready unlocked")
        else:
            for temp in self.objects:
                if obj == temp.name:
                    if temp.containedObject.location == self.current_section:
                        if (temp.containedObject.canBeLocked and not temp.containedObject.locked) or not temp.containedObject.canBeLocked:
                            if (temp.containedObject.canBeOpened and temp.containedObject.opened) or not temp.containedObject.canBeOpened:
                                if not temp.pickedUp:
                                    if temp.canBeLocked and temp.locked:
                                        temp.locked = False
                                        print(f"{obj} is unlocked")
                                    else:
                                        print(f"{obj} cannot be unlocked or is allready unlocked")
            print("That object doesn't exist")  

    def open_an_object(self, obj):
        if obj in self.current_section.objects:
            if self.isUnlocked(self.current_section.objects[obj]):
                if self.current_section.objects[obj].canBeOpened and not self.current_section.objects[obj].opened:
                    self.current_section.objects[obj].opened = True
                    print(f"{obj} is opened")
                else:
                    print(f"{obj} cannot be opened or is allready opened")
            else:
                print(f"{obj} is locked")
        elif obj in self.inventory:
            if self.isUnlocked(self.inventory[obj]):
                if self.inventory[obj].canBeOpened and self.inventory[obj].opened:
                    self.inventory[obj].opened = True
                    print(f"{obj} is opened")
                else:
                    print(f"{obj} cannot be opened or is allready opened")
            else:
                print(f"{obj} is locked")
        else:
            for temp in self.objects:
                if obj == temp.name and temp.containedObject.location == self.current_section:
                    if self.isUnlocked(temp.containedObject):
                        if self.isOpened(temp.containedObject):
                            if self.isUnlocked(temp):
                                if temp.canBeOpened and not temp.opened:
                                    temp.opened = True
                                    print(f"{obj} is opened")
                                else:
                                    print(f"{obj} cannot be opened or is allready opened")
                            else:
                                print(f"{obj} is locked")
            print("That object doesn't exist")    

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

    #region look
    def do_look(self, arg):
        'Describes current location or an object'
        self.game.describe(arg)
        pass

    def do_rediscribe(self, arg):
        'Describes current location'
        self.game.describe()
        pass
    
    def do_examine(self, arg):
        'Describes object'
        self.game.describe(arg)
        pass

    def do_exam(self, arg):
        'Describes object'
        self.game.describe(arg)
        pass
    #endregion

    def do_go(self, arg):
        'Go certain direction'
        self.game.set_section(arg)

    def do_inventory(self, arg):
        'List items in inventory'
        self.game.list_inventory()

    #region pick up
    def do_pick(self, arg):
        'pick up an object'
        self.game.pick_an_object(arg)

    def do_take(self, arg):
        'pick up an object'
        self.game.pick_an_object(arg)

    def do_get(self, arg):
        'pick up an object'
        self.game.pick_an_object(arg)
    #endregion

    def do_drop(self, arg):
        'drop an object'
        self.game.drop_an_object(arg)

    def do_unlock(self, arg):
        'unlock an object'
        self.game.unlock_an_object(arg)

    def do_open(self, arg):
        'open an object'
        self.game.open_an_object(arg)

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
    game_mm = metamodel_from_file(join(this_folder, 'grammar.tx'))#, classes=[Game, Location, Connection, Object])

    game = game_mm.model_from_file(join(this_folder, 'game.wi'))
    #GamePlay(game, game_mm).cmdloop()

if __name__ == "__main__":
    main()