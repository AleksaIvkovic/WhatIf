from typing import List

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
    def __init__(self, parent, name, description, requirements):
        self.parent = parent
        self.name = name
        self.description = description
        self.requirements = requirements
        self.connections = {}

    def __str__(self):
        return self.description.text

class Object(object):
    def __init__(self, parent, name: str, description, location):
        self.parent = parent
        self.name = name
        self.description = description
        self.location = location

    def __str__(self):
        return self.description.text

class Game(object):
    def __init__(self, title: str, start, end, locations, connections, objects: List[Object], states, actions, verbs):
        self.title = title
        self.start = start
        self.end = end
        self.locations = convert(locations)
        self.connections = connections
        self.objects = convert(objects)
        self.states = convert(states)
        self.actions = actions
        self.verbs = convert(verbs)

    def load_location_connections(self):
        for location in self.locations.values():
            for connection in self.connections:
                if connection.from_location == location:
                    location.connections[connection.direction] = connection
                elif connection.to_location == location:
                    new_connection = Connection(connection.parent, connection.from_location, connection.to_location, connection.direction)
                    new_connection.to_location = connection.from_location
                    new_connection.from_location = connection.to_location
                    new_connection.direction = opposite_direction[connection.direction]
                    location.connections[new_connection.direction] = new_connection

    def initialize(self, player: Object):
        self.player = player
        self.load_location_connections()
        self.player.location = self.start

    def check_conditions(self, requirements):
        for condition in requirements.conditions:
            if condition.__class__.__name__ == "LocationCondition":
                if condition.object.location != condition.location:
                    return False
            else:
                if condition.state.state != condition.value:
                    return False
        return True

    def location_as_string(self, location):
        string = location.description.text
        first = True
        for object in self.objects.values():
            if object.location == location:
                if first:
                    first = False
                    string += "\nYou see: "
                string += f"\n\t{object}"
        
        i = 1
        connections = "\nExits are on: "
        for connection in location.connections:
            connections += connection.__str__()
            if i != len(location.connections):
                connections += ", "
            i = i + 1
        string += connections
        return string

    def print_object(self, object, description):
        print(object)
        if description.__class__.__name__ == "DescribeConditions":
            print(description.conditions.message.text)
        if description.print_content:
            for obj in self.objects.values():
                if obj.location == object:
                    print(f"\t{obj}")

    def print_location(self, location):
        print(location.description.text)
        first = True
        for object in self.objects.values():
            if object.location == location:
                if first:
                    first = False
                    print("You see: ")
                print(f"\t{object}")
        
        i = 1
        connections = "Exits are on: "
        for connection in location.connections:
            connections += connection.__str__()
            if i != len(location.connections):
                connections += ", "
            i = i + 1
        print(connections)

    def print_object(self, object, description):
        print(object)
        if description.__class__.__name__ == "DescribeConditions":
            print(description.conditions.message.text)
        if description.print_content:
            for obj in self.objects.values():
                if obj.location == object:
                    print(f"\t{obj}")

    def print_inventory(self):
        inventory = []
        for object in self.objects.values():
            if object.location.name == self.player.name:
                inventory.append(object)
        if len(inventory) == 0:
            print("You currently don't have anything in your inventory")
        else:
            print("Inventory:")
            for object in inventory:
                print(f"\t{object}")

    def change_location(self, direction: str):
        if direction.capitalize() == 'UP' or direction.capitalize() == 'U':
            direction = 'N'
        elif direction.capitalize() == 'DOWN' or direction.capitalize() == 'D':
            direction = 'S'

        if direction.capitalize() in self.player.location.connections:
            if self.player.location.connections[direction.capitalize()].to_location.requirements != None:
                if self.check_conditions(self.player.location.connections[direction.capitalize()].to_location.requirements):
                    self.player.location = self.player.location.connections[direction.capitalize()].to_location
                    if self.check_conditions(self.end):
                        print(self.end.message.text)
                    else:
                        self.print_location(self.player.location)
                else:
                    print(self.player.location.connections[direction.capitalize()].to_location.requirements.message.text)
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
            if action.verb.name == verb and (action.related.name == object or action.related == None):
                if action.execution.__class__.__name__ == "StateAction":
                    if action.execution.conditions != None:
                        if self.check_conditions(action.execution.conditions):
                            self.execute_changes(action.execution.changes)
                            print(action.execution.conditions.message.success)
                        else:
                            print(action.execution.conditions.message.failure)
                    else:
                        self.execute_changes(action.execution.changes)
                else:
                    for description in action.execution.descriptions:
                        if description.__class__.__name__ == "DescribeConditions":
                            if self.check_conditions(description.conditions):
                                self.print_object(action.related, description)
                                return
                        else:
                            self.print_object(action.related, description)
                            return
                return
        print("Not a valid object for a command")