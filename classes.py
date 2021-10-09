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

class Description(object):
    def __init__(self, parent, text):
        self.parent = parent
        self.text = text

    def __str__(self):
        return self.text

class Message(object):
    def __init__(self, parent, text, success, failure):
        self.parent = parent
        self.text = text
        self.success = success
        self.failure = failure

class DescribeConditions(object):
    def __init__(self, parent, conditions, print_content):
        self.parent = parent
        self.conditions = conditions
        self.print_content = print_content

class Condition(object):
    def __init__(self, parent, state, value: bool, object, location):
        self.parent = parent
        self.state = state
        self.value = value
        self.object = object
        self.location = location

class Conditions(object):
    def __init__(self, parent, conditions: List[Condition], message:Message):
        self.parent = parent
        self.conditions = conditions
        self.message = message

class Change(object):
    def __init__(self, parent, object, location, state, value):
        self.parent = parent
        self.object = object
        self.location = location
        self.state = state
        self.value = value

class Action(object):
    def __init__(self, parent, verb, related, execution):
        self.parent = parent
        self.verb = verb
        self.related = related
        self.execution = execution

class State(object):
    def __init__(self, parent, name, related, state, true_message, false_message):
        self.parent = parent
        self.name = name
        self.related = related
        self.state = state
        self.true_message = true_message
        self.false_message = false_message

class Object(object):
    def __init__(self, parent, name: str, description: Description, location):
        self.parent = parent
        self.name = name
        self.description = description
        self.location = location

    def __str__(self):
        return self.description.text

class Connection(object):
    def __init__(self, parent, from_location, to_location, direction):
        self.parent = parent
        self.from_location = from_location
        self.to_location = to_location
        self.direction = direction

class Location(object):
    def __init__(self, parent, name: str, description: Description, requirements: Conditions):
        self.parent = parent
        self.name = name
        self.description = description
        self.requirements = requirements
        self.connections = {}

    def __str__(self):
        string = self.description.text
        string += "\n Exits are on: "
        for connection in self.connections:
            string+=f"{connection}, "
        return string

class Game(object):
    def __init__(self, title: str, start: Location, end: Conditions, locations: List[Location], connections: List[Connection], \
        objects: List[Object], states: List[Object], actions: List[Action], verbs):
        self.title = title
        self.start = start
        self.end = end
        self.locations = locations
        self.connections = connections
        self.objects = objects
        self.states = states
        self.actions = actions
        self.verbs = verbs

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

    def initialize(self, player: Object):
        self.player = player
        self.load_location_connections()
        self.player.location = self.start
        
    def check_conditions(self, requirements: Conditions):
        for condition in requirements.conditions:
            if condition.__class__.__name__ == "LocationCondition":
                if condition.object.location != condition.location:
                    return False
            else:
                if condition.state.state != condition.value:
                    return False
        return True

    def print_inventory(self):
        for object in self.objects:
            if object.location.name == "player":
                print(object)

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
                        print(self.player.location)
                else:
                    print(self.player.location.connections[direction.capitalize()].to_location.requirements.message.text)
            else:
                self.player.location = self.player.location.connections[direction.capitalize()].to_location
                print(self.player.location)
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
            if action.verb.name == verb and action.related.name == object:
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
                    print("EA")
                return
        print("Not a valid object for a command")