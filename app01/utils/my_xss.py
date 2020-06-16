from bs4 import BeautifulSoup


def pre_xss(content):
    soup = BeautifulSoup(content, 'html.parser')
    tags = soup.find_all()
    for tag in tags:    # 获取所有的标签
        if tag.name == 'script':
            tag.decompose()  # 针对script标签 直接删除
    return soup
