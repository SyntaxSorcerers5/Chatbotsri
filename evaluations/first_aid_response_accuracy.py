from sklearn.metrics import precision_score, recall_score, f1_score
import json

# Function to load the knowledge base
def load_knowledge_base(file_path="ground_truth.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: Knowledge base file not found!")
        return {}

# Function to preprocess text
def preprocess_text(text):
    return text.lower().split()

# Function to evaluate the chatbot's first aid accuracy
def evaluate_first_aid_accuracy(chatbot_response, ground_truth):
    chatbot_tokens = preprocess_text(" ".join(chatbot_response))
    ground_truth_tokens = preprocess_text(" ".join(ground_truth))

    y_true = [1 if word in ground_truth_tokens else 0 for word in chatbot_tokens]
    y_pred = [1] * len(chatbot_tokens)

    precision = precision_score(y_true, y_pred, zero_division=1)
    recall = recall_score(y_true, y_pred, zero_division=1)
    f1 = f1_score(y_true, y_pred, zero_division=1)

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

# Function to evaluate chatbot response against the knowledge base
def evaluate_chatbot_response(user_input, chatbot_response, knowledge_base):
    for accident_type, details in knowledge_base["accidents"].items():
        if any(keyword in user_input.lower() for keyword in details["keywords"]):
            ground_truth = details["ground_truth"]
            return evaluate_first_aid_accuracy(chatbot_response.split("\n"), ground_truth)
    return None

# Main program
if __name__ == "__main__":
    knowledge_base = load_knowledge_base()

    user_input = "How do I treat a burn?"
    chatbot_response = (
        "Cool the burn under running water for at least 10 minutes.\n"
        "Cover the burn with a sterile, non-fluffy dressing or cloth."
    )

    evaluation_results = evaluate_chatbot_response(user_input, chatbot_response, knowledge_base)
    if evaluation_results:
        print("Evaluation Results:")
        for metric, value in evaluation_results.items():
            print(f"{metric.capitalize()}: {value:.2f}")
    else:
        print("No matching accident type found in the knowledge base.")
