from django.shortcuts import render, HttpResponse, redirect, reverse
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db import transaction
from app01 import myforms, models
from app01.utils.mypagination import Pagination
from app01.utils.my_xss import pre_xss
from app01.utils.save_image import save_image

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random, string, json


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
            back_info['url'] = reverse('index')
        else:
            back_info['code'] = 2000
            back_info['msg'] = form_obj.errors

        return JsonResponse(back_info)


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', locals())

    def post(self, request):
        back_info = {'code': 1000}
        form_obj = myforms.LoginForm(request.POST)
        if form_obj.is_valid():
            code = request.POST.get('code')
            if code.lower() == request.session.get('code').lower():
                user_obj = auth.authenticate(request, **form_obj.cleaned_data)
                if user_obj:
                    auth.login(request, user_obj)
                    back_info['msg'] = '登录成功'
                    target_url = request.POST.get('target_url', 'login')
                    # 单纯的登录页面登录
                    if 'login' in target_url:
                        target_url = reverse('blog', args=(user_obj.username, ))
                    back_info['url'] = target_url
                else:
                    back_info['code'] = 3000
                    back_info['msg'] = '用户名或密码错误'
            else:
                back_info['code'] = 3000
                back_info['msg'] = '验证码错误'
        else:
            back_info['code'] = 2000
            back_info['msg'] = form_obj.errors
        return JsonResponse(back_info)


def get_user_avatar(request):
    if request.is_ajax() and request.method == 'POST':
        back_info = {'avatar': ''}
        username = request.POST.get('username')
        user_obj = models.UserInfo.objects.filter(username=username).first()
        # user_obj.avatar.name, 'avatar/xxx.png'
        user_avatar = user_obj.avatar.name if user_obj else '/avatar/default.png'
        back_info['avatar'] = user_avatar
        return JsonResponse(back_info)
    else:
        return render(request, 'error404.html')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')


@login_required
def reset_password(request):
    if request.is_ajax():
        back_info = {'code': 1000}
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        re_password = request.POST.get('re_password')
        if not request.user.check_password(old_password):
            back_info['code'] = 2000
            back_info['msg'] = '原密码错误'
        else:
            if new_password and re_password and new_password == re_password:
                request.user.set_password(re_password)
                request.user.save()
            else:
                back_info['code'] = 2000
                back_info['msg'] = '两次密码输入不一致或密码输入为空'
        return JsonResponse(back_info)
    else:
        return render(request, 'error404.html')


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
    print(code)
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def index(request):
    article_queryset = models.Article.objects.all()

    current_page = request.GET.get('page', 1)
    all_count = article_queryset.count()
    # 1 传值实例化对象
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    # 2 直接对总数据进行切片操作
    page_queryset = article_queryset[page_obj.start:page_obj.end]
    # 3 将page_queryset传递到页面，替换之前的book_queryset

    return render(request, 'index.html', locals())


def blog(request, username, **kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'error404.html')
    blog = user_obj.blog
    article_queryset = models.Article.objects.filter(blog=blog)
    # 按照标签、分类、归档条件查询文章的情况
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'tag':
            article_queryset = article_queryset.filter(tags__pk=param).all()
        elif condition == 'category':
            article_queryset = article_queryset.filter(category__pk=param).all()
        else:
            year, month = param.split('-')
            article_queryset = article_queryset.filter(publish_time__year=year,
                                                       publish_time__month=month).all()

    current_page = request.GET.get('page', 1)
    all_count = article_queryset.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    page_queryset = article_queryset[page_obj.start:page_obj.end]
    return render(request, 'blog.html', locals())


def article_detail(request, username, article_id):
    # 判断文章是否存在
    article_obj = models.Article.objects.filter(pk=article_id,
                                                blog__userinfo__username=username).first()
    # username对应的主键为article_id的文章不存在
    if not article_obj:
        return render(request, 'error404.html')
    comment_list = models.Comment.objects.filter(article__pk=article_id)
    # blog = article_obj.blog

    return render(request, 'article_detail.html', locals())


def up_and_down(request):
    if request.is_ajax() and request.method == 'POST':
        back_info = {'code': 1000}
        article_id = request.POST.get('article_id')
        is_up = json.loads(request.POST.get('is_up'))   # 反序列化成布尔型
        print(article_id, is_up)
        # 判断当前用户是否登录
        if request.user.is_authenticated:
            # 判断当前用户是否点赞自己的文章
            if not models.Article.objects.filter(pk=article_id, blog__userinfo=request.user):
                # 判断用户是否已经给这篇文章点过赞了
                if not models.UpDown.objects.filter(user=request.user, article__pk=article_id):
                    with transaction.atomic():
                        if is_up:
                            models.Article.objects.filter(pk=article_id).update(up_counts=F('up_counts')+1)
                        else:
                            models.Article.objects.filter(pk=article_id).update(down_counts=F('down_counts')+1)
                        models.UpDown.objects.create(user=request.user, article_id=article_id, is_up=is_up)
                        back_info['msg'] = '成功点赞' if is_up else '成功点踩'
                else:
                    action = models.UpDown.objects.filter(user=request.user, article__pk=article_id).first().is_up
                    back_info['code'] = 1002
                    back_info['msg'] = '您已经点赞了' if action else '您已经点踩了'
            else:
                back_info['code'] = 1003
                back_info['msg'] = '不能给自己点赞哦'
        else:
            back_info['code'] = 1004
            back_info['msg'] = '不<a href="/login/">登录</a>不让点'
        return JsonResponse(back_info)
    else:
        return render(request, 'error404.html')


