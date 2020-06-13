from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from app01 import models, myforms


register = template.Library()


@register.inclusion_tag('side_bar.html', name='side_bar')
def side_bar(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 标签、分类、归档ORM查询
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article__pk')).values('pk', 'name', 'c')
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article__pk')).values('pk', 'name', 'c')
    # 日期归档查询使用django提供的TruncMonth自动按月截取，形成一个虚拟字段用于日期分组
    archive_list = models.Article.objects.filter(blog=blog). \
        annotate(month=TruncMonth('publish_time')).values('month'). \
        annotate(c=Count('pk')).order_by('-month').values('month', 'c')

    return locals()


@register.inclusion_tag('tmp_register.html')
def reg_form():
    form_obj = myforms.RegForm()
    return locals()