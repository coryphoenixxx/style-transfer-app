from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .eval import eval_func
import os


def index(request):
    content_url = './images/default_content.jpg'
    style_url = './images/default_style.jpg'

    try:
        os.remove('./images/content.jpg')
        os.remove('./images/style.jpg')
    except FileNotFoundError:
        pass

    if request.method == 'POST':
        fs = FileSystemStorage()
        if request.FILES.get('content') and not request.FILES.get('style'):
            content_img = request.FILES['content']
            content_name = fs.save('content.jpg', content_img)
            content_url = '.' + fs.url(content_name)

        elif not request.FILES.get('content') and request.FILES.get('style'):
            style_img = request.FILES['style']
            style_name = fs.save('style.jpg', style_img)
            style_url = '.' + fs.url(style_name)

        elif request.FILES.get('content') and request.FILES.get('style'):
            content_img = request.FILES['content']
            style_img = request.FILES['style']
            content_name = fs.save('content.jpg', content_img)
            style_name = fs.save('style.jpg', style_img)
            content_url = '.' + fs.url(content_name)
            style_url = '.' + fs.url(style_name)

        eval_func(content_url, style_url)
        stylized_url = './images/stylized.jpg'
        return render(request, "index.html", {'content_url': content_url,
                                              'style_url': style_url,
                                              'stylized_url': stylized_url})

    return render(request, "index.html", {'content_url': content_url,
                                          'style_url': style_url
                                          })
