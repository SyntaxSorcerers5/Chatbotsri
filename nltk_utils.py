import string

import nltk
from fuzzywuzzy import fuzz
from nltk import WordNetLemmatizer, pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Initialize the lemmatizer and stop words
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def process_sentence(sentence):
    # Tokenize the sentence
    tokens = word_tokenize(sentence.lower())  # Convert to lowercase
    # Remove punctuation and stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in tokens if word not in stop_words and word not in string.punctuation]
    return words

# Bag of words function to convert sentence into a vector representation
def bag_of_words(sentences, words):
    bag = []
    for sentence in sentences:
        sentence_words = process_sentence(sentence)
        bag.append([1 if word in sentence_words else 0 for word in words])
    return bag

def preprocess_text(text):
    tokens = word_tokenize(text)
    return " ".join([word.lower() for word in tokens if word.lower() not in stop_words])

def fuzzy_match(user_input, keywords):
    input_processed = preprocess_text(user_input)
    max_score = 0
    best_match = None
    for keyword in keywords:
        score = fuzz.partial_ratio(input_processed, preprocess_text(keyword))
        if score > max_score:
            max_score = score
            best_match = keyword
    return max_score, best_match

def load_knowledge_base(file_path="knowledge_base.json"):
    with open(file_path, "r") as file:
        return json.load(file)
def tokenize(text: str) -> list[str]:
    """Tokenize the input text into words."""
    return word_tokenize(text)

def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove stop words from the token list."""
    return [word for word in tokens if word.lower() not in stop_words]

def lemmatize(tokens: list[str]) -> list[str]:
    """Lemmatize the token list."""
    lemmatized_tokens = []
    for token, tag in pos_tag(tokens):
        pos = get_wordnet_pos(tag)
        lemmatized_tokens.append(lemmatizer.lemmatize(token, pos))
    return lemmatized_tokens

def get_wordnet_pos(treebank_tag: str) -> str:
    """Convert Treebank POS tag to WordNet POS tag."""
    if treebank_tag.startswith('J'):
        return 'a'  # Adjective
    elif treebank_tag.startswith('V'):
        return 'v'  # Verb
    elif treebank_tag.startswith('N'):
        return 'n'  # Noun
    elif treebank_tag.startswith('R'):
        return 'r'  # Adverb
    else:
        return 'n'  # Default to noun if uncertain

def preprocess_text(text: str) -> list[str]:
    """Process the input text through tokenization, stop word removal, and lemmatization."""
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)
    return tokens

def prepare_data_for_model(texts: list[str]) -> list[list[str]]:
    """Prepare a list of texts for model training or prediction."""
    return [preprocess_text(text) for text in texts]

if __name__ == "__main__":
    sample_text = "This is an example sentence, demonstrating the preprocessing capabilities of this script."
    processed_text = preprocess_text(sample_text)
    print("Processed text:", processed_text)