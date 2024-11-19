import json
from sklearn.metrics import accuracy_score, f1_score


# Load intents data (for tagging intents)
def load_intents(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['intents']


# Function to simulate chatbot intent prediction
def predict_intent(user_input, intents):
    from fuzzywuzzy import process
    for intent_data in intents:
        best_match, score = process.extractOne(user_input, intent_data['patterns'])
        if score >= 70:  # Threshold for matching
            return intent_data['tag']
    return "noanswer"  # Default if no match is found


# Evaluate Intent Recognition Accuracy
def evaluate_intent_recognition(test_data, intents):
    predicted_intents = []
    true_intents = []

    for entry in test_data:
        user_input = entry['input']
        true_intent = entry['intent']
        true_intents.append(true_intent)

        # Predict intent
        predicted_intent = predict_intent(user_input, intents)
        predicted_intents.append(predicted_intent)

    # Calculate accuracy and F1-score
    accuracy = accuracy_score(true_intents, predicted_intents)
    f1 = f1_score(true_intents, predicted_intents, average='weighted')

    return accuracy, f1, predicted_intents, true_intents


# Load test dataset
def load_test_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['test_data']  # Make sure to return the list under 'test_data'


# Main Function
if __name__ == "__main__":
    intents = load_intents("../intents.json")  # Load chatbot intents
    test_data = load_test_data("test_data.json")  # Load test dataset

    # Evaluate intent recognition
    accuracy, f1, predicted_intents, true_intents = evaluate_intent_recognition(test_data, intents)

    # Print evaluation metrics
    print(f"Accuracy: {accuracy:.2f}")
    print(f"F1-Score: {f1:.2f}")

    # Display mismatches
    for i, (true, predicted) in enumerate(zip(true_intents, predicted_intents)):
        if true != predicted:
            print(f"Mismatch at index {i}:")
            print(f"  Input: {test_data[i]['input']}")
            print(f"  True Intent: {true}")
            print(f"  Predicted Intent: {predicted}")
