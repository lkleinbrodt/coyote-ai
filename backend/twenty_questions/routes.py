from flask import jsonify, Blueprint, request, Response, stream_with_context
from backend.extensions import create_logger
from backend.config import Config
from openai import OpenAI
import random

logger = create_logger(__name__, level="DEBUG")

OPENAI_API_KEY = Config.TWENTY_QUESTIONS_OPENAI_API_KEY

twenty_questions = Blueprint(
    "twenty_questions", __name__, url_prefix="/twenty-questions"
)


@twenty_questions.route("/chat", methods=["POST"])
def chat():
    messages = request.json.get("messages", [])

    client = OpenAI(
        api_key=Config.TWENTY_QUESTIONS_OPENAI_API_KEY,
    )

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )

    def yield_stream():
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return Response(stream_with_context(yield_stream()))


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


@twenty_questions.route("/get-person", methods=["GET"])
def get_person():
    person = pick_person()
    return {"person": person}, 200


@twenty_questions.route("/ask", methods=["POST"])
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
            "and nothing else. Stick strictly to the game and avoid discussing anything unrelated."
            "Here is the person you are pretending to be, as well as some information about them:"
            f"{person}"
        )
        messages.insert(0, {"role": "system", "content": system_prompt})

    client = OpenAI(
        api_key=Config.TWENTY_QUESTIONS_OPENAI_API_KEY,
    )

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
        max_tokens=50,  # Keep responses short for the yes/no nature
        temperature=0.7,
    )

    # Stream the response back to the client
    def yield_stream():
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return Response(stream_with_context(yield_stream()))
