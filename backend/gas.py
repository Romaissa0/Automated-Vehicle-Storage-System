import time

# parent class for the GAS system
class GAS:
    pass

# Class to manage assets : properties
class Assets:
    def __init__(self):
        self.properties = []
    def add(self, property):
        if isinstance(property, Property):
            self.properties.append(property)
            return f"{property.__class__.__name__} added successfully."
        else : return Alert("Invalid asset type. Cannot add to assets.").alert()
    def retrieve(self):
        return [prop.presentation() for prop in self.properties]

# parent class for properties
class Property:
    def __init__(self, id):
        self.id = id
        self.details = []
    def add_detail(self, detail):
        if detail:
            self.details.append(detail)
        return f"Detail '{detail}' added to {self.__class__.__name__} {self.id}."
    def retrieve_details(self):
        return self.details
    def presentation(self):
        return {
    f"{self.__class__.__name__}_id": self.id,
    "details": self.details
    }

# property type: Garage
class Garage(Property):
    def __init__(self, capacity, garage_id):
        super().__init__(garage_id)
        self.capacity = capacity
        self.cars = []
    def add_car(self, car):
        if len(self.cars) < self.capacity:
            self.cars.append(car)
            return f"Car '{car}' added successfully to garage {self.id}."
        else:
            return Alert(f"Garage {self.id} is full. Cannot add car '{car}'.").alert()
    def retrieve_cars(self):
        return self.cars
    def presentation(self):
        return {
    "garage_id": self.id,
    "capacity": self.capacity,
    "cars": self.cars
    }

# property type: Residence
class Residence(Property):
    def __init__(self, id, location, area):
        super().__init__(id)
        self.location = location
        self.area = area
    def presentation(self):
        return {
    "residence_id": self.id,
    "location": self.location,
    "area": self.area,
    "details": self.details
    }

# property type: Building
class Building(Property):
    def __init__(self, n_house, n_floor, building_id):
        super().__init__(building_id)
        self.n_house = n_house
        self.n_floor = n_floor
    def presentation(self):
        return {
    "building_id": self.id,
    "number_of_houses": self.n_house,
    "number_of_floors": self.n_floor,
    "details": self.details
    }

# parent system class
class System(GAS):
    pass

# Interface class for user interactions
class Interface(System):
    def __init__(self, name, email, phone, house_id):
        self.name = name
        self.email = email
        self.phone = phone
        self.house_id = house_id

# Alert class for error notifications
class Alert(Interface):
        def __init__(self, problem):
            self.problem = problem
        def alert(self):
            return f"ALERT: {self.problem}! Immediate action required." if self.problem else "No problems detected."

# Login class for user authentication
class Login(Interface):
    def login(self):
        if self.name and self.email:
            return f"{self.name} is successfully logged in with email: {self.email}."
        else:
            return "Login failed. Missing required information."

# Edit class for updating user details
class Edit(Interface):
    def edit_details(self, name=None, phone=None, email=None):
        if name:
            self.name = name
        if phone:
            self.phone = phone
        if email:
            self.email = email
        return f"Details updated successfully: Name: {self.name}, Phone: {self.phone}, Email: {self.email}."

# Controller class for managing garage doors
class Controller(System):
    def __init__(self):
        self.is_open = False
        self.is_moving = False
    def open_door(self):
        if self.is_open:
            return "The garage door is already open."
        self.is_moving = True
        time.sleep(1) # Simulate delay
        self.is_open = True
        self.is_moving = False
        return "The garage door is fully open."
    def close_door(self):
        if not self.is_open:
            return "The garage door is already closed."
        self.is_moving = True
        time.sleep(1) # Simulate delay
        self.is_open = False
        self.is_moving = False
        return "The garage door is fully closed."
    def remote_control(self, command):
        if command == "open":
            return self.open_door()
        elif command == "close":
            return self.close_door()
        else:
            return "Invalid command! Please use 'open' or 'close'."

# Request class for handling car access requests
# NOTE: in the original script this class -- and create_request -- were
# accidentally indented one level too far, nesting them inside Controller
# and splitting Request from its own method. That's the only change here:
# both are de-indented back to top-level so `Request` exists and
# `create_request` is a method of `Request`, not `Controller`.
class Request:
    def __init__(self, car_id, garage_id):
        self.car_id = car_id
        self.garage_id = garage_id
        self.cars = {level: [] for level in range(1, 20)}
    def create_request(self, car_id, requested_level):
        self.cars[requested_level].append(car_id)
        return f"Car '{car_id}' added successfully to requested level {requested_level} in multi_level garage."

# Task management classes
class TaskManage(System):
    pass

class Notify(TaskManage):
    def __init__(self, car_id, garage_id, name):
        self.car_id = car_id
        self.garage_id = garage_id
        self.name = name
    def send_notification(self):
        return f"Notification sent for car {self.car_id} in garage {self.garage_id} by {self.name}."

class Verify(TaskManage):
    def __init__(self, alert):
        self.alert = alert
    def verify_alert(self):
        return self.alert.alert()

# Help class for providing assistance
class Help(System):
    def __init__(self, car_id, payment_state, car_state, rental_value):
        self.car_id = car_id
        self.payment_state = payment_state
        self.car_state = car_state
        self.rental_value = rental_value

    def provide_help(self):
        return f"Help provided for car {self.car_id}: Payment State - {self.payment_state}, Car State - {self.car_state}, Rental Value - {self.rental_value}."


# Account combines Login + Edit through your existing Interface hierarchy --
# no new logic, just reusing both mixins on one object so a session can both
# log in and edit its own details.
class Account(Login, Edit):
    pass
