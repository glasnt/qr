import tempfile
from pathlib import Path
import os
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
import qrcode
from PIL import Image
from ih.chart import chart as ih_chart

app = Flask(__name__)
SCALE = 10


@app.route("/")
def main():
    query = request.args.get("q")
    if not query: 
        query = "Sample String"

    # Make a QR code, and resize it to make it easily parsable.
    im = qrcode.make(query)
    im = im.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
    im = im.resize((int(im.width / SCALE), int(im.height / SCALE)))

    # save it to a temp file
    tfn = Path("tmp", next(tempfile._get_candidate_names()) + ".png")
    im.save(tfn)

    # process through ih
    chart = ih_chart(
        image_name=tfn,
        scale=1,
        colours=2,
        save=False,
        guidelines=False,
        palette_name="floss",
        render=False,
    )

    # get out the style css and chart from the ih result
    soup = BeautifulSoup(chart, "html.parser")
    chart = soup.findAll("div", {"class": "chart"})[0]
    style = "\n".join(x.contents[0] for x in soup.findAll("style"))

    # do do do do
    return render_template("base.html", query=query, chart=chart, style=style)


@app.route("/generate", methods=["POST"])
def generate():
    q = request.form["q"]
    url = f"/?q={q}"
    return redirect(url)


if __name__ == "__main__":
    print(main)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
