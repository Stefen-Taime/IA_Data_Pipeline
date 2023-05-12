import os
import requests
import json
from pymongo import MongoClient
from flask import Flask, request, jsonify
import logging
from bson import ObjectId
from flask import json
import openai
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# Get API key from environment variable
api_key = os.getenv("OPENAI_KEY")
print(api_key)  # Debug: print the api_key
if not api_key:
    raise ValueError("Missing OpenAI API key")

# Set the OpenAI API key
openai.api_key = api_key

# Connect to MongoDB
client = MongoClient('mongodb+srv://<username>:<password>@cluster0.td8y4zr.mongodb.net/?retryWrites=true&w=majority')
db = client['booking']
collection = db['airbnb']

def process_query(query):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    # Use GPT-3 to process the query
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You can retrieve information from a database and present it to the user. You can communicate information about an apartment such as its title, location, price, availability, and the link to its page. The user will provide you with their requirements in the following format: 'city: city_name, budget: budget_amount, dates: start_date to end_date'."},
            {"role": "user", "content": query}
        ],
        max_tokens=100
    )

    # Get the desired information from the response
    processed_query = response.choices[0].message['content'].strip()

    return processed_query

def translate_to_mongo_query(processed_query):
    # Initialize the MongoDB query dictionary
    query_dict = {}

    # Search for city in the processed query
    city_search = re.search(r'city: (.*?),', processed_query, re.IGNORECASE)
    if city_search:
        query_dict['city'] = city_search.group(1).strip()

    # Search for budget in the processed query
    budget_search = re.search(r'budget: \$?(\d+)', processed_query, re.IGNORECASE)
    if budget_search:
        # Convert the budget to the same currency as in your database
        budget_in_dollars = int(budget_search.group(1))
        query_dict['price.value'] = {'$lte': budget_in_dollars}

    # Search for the dates in the processed query
    date_search = re.search(r'dates: (.*?) - (.*?)\.', processed_query, re.IGNORECASE)
    if date_search:
        # Format the dates string to match your database format
        dates_string = f"{date_search.group(1)} – {date_search.group(2)}"
        query_dict['subtitles'] = {"$regex": dates_string}

    return query_dict

def find_results(query):
    logger.debug('Starting to find results')

    # Use GPT-3 to understand the query
    processed_query = process_query(query)
    print("Processed Query:", processed_query)
    logger.debug('Processed query with GPT-3')

    # Translate the processed query into MongoDB query
    mongo_query = translate_to_mongo_query(processed_query)
    logger.debug('Translated query to MongoDB query')
    print("MongoDB query:", mongo_query)

    # Run the query and get the results
    results = collection.find(mongo_query).limit(5)  
    logger.debug('Got results from MongoDB')

    # Transform the results into a string, including less information for each result
    results_string = "\n".join([f"Apartment title: {result['title']}, price: {result['price']['value']}, link: {result['link']}" for result in results])

    return results_string

def generate_preamble():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Provide a friendly introduction to a list of apartment options."}
        ],
        max_tokens=100
    )

    # Get the generated preamble from the response
    preamble = response.choices[0].message['content'].strip()

    return preamble

def format_results(results):
    formatted_results = []
    for result in results:
        formatted_result = f"Title: {result['title']}\nCity: {result['city']}\nPrice: {result['price']['value']} {result['price']['currency']} per {result['price']['period']}\nDates: {', '.join(result['subtitles'])}\nRating: {result['rating']}\nLink: {result['link']}"
        formatted_results.append(formatted_result)
    return formatted_results

@app.route('/', methods=['POST'])
def home():
    try:
        data = request.get_json(force=True)
        query = data['query']

        # Get the results string from find_results
        results_string = find_results(query)

        # Create a GPT-3 prompt with the results
        prompt = f"{query}\n{results_string}"

        # Check if the total token count is within the model's limit
        total_tokens = len(query.split()) + len(results_string.split())
        if total_tokens > 4097:
            raise ValueError(f"Total token count ({total_tokens}) exceeds the model's limit (4097)")

        # Use GPT-3 to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
        )
        gpt3_response = response.choices[0].message['content'].strip()

        return jsonify({"response": gpt3_response})
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)

