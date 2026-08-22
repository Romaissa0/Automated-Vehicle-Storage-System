"""
Flask API for the GAS system. Every route just builds/calls objects from
gas.py and returns their real return values -- no logic is duplicated here.
"""
from flask import Flask, jsonify, request

from gas import (
    Account, Alert, Assets, Building, Controller, Garage, Help, Notify,
    Request as GasRequest, Residence, Verify,
)

app = Flask(__name__)

# ---- Server-side state (in-memory, mirrors what the demo script created) ----
assets = Assets()
controllers = {}          # garage_id -> Controller  (one real door controller per garage)
request_book = GasRequest(car_id=None, garage_id=None)  # one shared 19-level request book, as in the original
account = Account(name="", email="", phone="", house_id="")
activity_feed = []        # log of every Alert/Notify/Login/Edit message, newest first
help_records = []         # every Help.provide_help() call, newest first


def log(kind, message):
    activity_feed.insert(0, {"kind": kind, "message": message})


def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


app.after_request(cors)


@app.route("/api/<path:_any>", methods=["OPTIONS"])
def preflight(_any):
    return "", 204


# ---------------------------------------------------------------- Assets ----
@app.get("/api/assets")
def list_assets():
    # Assets.retrieve() is called exactly as in the original script
    return jsonify(assets.retrieve())


@app.post("/api/assets/residence")
def add_residence():
    data = request.get_json(force=True)
    residence = Residence(id=data["id"], location=data["location"], area=data["area"])
    message = assets.add(residence)  # Assets.add()
    return jsonify({"message": message, "assets": assets.retrieve()})


@app.post("/api/assets/garage")
def add_garage():
    data = request.get_json(force=True)
    garage = Garage(capacity=int(data["capacity"]), garage_id=data["id"])
    message = assets.add(garage)
    controllers[garage.id] = Controller()  # one door controller for this garage
    return jsonify({"message": message, "assets": assets.retrieve()})


@app.post("/api/assets/building")
def add_building():
    data = request.get_json(force=True)
    building = Building(n_house=int(data["n_house"]), n_floor=int(data["n_floor"]), building_id=data["id"])
    message = assets.add(building)
    return jsonify({"message": message, "assets": assets.retrieve()})


@app.post("/api/assets/<asset_id>/detail")
def add_detail(asset_id):
    data = request.get_json(force=True)
    prop = next((p for p in assets.properties if p.id == asset_id), None)
    if prop is None:
        return jsonify({"error": "No asset with that id"}), 404
    message = prop.add_detail(data["detail"])  # Property.add_detail()
    return jsonify({"message": message, "assets": assets.retrieve()})


# ---------------------------------------------------------------- Garage ----
def _find_garage(garage_id):
    return next((p for p in assets.properties if isinstance(p, Garage) and p.id == garage_id), None)


@app.post("/api/garages/<garage_id>/cars")
def add_car(garage_id):
    garage = _find_garage(garage_id)
    if garage is None:
        return jsonify({"error": "No garage with that id"}), 404
    data = request.get_json(force=True)
    message = garage.add_car(data["car"])  # Garage.add_car() -- may itself return an Alert message
    log("alert" if "ALERT" in message else "notify", message)
    return jsonify({"message": message, "assets": assets.retrieve()})


@app.post("/api/garages/<garage_id>/door")
def move_door(garage_id):
    controller = controllers.get(garage_id)
    if controller is None:
        return jsonify({"error": "No controller for that garage"}), 404
    command = request.get_json(force=True)["command"]
    message = controller.remote_control(command)  # Controller.remote_control() -- real 1s delay inside
    log("notify", message)
    return jsonify({"message": message, "is_open": controller.is_open})


@app.get("/api/garages/<garage_id>/door")
def door_status(garage_id):
    controller = controllers.get(garage_id)
    if controller is None:
        return jsonify({"error": "No controller for that garage"}), 404
    return jsonify({"is_open": controller.is_open, "is_moving": controller.is_moving})


# ------------------------------------------------------------- Requests ----
@app.post("/api/requests")
def create_request():
    data = request.get_json(force=True)
    message = request_book.create_request(data["car_id"], int(data["level"]))  # Request.create_request()
    log("notify", message)
    return jsonify({"message": message, "levels": request_book.cars})


@app.get("/api/requests")
def list_requests():
    return jsonify(request_book.cars)


# --------------------------------------------------------------- Account ----
@app.post("/api/account/login")
def login():
    global account
    data = request.get_json(force=True)
    account = Account(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        house_id=data.get("house_id", ""),
    )
    message = account.login()  # Login.login()
    log("notify" if "successfully" in message else "alert", message)
    return jsonify({
        "message": message,
        "logged_in": "successfully" in message,
        "account": vars(account),
    })


@app.put("/api/account")
def edit_account():
    data = request.get_json(force=True)
    message = account.edit_details(
        name=data.get("name") or None,
        phone=data.get("phone") or None,
        email=data.get("email") or None,
    )  # Edit.edit_details()
    log("notify", message)
    return jsonify({"message": message, "account": vars(account)})


@app.get("/api/account")
def get_account():
    return jsonify(vars(account))


# ----------------------------------------------------- Alerts / Notify ----
@app.post("/api/notify")
def notify():
    data = request.get_json(force=True)
    n = Notify(car_id=data["car_id"], garage_id=data["garage_id"], name=account.name or "Guest")
    message = n.send_notification()  # Notify.send_notification()
    log("notify", message)
    return jsonify({"message": message})


@app.post("/api/alert")
def raise_alert():
    data = request.get_json(force=True)
    alert = Alert(data["problem"])
    alert_message = alert.alert()          # Alert.alert()
    verify_message = Verify(alert).verify_alert()  # Verify.verify_alert()
    log("alert", alert_message)
    log("notify", f"Verified: {verify_message}")
    return jsonify({"alert": alert_message, "verified": verify_message})


@app.get("/api/activity")
def get_activity():
    return jsonify(activity_feed)


# ------------------------------------------------------------------ Help ----
@app.post("/api/help")
def file_help():
    data = request.get_json(force=True)
    h = Help(
        car_id=data["car_id"],
        payment_state=data["payment_state"],
        car_state=data["car_state"],
        rental_value=data["rental_value"],
    )
    message = h.provide_help()  # Help.provide_help()
    help_records.insert(0, {
        "car_id": h.car_id, "payment_state": h.payment_state,
        "car_state": h.car_state, "rental_value": h.rental_value, "message": message,
    })
    return jsonify({"message": message, "records": help_records})


@app.get("/api/help")
def list_help():
    return jsonify(help_records)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def seed():
    """Same seed data as the bottom of the original script, so the UI opens with something in it."""
    residence1 = Residence(id="R1", location="Downtown", area="120 sqm")
    residence1.add_detail("3 bedrooms")
    residence1.add_detail("2 bathrooms")
    assets.add(residence1)

    garage = Garage(capacity=2, garage_id="G1")
    garage.add_car("Car1")
    garage.add_car("Car2")
    assets.add(garage)
    controllers["G1"] = Controller()

    building1 = Building(n_house=10, n_floor=5, building_id="B1")
    building1.add_detail("Parking available")
    assets.add(building1)


if __name__ == "__main__":
    seed()
    app.run(debug=True, port=5000)
