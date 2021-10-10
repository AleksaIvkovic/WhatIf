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

def convert(list):
    res_dct = {list[i].name: list[i] for i in range(0, len(list))}
    return res_dct

class Connection(object):
    def __init__(self, parent, from_location, to_location, direction):
        self.parent = parent
        self.from_location = from_location
        self.to_location = to_location
        self.direction = direction

class Location(object):
    def __init__(self, parent, name, description, requirements, message):
        self.parent = parent
        self.name = name
        self.description = description
        self.requirements = requirements
        self.message = message
        self.connections = {}
        self.states = []
    
class Object(object):
    def __init__(self, parent, name: str, description, location):
        self.parent = parent
        self.name = name
        self.description = description
        self.location = location
        self.states = []

class Game(object):
    def __init__(self, title: str, start, end, locations, connections, objects, states, actions, verbs):
        self.title = title
        self.start = start
        self.end = end
        self.locations = locations
        self.locationsDic = convert(locations)
        self.connections = connections
        self.objects = objects
        self.objectsDic = convert(objects)
        self.states = states
        self.statesDic = convert(states)
        self.actions = actions
        self.verbs = verbs
        self.verbsDic = convert(verbs)

    def load_location_connections(self):
        for location in self.locations:
            for connection in self.connections:
                if connection.from_location == location:
                    location.connections[connection.direction] = connection
                elif connection.to_location == location:
                    new_connection = Connection(connection.parent, connection.from_location, connection.to_location, connection.direction)
                    new_connection.to_location = connection.from_location
                    new_connection.from_location = connection.to_location
                    new_connection.direction = opposite_direction[connection.direction]
                    location.connections[new_connection.direction] = new_connection

    def load_object_states(self):
        for state in self.states:
            if state.related.states == None:
                state.related.states = []
            state.related.states.append(state)

        for object in self.objects:
            object.states.sort(key=lambda x: x.priority)

    def initialize(self, player: Object):
        self.player = player
        self.load_location_connections()
        self.load_object_states()
        self.player.location = self.start

    def check_conditions(self, requirements, doPrint=False):
        for condition in requirements.conditions:
            if condition.__class__.__name__ == "LocationCondition":
                result = condition.object.location == condition.location
                if not result:
                    if condition.message != None and doPrint:
                        print(condition.message.text)
                    return False 
            else:
                result = condition.state.state == condition.value
                if not result:
                    if condition.message != None and doPrint:
                        print(condition.message.text)
                    return False 
        return True

    def check_location(self, object):
        if object.location.name == self.player.location.name:
            return True
        else:
            if object.location.__class__.__name__ == "Object":
                return self.check_location(object.location)
            else:
                return False

    def location_as_string(self, location):
        string = location.description.text
        first = True
        for object in self.objects:
            if object.location == location:
                if first:
                    first = False
                    string += "\nYou see: "
                string += f"\n\t{object.name}"
        
        i = 1
        connections = "\nExits are on: "
        for connection in location.connections:
            connections += connection.__str__()
            if i != len(location.connections):
                connections += ", "
            i = i + 1
        string += connections
        return string

    def print_location(self, location):
        print(location.description.text)
        first = True
        for object in self.objects:
            if object.location == location:
                if first:
                    first = False
                    print("You see: ")
                print(f"\t{object.name}")
        
        i = 1
        connections = "Exits are on: "
        for connection in location.connections:
            connections += connection.__str__()
            if i != len(location.connections):
                connections += ", "
            i = i + 1
        print(connections)

    def print_object(self, object):
        if self.check_location(self.objectsDic[object]) or self.objectsDic[object].location == self.player:
            print(self.objectsDic[object].description.text)
            if self.objectsDic[object].states != []:
                for state in self.objectsDic[object].states:
                    if state.state:
                        if state.true_message:
                            print(state.true_message)
                            break
                    else:
                        if state.false_message:
                            print(state.false_message)
                            break
            for action in self.actions:
                if action.__class__.__name__ == "DescribeAction":
                    if action.related.name == object:
                        if self.check_conditions(action.conditions):
                            print(action.message.text)
                            if action.print_content:
                                for obj in self.objects:
                                    if obj.location.name == object:
                                        print(f"\t{obj.name}")
        else:
            print("There is no such object in this location")

    def print_inventory(self):
        inventory = []
        for object in self.objects:
            if object.location.name == self.player.name:
                inventory.append(object)
        if len(inventory) == 0:
            print("You currently don't have anything in your inventory")
        else:
            print("Inventory:")
            for object in inventory:
                print(f"\t{object.name}")

    def change_location(self, direction: str):
        if direction.capitalize() == 'UP' or direction.capitalize() == 'U':
            direction = 'N'
        elif direction.capitalize() == 'DOWN' or direction.capitalize() == 'D':
            direction = 'S'

        if direction.capitalize() in self.player.location.connections:
            if self.player.location.connections[direction.capitalize()].to_location.requirements != None:
                if self.check_conditions(self.player.location.connections[direction.capitalize()].to_location.requirements):
                    self.player.location = self.player.location.connections[direction.capitalize()].to_location
                    if self.check_conditions(self.end.conditions):
                        print(self.end.message.text)
                    else:
                        self.print_location(self.player.location)
                else:
                    print(self.player.location.connections[direction.capitalize()].to_location.message.text)
            else:
                self.player.location = self.player.location.connections[direction.capitalize()].to_location
                self.print_location(self.player.location)
        else:
            print("There is nothing in that direction")

    def execute_changes(self, changes):
        for change in changes:
            if change.__class__.__name__ == "StateValueChange":
                change.state.state = change.value
            else:
                change.object.location = change.location

    def handle_custom_actions(self, verb, object):
        for action in self.actions:
            if action.__class__.__name__ == "StateAction":
                if action.verb.name == verb and action.related.name == object:
                    if self.check_location(action.related) or action.related.location == self.player:
                        if action.conditions != None:
                            if self.check_conditions(action.conditions, True):
                                self.execute_changes(action.changes)
                                if action.message != None:
                                    print(action.message.text) 
                        else:
                            self.execute_changes(action.changes)
                            if action.message != None:
                                print(action.message.text) 
                    else:
                        print("That object doesn't exist in this location")
                    return
        print("Not a valid object for a command")