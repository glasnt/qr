import io

from PIL import Image

import qrcode 
import qrcode.image.svg

from django.shortcuts import render

SCALE = 10

def index(request):
    # Submitting a new string? redirect
    if request.method == "POST":
        return HttpResponseRedirect('/?code=' + request.POST.get('code'))

    # Code from querystring
    code = request.GET.get('code')

    if code is None:
        return render(request, 'index.html')

    chart = []

    # Make a QR code, and resize it to make it easily parsable. 
    im = qrcode.make(code)
    im = (im.transpose(Image.FLIP_TOP_BOTTOM)
            .transpose(Image.ROTATE_270))
    im = im.resize((int(im.width/SCALE), int(im.height/SCALE)))

    def cell(rgb, center_cell, highlight=False):
        cell = '<div class="color_cell %s" style="background-color: %s; color: %s ">%s</div>'
    
        add_style = "highlight_cell" if center_cell else ""

        # js implementation buggy
        #add_style += "red" if highlight else ""

        if rgb == 0:
            return cell % (add_style, '#000', 'lightgray', '–')
        else:
            return cell % (add_style, '#fff', 'black', '·')

    def grid(i):
        "Highlight if the grid is a special number"
        if i == 10:
            return True
        if i == im.height - 11:
            return True
    
    CENTER = True
    for x in range(0, im.width):
        row = []
        for y in range(0, im.height):

            center_cell = False
            highlight = False
            if CENTER:
                if im.height / 2 <= y and im.width / 2 <= x:
                    CENTER = False
                    center_cell = True
            if grid(x) or grid(y): 
                highlight = True
            rgb = im.getpixel((x, y))
            row.append(cell(rgb, center_cell, highlight=highlight))
        chart.append("<div>" + "".join(row) + "</div>")

    # Ensure the chartdiv is large enough to chart, without wrapping
    chartholder = im.width * 20 + 100

    return render(request, 'index.html', {"code": code, "chart": "".join(chart), "chartholder": chartholder})
    
