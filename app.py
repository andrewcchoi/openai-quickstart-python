import os
import json
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


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
        image_url = response['data'][0]['url']
        # image_url = response # TODO: unable to show more than one image. need to fix.
        return redirect(url_for("image", result=image_url, prompt=image, count=image_count, size=image_size))

    result = request.args.get("result")
    image = request.args.get("prompt", "")
    image_count = int(request.args.get("count", 2))
    image_size = request.args.get("size", "512x512")
    return render_template("image.html", result=result, prompt=image, count=image_count, size=image_size)


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
