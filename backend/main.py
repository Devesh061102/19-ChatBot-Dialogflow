from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper  # Assumed to handle database operations like inserting order data
import generic_helper  # Assumed to provide helper functions like extracting session_id

# Create a FastAPI application
app = FastAPI()

# Dictionary to store in-progress orders with session_id as the key
inprogress_orders = {}

# Route that handles POST requests (Dialogflow webhook)
@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data sent by Dialogflow
    payload = await request.json()

    # Extracting important details from the request payload
    intent = payload['queryResult']['intent']['displayName']  # The intent name (like "order.add")
    parameters = payload['queryResult']['parameters']  # Parameters from the user query (like food items, quantity)
    output_contexts = payload['queryResult']['outputContexts']  # Contexts maintained across conversation
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])  # Extract session_id from the context

    # Dictionary to map intent to corresponding handler function
    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        'order.remove - context: ongoing-order': remove_from_order,
        'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }

    # Call the appropriate handler based on the identified intent
    return intent_handler_dict[intent](parameters, session_id)

# Function to save the order to the database
def save_to_db(order: dict):
    # Get the next available order ID from the database
    next_order_id = db_helper.get_next_order_id()

    # Insert each item in the order along with its quantity into the database
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)
        
        # If there's a failure in inserting the item, return an error (-1)
        if rcode == -1:
            return -1

    # Insert the order tracking status (default: "in progress")
    db_helper.insert_order_tracking(next_order_id, "in progress")

    # Return the order ID for further use
    return next_order_id

# Function to complete the order and store it in the database
def complete_order(parameters: dict, session_id: str):
    # Check if the session has an in-progress order
    if session_id not in inprogress_orders:
        # If no order found for the session, return an error message
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order please?"
    else:
        # Retrieve the in-progress order for the session
        order = inprogress_orders[session_id]
        # Save the order to the database
        order_id = save_to_db(order)
        if order_id == -1:
            # If there was an error saving the order, return an error message
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            # Calculate the total price of the order
            order_total = db_helper.get_total_order_price(order_id)

            # Send the order confirmation message with order ID and total price
            fulfillment_text = f"Awesome. We have placed your order. " \
                               f"Here is your order id # {order_id}. " \
                               f"Your order total is {order_total}, which you can pay at the time of delivery!"

        # Clear the in-progress order for the session after completion
        del inprogress_orders[session_id]

    # Return the fulfillment message as a JSON response
    return JSONResponse(content={"fulfillmentText": fulfillment_text})

# Function to add items to the order
def add_to_order(parameters: dict, session_id: str):
    # If this is a new order, clear the previous session's order
    if session_id in inprogress_orders:
        del inprogress_orders[session_id]  # Clear previous order data

    # Extract food items and their quantities from the parameters
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    # Check if the lengths of food items and quantities match
    if len(food_items) != len(quantities):
        # If not, return an error message
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        # Create a dictionary of food items with their quantities
        new_food_dict = dict(zip(food_items, quantities))

        # Store the new order in the session
        inprogress_orders[session_id] = new_food_dict

        # Generate a string representation of the current order
        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"Your current order is: {order_str}. Do you need anything else?"

    # Return the updated order as a JSON response
    return JSONResponse(content={"fulfillmentText": fulfillment_text})

# Function to remove items from the order
def remove_from_order(parameters: dict, session_id: str):
    # Check if there's an order associated with the session
    if session_id not in inprogress_orders:
        # If not, return an error message
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Sorry! Can you place a new order please?"
        })
    
    # Extract food items from the parameters
    food_items = parameters["food-item"]
    # Retrieve the current order for the session
    current_order = inprogress_orders[session_id]

    removed_items = []  # List to store removed items
    no_such_items = []  # List to store items not found in the order

    # Attempt to remove specified items from the current order
    for item in food_items:
        if item not in current_order:
            # If an item isn't found, add it to the "not found" list
            no_such_items.append(item)
        else:
            # Otherwise, remove the item and add it to the "removed" list
            removed_items.append(item)
            del current_order[item]

    # Generate appropriate fulfillment messages based on removed/not found items
    if len(removed_items) > 0:
        fulfillment_text = f"Removed {', '.join(removed_items)} from your order!"

    if len(no_such_items) > 0:
        fulfillment_text += f" Your current order does not have {', '.join(no_such_items)}."

    # If the order is now empty, notify the user
    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        # Otherwise, list the remaining items in the order
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    # Return the updated order or empty status as a JSON response
    return JSONResponse(content={"fulfillmentText": fulfillment_text})

# Function to track the order status based on order ID
def track_order(parameters: dict, session_id: str):
    # Extract the order ID from the parameters
    order_id = int(parameters['order_id'])
    # Retrieve the status of the order from the database
    order_status = db_helper.get_order_status(order_id)
    
    # If the order is found, return its status
    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        # If the order isn't found, return an error message
        fulfillment_text = f"No order found with order id: {order_id}"

    # Return the order status as a JSON response
    return JSONResponse(content={"fulfillmentText": fulfillment_text})
