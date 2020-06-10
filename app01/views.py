from django.shortcuts import render, HttpResponse, redirect, reverse
from django.http import JsonResponse
from django.views import View
from django.contrib import auth
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random, string
from app01 import myforms, models


class RegView(View):
    def get(self, request):
        form_obj = myforms.RegForm()
        return render(request, 'register.html', locals())

    def post(self, request):
        back_info = {'code': 1000}
        form_obj = myforms.RegForm(request.POST)
        if form_obj.is_valid():
            cleaned_data = form_obj.cleaned_data
            cleaned_data.pop('re_password')
            avatar = request.FILES.get('avatar')
            if avatar: cleaned_data['avatar'] = avatar
            models.UserInfo.objects.create_user(**cleaned_data)
            back_info['url'] = reverse('login')
        else:
            back_info['code'] = 2000
            back_info['msg'] = form_obj.errors

        return JsonResponse(back_info)


class LoginView(View):
    def get(self, request):
        form_obj = myforms.LoginForm()
        return render(request, 'login.html', locals())

    def post(self, request):
        back_info = {'code': 1000}
        form_obj = myforms.LoginForm(request.POST)
        if form_obj.is_valid():
            user_obj = auth.authenticate(request, **form_obj.cleaned_data)
            if user_obj:
                code = request.POST.get('code')
                if code.lower() == request.session.get('code'):
                    auth.login(request, user_obj)
                    return JsonResponse(back_info)
                else:
                    back_info['code'] = 2000
                    back_info['msg'] = {'id_code': '验证码错误'}
            else:
                back_info['code'] = 2000
                back_info['msg'] = form_obj.errors
        else:
            back_info['code'] = 2000
            back_info['msg'] = form_obj.errors
        return JsonResponse(back_info)


def get_code(request):

    def get_random():
        rgb_list = []
        for _ in range(3):
            rgb_list.append(random.randint(0, 255))
        return tuple(rgb_list)

    img_obj = Image.new('RGB', (380, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/font.ttf', 30)  # 字体样式 大小
    digits_letters = string.digits + string.ascii_letters
    code = ''.join(random.choices(digits_letters, k=5))
    for i in range(5):
        tmp = code[i]
        img_draw.text((i*60+60, -2), tmp, get_random(), img_font)

    request.session['code'] = code.lower()
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def index(request):
    return render(request, 'index.html', locals())

