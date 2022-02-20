from flask import Blueprint, render_template, request, redirect, url_for, session
from models.alert_dynamo import Alert
from models.store_dynamo import Store
from models.item_dynamo import Item
from models.user_dynamo.decorators import requires_login

alert_blueprint = Blueprint("alerts", __name__)


@alert_blueprint.route("/")
@requires_login
def index():
    alerts = Alert.find_by_email(session["email"])
    return render_template("alerts/index.html", alerts=alerts)


@alert_blueprint.route("/new", methods=["GET", "POST"])
@requires_login
def create_alert():
    if request.method == "POST":
        item_url = request.form["item_url"]

        store = Store.find_by_url(item_url)
        item = Item(item_url, store.tag_name, store.query)
        item.load_price()
        item.save_to_dynamo(item.json())

        alert_name = request.form["name"]
        price_limit = float(request.form["price_limit"])

        alert = Alert(alert_name, item._id, price_limit, session["email"])
        Alert.save_to_dynamo(alert.json())

    # What happens if it's a GET request
    return render_template("alerts/new_alert.html")


@alert_blueprint.route("/edit/<string:alert_id>", methods=["GET", "POST"])
@requires_login
def edit_alert(alert_id):
    if request.method == "POST":
        price_limit = float(request.form["price_limit"])

        alert = Alert.find_by_id(alert_id, session['email'])
        alert.price_limit = price_limit
        Alert.save_to_dynamo(alert.json())

        return redirect(url_for(".index"))

    # What happens if it's a GET request
    return render_template("alerts/edit_alert.html", alert=Alert.find_by_id(alert_id, session['email']))


@alert_blueprint.route("/delete/<string:alert_id>")
@requires_login
def delete_alert(alert_id):
    alert = Alert.find_by_id(alert_id, session['email'])
    if alert.user_email == session["email"]:
        Alert.remove_from_dynamo({
            'user_email': session['email'],
            '_id': alert_id
        }
        )
        return redirect(url_for(".index"))
