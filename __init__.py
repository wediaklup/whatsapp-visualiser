from datetime import datetime
from flask import Flask, render_template, send_from_directory, request, session, redirect
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


class Message:
    def __init__(self, content: str, author: str, sent: datetime):
        self.content = content
        self.author = author
        self.sent = sent


class SystemMessage:
    def __init__(self, content):
        self.content = content


def _parsearr(arr: list):
    output = []
    for line in arr:
        try:
            raw_datetime, raw_name_content = line.split("-", 1)
            sent = datetime.strptime(raw_datetime.strip(), "%d.%m.%y, %H:%M")
            author, message = raw_name_content.split(":", 1)
            output.append(Message(message.strip(), author.strip(), sent))
        except ValueError:
            output.append(SystemMessage(line.strip()))

    return output


def parse(fp, encoding="utf-8"):
    lines = fp.readlines()
    return _parsearr(lines)


def parses(text: str):
    return _parsearr(text.split("\n"))


@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        session["messages"] = request.files["messages"].stream.read().decode("utf-8")

    file_is_attached = bool(session.get("messages"))

    return render_template("index.html", file_is_attached=file_is_attached)


@app.route("/chat")
def chat():
    messages = session.get("messages")

    return render_template("chat.html", messages=messages)


@app.route("/clear")
def clear():
    session["messages"] = None
    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9980)
