import time
from unicodedata import name
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
    class Request:
        def __init__(self, car_id, garage_id):
            self.car_id = car_id
            self.garage_id = garage_id
            self.cars = {level: [] for level in range(1, 20)}
    def create_request(self,car_id,requested_level):
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

# Create assets and add properties
assets = Assets()
# Add a Residence
residence1 = Residence(id="R1", location="Downtown", area="120 sqm")
residence1.add_detail("3 bedrooms")
residence1.add_detail("2 bathrooms")
print(assets.add(residence1)) # Add the residence to assets
# Add a Garage
garage = Garage(capacity=2, garage_id="G1")
garage.add_car("Car1")
garage.add_car("Car2")
print(assets.add(garage)) # Add the garage to assets
# Add a Building
building1 = Building(n_house=10, n_floor=5, building_id="B1")
building1.add_detail("Parking available")
print(assets.add(building1)) # Add the building to assets
# Retrieve and display all properties
print("Assets Overview:")
for property_info in assets.retrieve():
    print(property_info)
# garage functionalities:
# Controller operations for a garage door
controller = Controller()
print(controller.remote_control("open")) # Open the garage door
print(controller.remote_control("close")) # Close the garage door
print()
# user interactions:
# Create a user login
login = Login(name="Alice", email="alice@example.com", phone="123456789", house_id="R1")
print(login.login())
# Edit user details
edit = Edit(name="Alice", email="alice@example.com", phone="123456789", house_id="R1")
print(edit.edit_details(phone="987654321"))
# Create a request
request = Request( car_id="Car1",garage_id="G1")
print(request.create_request("G1",3))
# Send a notification
notification = Notify(car_id="Car1", garage_id="G1", name="Alice")
print(notification.send_notification())
# Verify an alert
alert = Alert("Garage is FULL")
verify = Verify(alert=alert)
print(alert.alert())
print(verify.verify_alert())
# Provide help
help_system = Help(car_id="Car2", payment_state="Paid", car_state="Good", rental_value="$500/month")
print(help_system.provide_help())