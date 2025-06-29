from flask import ABC, request, jsonify
import os
app = ABC(__name__)
user_sessions = {}

MENU = {
    "1": "🛍️ Order Products",
    "2": "✂️ Grooming Appointment",
    "3": "🏨 Pet Hostel Booking",
    "4": "📞 Talk to Support"
}

@app.route('/whatsapp-bot', methods=['POST'])
def whatsapp_bot():
    incoming = request.json

    # Basic validation
    if not incoming or "sender" not in incoming or "message" not in incoming:
        return jsonify({"message": "❌ Invalid request format."}), 400

    user = incoming.get("sender")
    msg = incoming.get("message").strip().lower()
    session = user_sessions.get(user, {"step": 0, "service": None, "data": {}})

    reply = ""

    if session["step"] == 0:
        reply = (
            "👋 Welcome to *The Pets Cafe* 🐾\n"
            "Please choose an option:\n" +
            "\n".join([f"{k}. {v}" for k, v in MENU.items()])
        )
        session["step"] = 1

    elif session["step"] == 1:
        if msg in MENU:
            session["service"] = MENU[msg]
            if msg == "1":
                reply = "🛍️ What product would you like to order? (e.g., Dog Food, Bones)"
                session["step"] = "order_product"
            elif msg == "2":
                reply = "✂️ What type of grooming do you want?\nOptions: Basic / Premium / Haircut Only"
                session["step"] = "grooming_type"
            elif msg == "3":
                reply = "🏨 How many days do you want to book the hostel for?"
                session["step"] = "hostel_days"
            elif msg == "4":
                reply = "📞 Please call us directly at +91-XXXXXXXXXX"
                session["step"] = 0
        else:
            reply = "❌ Invalid option. Please type 1, 2, 3, or 4."

    # Order flow
    elif session["step"] == "order_product":
        session["data"]["product"] = msg
        reply = f"How much {msg} would you like to order?"
        session["step"] = "order_quantity"

    elif session["step"] == "order_quantity":
        session["data"]["quantity"] = msg
        reply = "📍 Please provide your delivery address:"
        session["step"] = "order_address"

    elif session["step"] == "order_address":
        session["data"]["address"] = msg
        d = session["data"]
        reply = (
            f"✅ Order Confirmed!\n"
            f"Product: {d['product']}\n"
            f"Quantity: {d['quantity']}\n"
            f"Delivery Address: {d['address']}\n"
            "Thank you for shopping with *The Pets Cafe* 🐾"
        )
        session = {"step": 0}

    # Grooming flow
    elif session["step"] == "grooming_type":
        session["data"]["grooming_type"] = msg
        reply = "📅 Please enter your preferred date for grooming (e.g., 02 July 2025):"
        session["step"] = "grooming_date"

    elif session["step"] == "grooming_date":
        session["data"]["grooming_date"] = msg
        reply = "⏰ What time would you prefer? (e.g., 11:00 AM):"
        session["step"] = "grooming_time"

    elif session["step"] == "grooming_time":
        session["data"]["grooming_time"] = msg
        d = session["data"]
        reply = (
            f"✅ Grooming Appointment Confirmed!\n"
            f"Service: {d['grooming_type']}\n"
            f"Date: {d['grooming_date']} at {d['grooming_time']}\n"
            "We look forward to pampering your pet! 🐶"
        )
        session = {"step": 0}

    # Hostel flow
    elif session["step"] == "hostel_days":
        session["data"]["days"] = msg
        reply = "📅 What date do you want the booking to start? (e.g., 01 July 2025):"
        session["step"] = "hostel_start_date"

    elif session["step"] == "hostel_start_date":
        session["data"]["start_date"] = msg
        reply = "🐕 Please share your pet's name:"
        session["step"] = "hostel_pet_name"

    elif session["step"] == "hostel_pet_name":
        session["data"]["pet_name"] = msg
        d = session["data"]
        reply = (
            f"✅ Hostel Booking Confirmed!\n"
            f"Pet: {d['pet_name']}\n"
            f"Start Date: {d['start_date']} for {d['days']} days\n"
            "We'll take great care of your fur baby! 🐾"
        )
        session = {"step": 0}

    user_sessions[user] = session
    return jsonify({"message": reply})

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
