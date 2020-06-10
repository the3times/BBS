from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(verbose_name='手机号', null=True)
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.png')
    register_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    Blog = models.ForeignKey(to='Blog', null=True)


class Blog(models.Model):
    site_name = models.CharField(max_length=32, verbose_name='个人站点名')
    site_title = models.CharField(max_length=128, verbose_name='站点标题')
    site_theme = models.CharField(max_length=64, verbose_name='站点样式')


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='标签名')
    site = models.ForeignKey(to='Blog', null=True)


class Category(models.Model):
    name = models.CharField(max_length=32, verbose_name='分类名')
    site = models.ForeignKey(to='Blog', null=True)


class Article(models.Model):
    title = models.CharField(max_length=64, verbose_name='标题')
    desc = models.CharField(max_length=256, verbose_name='摘要')
    content = models.TextField(verbose_name='文章内容')
    publish_time = models.DateTimeField(auto_now_add=True)
    up_counts = models.BigIntegerField(verbose_name='点赞数')
    down_counts = models.BigIntegerField(verbose_name='点踩数')
    comment_counts = models.BigIntegerField(verbose_name='评论数')

    site = models.ForeignKey(to='Blog', null=True)
    category = models.ForeignKey(to='Category', null=True)
    tags = models.ManyToManyField(to='Tag', through='Article2Tag', through_fields=('article', 'tag'))


class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')


class UpDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField()


class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(max_length=256, verbose_name='评论内容')
    parent = models.ForeignKey(to='self', null=True)
