import os
import random

from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify, request, stream_with_context

from backend.extensions import create_logger
from backend.src.OpenRouter import OpenRouterClient

load_dotenv()

logger = create_logger(__name__, level="DEBUG")

poeltl = Blueprint("poeltl", __name__, url_prefix="/poeltl")

openrouter_client = OpenRouterClient(
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def pick_person():
    players = [
        "Paolo Banchero",
        "Scottie Barnes",
        "Jalen Brunson",
        "Tyrese Maxey",
        "Anthony Edwards",
        "Shai Gilgeous",
        "Tyrese Haliburton",
        "De'Aaron",
        "Jaren Jackson",
        "Lauri Markkanen",
        "Ja Morant",
        "Jarrett Allen",
        "LaMelo Ball",
        "Darius Garland",
        "Dejounte Murray",
        "Fred VanVleet",
        "Andrew Wiggins",
        "Jaylen Brown",
        "Julius Randle",
        "Zion Williamson",
        "Zach LaVine",
        "Mike Conley",
        "Bam Adebayo",
        "Pascal Siakam",
        "Trae Young",
        "Luka Dončić",
        "Donovan Mitchell",
        "Jayson Tatum",
        "Devin Booker",
        "Rudy Gobert",
        "Domantas Sabonis",
        "Brandon Ingram",
        "Nikola Vučević",
        "Nikola Jokić",
        "Ben Simmons",
        "Khris Middleton",
        "D'Angelo",
        "Joel Embiid",
        "Karl-Anthony",
        "Bradley Beal",
        "Victor Oladipo",
        "Goran Dragić",
        "Kristaps Porziņģis",
        "Giannis Antetokounmpo",
        "Kemba Walker",
        "Gordon Hayward",
        "DeAndre Jordan",
        "Andre Drummond",
        "Draymond Green",
        "Kawhi Leonard",
        "Isaiah Thomas",
        "Kyle Lowry",
        "Klay Thompson",
        "Jimmy Butler",
        "DeMarcus Cousins",
        "Kyle Korver",
        "Jeff Teague§",
        "DeMar DeRozan",
        "Anthony Davis",
        "Stephen Curry",
        "John Wall",
        "Paul Millsap",
        "Damian Lillard",
        "Jrue Holiday",
        "James Harden",
        "Kyrie Irving",
        "Paul George",
        "Joakim Noah",
        "Tyson Chandler",
        "Brook Lopez",
        "Marc Gasol§",
        "Roy Hibbert",
        "LaMarcus Aldridge",
        "Luol Deng",
        "Andrew Bynum",
        "Andre Iguodala",
        "Blake Griffin",
        "Russell Westbrook",
        "Kevin Love",
        "David Lee",
        "Zach Randolph",
        "Kevin Durant",
        "Rajon Rondo",
        "Derrick Rose",
        "Deron Williams",
        "Al Horford",
        "Chris Kaman",
        "Gerald Wallace",
    ]

    return random.choice(players)


@poeltl.route("/get-person", methods=["GET"])
def get_person():
    logger.info("Get person route accessed")
    try:
        person = pick_person()
        logger.debug(f"Selected person: {person}")
        return {"person": person}, 200
    except Exception as e:
        logger.error(f"Error picking person: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to pick person"}), 500


@poeltl.route("/ask", methods=["POST"])
def ask():
    """
    Chat endpoint for the 20 Questions bot.
    Expects a list of messages from the frontend including the system prompt and user/assistant history.
    """

    messages = request.json.get("messages", [])
    if not messages:
        return {"error": "No messages found"}, 400

    person = request.json.get("person")
    if person is None:
        return {"error": "Person not found"}, 400

    if not messages or not isinstance(messages, list):
        return {
            "error": "Invalid input. 'messages' must be a list of conversation messages."
        }, 400

    if not any(msg["role"] == "system" for msg in messages):
        system_prompt = (
            "You are pretending to be a specific person for a 20 Questions game. "
            "The user will try to guess who you are by asking yes/no questions. "
            "You should only allow the user to ask you yes/no questions, or very short answers providing minimal context, "
            "and nothing else (If the user specifically gives up/quits the game, you are allowed to tell them who you are). Stick strictly to the game and avoid discussing anything unrelated."
            "if the user answers correctly, give them a short congratulations message and elaborate on the person's background and career."
            "Here is the person you are pretending to be, as well as some information about them:"
            f"{person}"
        )
        messages.insert(0, {"role": "system", "content": system_prompt})

    stream = openrouter_client.chat(
        messages=messages,
        stream=True,
        max_tokens=50,  # Keep responses short for the yes/no nature
        temperature=0.7,
    )

    # Stream the response back to the client
    def yield_stream():
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content)
                yield chunk.choices[0].delta.content

    return Response(stream_with_context(yield_stream()))