@login_required
def article_comment(request):
    if request.is_ajax():
        back_info = {'code': 1000}
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')

        if not content:
            back_info['code'] = 2000
            back_info['msg'] = '评论内容不能为空'
            return JsonResponse(back_info)
        with transaction.atomic():
            models.Article.objects.filter(pk=article_id).update(comment_counts=F('comment_counts')+1)
            models.Comment.objects.create(user=request.user, article_id=article_id, content=content, parent_id=parent_id)
            back_info['msg'] = '评论成功'
            return JsonResponse(back_info)
    else:
        return render(request, 'error404.html')


@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog__userinfo=request.user)
    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    page_queryset = article_list[page_obj.start:page_obj.end]

    return render(request, 'backend/backend.html', locals())


@login_required
def upload_img(request):
    back_info = {"error": 0}
    file_obj = request.FILES.get('imgFile')
    file_naw_path, file_new_name = save_image(file_obj)
    back_info['url'] = f'/media/images/{file_new_name}/'
    return JsonResponse(back_info)


@login_required
def change_avatar(request):
    if request.is_ajax():
        back_info = {'code':1000}
        avatar = request.FILES.get('avatar')
        request.user.avatar = avatar       # 自动拼接头像字段路径
        request.user.save()
        return JsonResponse(back_info)
    else:
        return render(request, 'error404.html')


class ArticleAddView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_list = models.Category.objects.filter(blog__userinfo=request.user)
        tag_list = models.Tag.objects.filter(blog__userinfo=request.user)
        return render(request, 'backend/article_add.html', locals())

    @method_decorator(login_required)
    def post(self, request):
        form_obj = myforms.ArticleAddForm(request.POST)
        if form_obj.is_valid():
            title = form_obj.cleaned_data.get('title')
            content = form_obj.cleaned_data.get('content')
            # 预防xss攻击
            soup = pre_xss(content)
            category_id = request.POST.get('category')
            tag_id_list = request.POST.getlist('tag')
            with transaction.atomic():
                article_obj = models.Article.objects.create(title=title,
                                                            content=str(soup),        # 使用去除了script的文章内容
                                                            desc=soup.text[0:150],
                                                            blog=request.user.blog,
                                                            category_id=category_id)
                tag_tmp_list = (models.Article2Tag(article=article_obj, tag_id=tag) for tag in tag_id_list)
                models.Article2Tag.objects.bulk_create(tag_tmp_list)
            return redirect('backend')
        else:
            category_list = models.Category.objects.filter(blog__userinfo=request.user)
            tag_list = models.Tag.objects.filter(blog__userinfo=request.user)
            return render(request, 'backend/article_add.html', locals())


class ArticleEditView(View):
    @method_decorator(login_required)
    def get(self, request, article_id):
        article_obj = models.Article.objects.filter(pk=article_id).first()
        if not article_obj:
            return render(request, 'error404.html')
        form_obj = myforms.ArticleEditForm(initial={'title': article_obj.title,
                                                    'content': article_obj.content})
        category_list = models.Category.objects.filter(blog=request.user.blog)
        tag_list = models.Tag.objects.filter(blog=request.user.blog)
        return render(request, 'backend/article_edit.html', locals())

    @method_decorator(login_required)
    def post(self, request, article_id):
        form_obj = myforms.ArticleEditForm(request.POST)
        category_list = models.Category.objects.filter(blog=request.user.blog)
        tag_list = models.Tag.objects.filter(blog=request.user.blog)
        if form_obj.is_valid():
            title = form_obj.cleaned_data.get('title')
            content = form_obj.cleaned_data.get('content')
            soup = pre_xss(content)
            category = request.POST.get('category')
            tag_id_list = request.POST.getlist('tag')
            with transaction.atomic():
                models.Article.objects.filter(pk=article_id).\
                    update(title=title, content=str(soup), desc=soup.text[0:150], category_id=category)
                models.Article2Tag.objects.filter(article_id=article_id).delete()
                tag_tmp_list = (models.Article2Tag(article_id=article_id, tag_id=tag) for tag in tag_id_list)
                models.Article2Tag.objects.bulk_create(tag_tmp_list)
            return redirect('backend')
        return render(request, 'backend/article_edit.html', locals())

@login_required
def article_delete(request, article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    if not article_obj:
        return render(request, 'error404.html')
    article_obj.delete()
    return redirect('backend')

