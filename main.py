import json
import os
import datetime
import spacy
from report_generator import generate_first_aid_report
from fuzzywuzzy import process
from flask import Flask
from flask import request
from waitress import serve
import json
from uuid import uuid4

app = Flask(__name__)

# Initialize spaCy model
nlp = spacy.load("en_core_web_md")

bot_name = "Advisor"
farewell_words = ["bye", "goodbye", "exit", "quit", "farewell"]


# Define functions as before, and update find_best_match

def load_knowledge_base(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['accidents']


def find_best_match(user_input: str, knowledge_base: dict) -> str | None:
    user_input_doc = nlp(user_input)
    best_match = None
    best_score = 0.0

    # Iterate over each accident's keywords to find the best match
    for accident_type, details in knowledge_base.items():
        for keyword in details["keywords"]:
            keyword_doc = nlp(keyword)
            similarity = user_input_doc.similarity(keyword_doc)

            # Update best match if this is the highest similarity score
            if similarity > best_score:
                best_score = similarity
                best_match = keyword

    return best_match if best_score >= 0.75 else None  # Using a threshold for similarity


def load_intents(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['intents']


# Store conversation function
def store_conversation(user_input: str, bot_response: str, conversation_log: list):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation_log.append({
        "timestamp": timestamp,
        "user_input": user_input,
        "bot_response": bot_response
    })


# Save conversation log to file
def save_conversation_log(conversation_log: list, convo_id:str = None):
    if convo_id is None:
        filename = f"conversation_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    else:
        filename = f"{convo_id}.txt"
    with open(filename, 'w') as file:
        json.dump(conversation_log, file, indent=4)
    print(f"Conversation log saved as {filename}")


# Initiate emergency contact (Stub function)
def initiate_emergency_contact():
    print("Emergency services contacted.")


# Chatbot functions
def find_best_match(user_input: str, knowledge_base: dict) -> str | None:
    all_keywords = [(keyword, accident) for accident in knowledge_base.values() for keyword in accident["keywords"]]
    best_match, best_score = process.extractOne(user_input, [kw[0] for kw in all_keywords])
    return best_match if best_score >= 70 else None


def get_responses_for_intent(intent: str, intents: dict) -> str | None:
    for intent_data in intents:
        if intent_data['tag'] == intent:
            return process.extractOne(intent, intent_data['responses'])[0]
    return None


def chat_bot(user_input):
    global pending_new_entry, latest_first_aid_interaction
    knowledge_base = load_knowledge_base('knowledge_base.json')
    intents = load_intents('intents.json')
    conversation_log = []

    # Check for farewell words to stop the conversation
    if user_input.lower() in farewell_words:
        return "Goodbye! Take care.", True

    # Check for intent responses first
    for intent_data in intents:
        if user_input.lower() in [pattern.lower() for pattern in intent_data['patterns']]:
            response = get_responses_for_intent(intent_data['tag'], intents)
            store_conversation(user_input, response, conversation_log)
            return response, False

    # Handle emergencies
    if user_input.lower() == 'emergency':
        initiate_emergency_contact()
        store_conversation(user_input, "Contacting emergency services...", conversation_log)
        return "Contacting emergency services...", False

    # Handle report generation
    if user_input.lower() == 'report':
        report_filename = f"first_aid_report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
        generate_first_aid_report(latest_first_aid_interaction, report_filename)
        return f"Generated first aid report: {report_filename}", False

    # Find best match in knowledge base
    best_match = find_best_match(user_input, knowledge_base)
    if best_match:
        for accident_type, details in knowledge_base.items():
            if best_match in details["keywords"]:
                response = f"Emergency Help: {details['emergency_help']}\n" \
                           f"First Aid Steps:\n" + "\n".join(details["first_aid"]) + "\n" \
                                                                                     f"Warning: {details['warning']}\n"
                store_conversation(user_input, response, conversation_log)
                latest_first_aid_interaction = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "accident_type": accident_type,
                    "first_aid_provided": response
                }
                return response, False

    # If no match found
    pending_new_entry = user_input
    return "I'm not sure how to help with that. Can you tell me more or provide the information?", False


conversations = {}


@app.route("/start", methods=["POST"])
def start_convo():
    convo_id = str(uuid4())
    conversations[convo_id] = []
    return json.dumps({"convo_id": convo_id})


@app.route("/load_convo/<convo_id>", methods=["GET"])
def load_convo(convo_id: str):
    print(convo_id)
    try:
        with open(f"{convo_id}.txt", 'r') as file:
            content = file.read()
            return json.dumps(content)
    except:
        return json.dumps({"error": "Could not retrieve conversation."})

@app.route("/", methods=["POST"])
def chat():
    payload = request.get_json()
    user_input = payload.get("message")
    convo_id = payload.get("convo_id")

    conversation_log = conversations.get(convo_id, None)

    if conversation_log is None:
        return json.dumps({"error": "Conversation not found"})

    response, should_exit = chat_bot(user_input)
    print(f"{bot_name}: {response}")

    # Store conversation and add to log
    store_conversation(user_input, response, conversation_log)

    # Exit if the farewell word is detected
    if should_exit:
        save_conversation_log(conversation_log, convo_id=convo_id)
        conversations.pop(convo_id, None)
    return json.dumps({"response": response})


def cli():
    print("Advisor: Welcome to the Virtual First Aid Advisor!")
    conversation_log = []
    while True:
        user_input = input("You: ")
        response, should_exit = chat_bot(user_input)
        print(f"{bot_name}: {response}")

        # Store conversation and add to log
        store_conversation(user_input, response, conversation_log)

        # Exit if the farewell word is detected
        if should_exit:
            save_conversation_log(conversation_log)
            break


if __name__ == '__main__':
    # cli()

    # Rest API
    print("Virtual First Aid Advisor, Started on Port 8080")
    serve(app=app, host="0.0.0.0", port=8080)
