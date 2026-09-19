import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "nova_secret_key"
DATABASE = os.path.join(os.path.dirname(__file__), "Nova.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def ensure_database_schema():
    connection = get_db()
    columns = {
        row[1] for row in connection.execute("PRAGMA table_info(house)")
    }

    if "house_number" not in columns:
        connection.execute(
            "ALTER TABLE house ADD COLUMN house_number TEXT NOT NULL DEFAULT ''"
        )

    connection.commit()
    connection.close()


ensure_database_schema()


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    customer_id = request.form["customerID"].strip()
    password = request.form["password"]

    connection = get_db()
    customer = connection.execute(
        """
        SELECT customer_id, first_name, surname
        FROM customer
        WHERE customer_id = ? AND password = ?
        """,
        (customer_id, password),
    ).fetchone()
    connection.close()

    if customer:
        session["logged_in"] = True
        session["customer_id"] = customer["customer_id"]
        session["customer_name"] = (
            f"{customer['first_name']} {customer['surname']}"
        )
        return redirect("/dashboard")

    return render_template(
        "login.html",
        error="Invalid Customer ID or Password"
    )


@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):
        return redirect("/")

    connection = get_db()
    house = connection.execute(
        "SELECT * FROM house WHERE customer_id = ?",
        (session["customer_id"],),
    ).fetchone()

    bills = []
    if house:
        bills = connection.execute(
            "SELECT * FROM bills WHERE house_id = ?",
            (house["house_id"],),
        ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        customer_name=session["customer_name"],
        house=house,
        bills=bills,
    )


@app.route("/submit-reading", methods=["POST"])
def submit_reading():
    if not session.get("logged_in"):
        return redirect("/")

    utility_type = request.form["utility_type"].strip().lower()
    reading_text = request.form["reading"].strip()

    if utility_type not in {"gas", "electric"}:
        flash("Choose gas or electric.", "error")
        return redirect("/dashboard")

    try:
        reading = float(reading_text)
    except ValueError:
        flash("Enter a valid meter reading.", "error")
        return redirect("/dashboard")

    connection = get_db()
    house = connection.execute(
        "SELECT house_id FROM house WHERE customer_id = ?",
        (session["customer_id"],),
    ).fetchone()

    if house:
        connection.execute(
            """
            UPDATE bills
            SET latest_reading = ?
            WHERE house_id = ? AND utility_type = ?
            """,
            (reading, house["house_id"], utility_type),
        )
        if connection.total_changes:
            connection.commit()
            flash(f"{utility_type.title()} meter reading updated.", "success")
        else:
            flash(f"No {utility_type} bill is linked to this account.", "error")
    else:
        flash("No house is linked to this account.", "error")

    connection.close()
    return redirect("/dashboard")


@app.route("/update-address", methods=["POST"])
def update_address():
    if not session.get("logged_in"):
        return redirect("/")

    postcode = request.form["postcode"].strip()
    house_number = request.form["house_number"].strip()

    if not postcode or not house_number:
        flash("Enter both a postcode and house number.", "error")
        return redirect("/dashboard")

    connection = get_db()
    connection.execute(
        """
        UPDATE house
        SET postcode = ?, house_number = ?, move_date = DATE('now'), is_moving = 'Yes'
        WHERE customer_id = ?
        """,
        (postcode, house_number, session["customer_id"]),
    )
    connection.commit()
    connection.close()
    flash("Address updated.", "success")
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)