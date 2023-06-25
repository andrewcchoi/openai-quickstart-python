import os
import openai

from io import BytesIO
from flask import Flask, flash, redirect, render_template, request, url_for, json

app = Flask(__name__)
# app.config['SESSION_TYPE'] = 'memcached'
# app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000

openai.api_key = os.getenv("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        animal = request.form["animal"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(animal),
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


@app.route("/image", methods=("GET", "POST"))
def image():
    image = ""
    image_count = 2
    image_size = "512x512"
    if request.method == "POST":
        image = request.form.get("image", False)
        image_count = int(request.form.get("image_count", 2))
        image_size = request.form.get("image_size", "512x512")

        response = openai.Image.create(
            prompt=image,
            n = image_count,
            size = image_size,
        )
        
        result = {i: item["url"] for i, item in enumerate(response["data"])}
        result = json.dumps(result) # * changes json to string. during redirect json was truncated.
        return redirect(url_for("image", result=result, prompt=image, count=image_count, size=image_size))
    
    # * converts string back to json.
    if request.args.get("result", ""):
        result = json.loads(request.args.get("result", ""))
    else:
        result = ""
        
    image = request.args.get("prompt", "")
    image_count = int(request.args.get("count", 2))
    image_size = request.args.get("size", "512x512")
    return render_template("image.html", result=result, prompt=image, count=image_count, size=image_size)


@app.route("/variation", methods=("GET", "POST"))
def variation():
    file = ""
    image_count = 2
    image_size = "512x512"

    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        print(f"{file=}")
        
        # with open(file, "rb") as f:
        #     print(f.read())
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        image_count = int(request.form.get("image_count", 1))
        image_size = request.form.get("image_size", "256x256")
        filename = file.filename

        byte_stream: BytesIO = file
        byte_array = byte_stream.read()
        # byte_array = byte_stream.getvalue()
        response = openai.Image.create_variation(
            image=byte_array,
            n=image_count,
            size=image_size
        )
        
        result = json.dumps(response["data"]) # * changes json to string. during redirect json was truncated.
        return redirect(url_for("variation", result=result, filename=filename, count=image_count, size=image_size))
    
    # * converts string back to json.
    if request.args.get("result", ""):
        result = json.loads(request.args.get("result", ""))
    else:
        result = ""
        
    file = request.args.get("filename", "")
    image_count = int(request.args.get("count", 1))
    image_size = request.args.get("size", "256x256")
    return render_template("variation.html", result=result, filename=file, count=image_count, size=image_size)


def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.

Animal: Cat
Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
Animal: Dog
Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
Animal: {}
Names:""".format(
        animal.capitalize()
    )
