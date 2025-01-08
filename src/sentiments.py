from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

sentences = [
    "The stock market is performing exceptionally well today.",
    "Tesla faces backlash over safety concerns.",
    "Apple reported strong Q3 earnings, exceeding expectations."
]


def analyze_sentiment(text):
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=1)
    
    labels = ["Negative", "Neutral", "Positive"]
    sentiment = labels[torch.argmax(probabilities).item()]
    
    return sentiment, probabilities.detach().numpy()

for sentence in sentences:
    sentiment, probabilities = analyze_sentiment(sentence)
    print(f"Text: {sentence}")
    print(f"Sentiment: {sentiment}")
    print(f"Probabilities: Negative={probabilities[0][0]:.4f}, Neutral={probabilities[0][1]:.4f}, Positive={probabilities[0][2]:.4f}\n")
