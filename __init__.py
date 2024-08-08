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

    @staticmethod
    def is_system():
        return False


class SystemMessage:
    def __init__(self, content, sent: datetime):
        self.content = content
        self.sent = sent

    @staticmethod
    def is_system():
        return True


def _parsearr(arr: list):
    output = []
    for index, line in enumerate(arr):
        try:
            raw_datetime, raw_name_content = line.split("-", 1)
            sent = datetime.strptime(raw_datetime.strip(), "%d.%m.%y, %H:%M")

            if raw_name_content.strip().startswith("\u200e"):
                output.append(SystemMessage(raw_name_content.strip(), sent))

            author, message = raw_name_content.split(":", 1)

            # traversing following lines to see if they are just new lines in the same message
            i = index + 1
            while True:
                try:
                    # does the line follow the syntax of a new message?
                    child_raw_datetime, child_raw_name_content = arr[i].split("-", 1)
                    _ = datetime.strptime(child_raw_datetime.strip(), "%d.%m.%y, %H:%M")
                    _, child_message = child_raw_name_content.split(":", 1)
                    # print(f"({i}) breaking out from new message line")
                    break
                except ValueError:
                    # if it doesn’t, it’s either a system message or a lew line
                    # print(f"({i}) discovered new orphaned line")
                    try:
                        # is it a system message?
                        child_raw_datetime, child_content = arr[i].split("-", 1)
                        _ = datetime.strptime(child_raw_datetime.strip(), "%d.%m.%y, %H:%M")
                        # print(f"({i}) discovered new system message")
                        break
                    except ValueError:
                        # so it must be a new line that we append to the previous message
                        # print(f"({i}) discovered new message line")
                        message += "\n" + arr[i].strip()
                        i += 1
                except IndexError:
                    break

            output.append(Message(message.strip(), author.strip(), sent))
        except ValueError:
            pass

    return output


def parse(fp, encoding="utf-8"):
    lines = fp.readlines()
    return _parsearr(lines)


def parses(text: str):
    return _parsearr(text.split("\n"))


def get_messages():
    return parses(session.get("messages"))


@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        session["messages"] = request.files["messages"].stream.read().decode("utf-8")

    file_is_attached = bool(session.get("messages"))

    return render_template("index.html", file_is_attached=file_is_attached)


@app.route("/chat")
def chat():
    messages = get_messages()
    pov = "Rafael"

    message_count_by_user = {}
    for msg in messages:
        try:
            author = msg.author
        except AttributeError:
            continue

        if msg.author.startswith("\u200e"):
            author = msg.author.removeprefix("\u200e")

        try:
            message_count_by_user[author] += 1
        except KeyError:
            message_count_by_user[author] = 1

    user_ranking = sorted(message_count_by_user.items(), key=lambda item: item[1], reverse=True)

    return render_template("chat.html", messages=enumerate(messages), pov=pov, user_ranking=user_ranking)


@app.route("/test")
def test():
    return render_template("test-chat.html")


@app.route("/clear")
def clear():
    session["messages"] = None
    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9980)
