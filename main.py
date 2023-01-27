import requests
import re
import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import json

def get_html(url):
    '''
    获取url信息
    get url information
    :param url:
    :return:
    '''
    r = requests.get(url)
    content = r.content
    html_str = str(content, encoding='utf-8')
    return html_str

def get_full_list(url):
    html = get_html(url)
    bs = BeautifulSoup(html, "html.parser")
    tt = bs.find_all(class_='tag')
    full_list = [(x.text, x['href'], int(x.find_parent().contents[-1].strip()[1:-1])) for x in tt]
    return full_list


def get_game_list():
    '''
    获取所有游戏的列表
    get a list of all game
    :return: list
    '''
    gamelist = get_full_list('https://archiveofourown.org/media/Video%20Games/fandoms')
    return gamelist

def get_movie_list():
    '''
    获取所有电影的列表
    get a list of all movie
    :return:
    '''
    movielist = get_full_list('https://archiveofourown.org/media/Movies/fandoms')
    return movielist

def get_related_page(url, page):
    '''
    获取某个电影或游戏的关联作品, 指定页码
    get fanart from specific game or movie, with selected page number
    :param url: 该电影的url
    url of the selected movie/game
    :param page: 页码
    page number
    :return:
    '''
    html = get_html('https://archiveofourown.org%s?page=%d'%(url,page))
    bs = BeautifulSoup(html, "html.parser")
    articles = bs.find_all(attrs={'role':'article'})
    get_text = lambda x: '' if x is None else x.text.strip()
    get_attr = lambda x,attr: '' if x is None else x[attr]
    article_info = []
    for article in articles:
        head = article.find(class_='header module')
        article_href = head.find('a')['href']
        article_name = get_text(head.find('a'))
        author_herf = get_attr(head.find(attrs={'rel':'author'}),'href')
        author_name = get_text(head.find(attrs={'rel':'author'}))
        tags_html = article.find(class_='tags commas').find_all('li')
        tags = []
        for t in tags_html:
            tags.append({
                'tag_type':t['class'][0],
                'text':get_text(t.find('a')),
                'href':get_attr(t.find('a'),'href'),
            })
        summary = get_text(article.find(class_='userstuff summary'))

        status = []
        for k,v in zip(article.find(class_='stats').find_all('dt'),article.find(class_='stats').find_all('dd')):
            k = get_text(k)[:-1]
            v = get_text(v)
            status.append((k,v))
        article_info.append({
            'article_href':article_href,
            'article_name':article_name,
            'author_herf':author_herf,
            'author_name':author_name,
            'tags':tags,
            'status':status,
            'summary':summary,
        })
    return article_info


def get_related(name, url, num):
    '''
    获取某个电影或游戏的关联作品
    get related work of a movie or a game
    :param name: 作品的名称
    name of the movie/game
    :param url: 该电影的url
    url of the movie/game
    :param num: 关联的数量
    how many related work you want to get
    :return:
    '''
    name, url, num = name, url, num
    article_info = []
    page_num = (num-1)//20+1
    for i in range(page_num):
        article_info += get_related_page(url, i+1)
    return article_info

def get_article_detail(url):
    '''
    获取某个文章的细节信息
    get detail information of an article
    :param url:
    the url of this article
    :return:
    '''
    html = get_html('https://archiveofourown.org%s?view_adult=true'%url)
    bs = BeautifulSoup(html, "html.parser")
    meta = bs.find(class_='work meta group')
    data = dict()

    get_text = lambda x: '' if x is None else x.text.strip()

    def stats_prcs(status_html):
        status = dict()
        for k, v in zip(status_html.find_all('dt'), status_html.find_all('dd')):
            k = k.text[:-1]
            v = v.text.strip()
            status[k] = v
        return status

    meta_proces_funcs = {
        'rating tags': lambda x: get_text(x.find(class_='tag')),
        'warning tags': lambda x: get_text(x.find(class_='tag')),
        'category tags': lambda x: get_text(x.find(class_='tag')),
        'fandom tags': lambda x: get_text(x.find(class_='tag')),
        'relationship tags': lambda x: [get_text(t) for t in x.find_all(class_='tag')],
        'character tags': lambda x: [get_text(t) for t in x.find_all(class_='tag')],
        'freeform tags': lambda x: [get_text(t) for t in x.find_all(class_='tag')],
        'language': lambda x: get_text(x),
        'stats': lambda x: stats_prcs(x),

    }
    if meta is not None:
        for k, v in zip(meta.find_all('dt'), meta.find_all('dd')):
            k = get_text(k)[:-1]
            v_type = v['class'] if isinstance(v['class'], str) else ' '.join(v['class'])
            v = get_text(v) if v_type not in meta_proces_funcs else meta_proces_funcs[v_type](v)
            data[k] = v



    data['title'] = get_text(bs.find(class_='title heading'))
    data['author'] = get_text(bs.find('a', attrs={'rel':'author'}))
    data['summary'] = get_text(bs.find(class_='summary module'))
    data['notes'] = get_text(bs.find(class_='notes module'))
    data['chapter'] = get_text(bs.find(id='chapters'))
    return data


def get_all_info(name, url, num):
    # 获取game_list或movie_list中某个作品关联文章的所有信息
    #get all information of a movie/game in game_list/movie_list 
    print('loading article list...')
    related_articles = get_related(name, url, num)
    print('total %s related'%len(related_articles))
    related_articles_detail = []
    for t in tqdm.tqdm(related_articles):
        related_articles_detail.append(get_article_detail(t['article_href']))
    return related_articles,related_articles_detail


game_list = get_game_list()
movie_list = get_movie_list()
def local_search(text):
    # 搜索作品名称
    #search by name of movie/game
    result = []
    for x in game_list+movie_list:
        if text in x[0]:
            result.append(x)
    return result

def onlin_search(text, page=1):
    '''
    搜索关键字, 指定页码
    search by word in selected page number
    :param text:关键字 the word you want to search
    :param page: 页码 page number
    :return:
    '''
    #这个搜索方式太死板
    #This searching method is too rigid. it requires the text to be exactly the name of the movie/game.
    html = get_html('https://archiveofourown.org/works/search?'+'page=%d'%page+'&utf8=%E2%9C%93&work_search%5Bquery%5D='+text)
    #html = get_html('https://archiveofourown.org%s?page=%d'%(url,page))
    bs = BeautifulSoup(html, "html.parser")
    articles = bs.find_all(attrs={'role':'article'})
    get_text = lambda x: '' if x is None else x.text.strip()
    get_attr = lambda x,attr: '' if x is None else x[attr]
    article_info = []
    for article in articles:
        head = article.find(class_='header module')
        article_href = head.find('a')['href']
        article_name = get_text(head.find('a'))
        author_herf = get_attr(head.find(attrs={'rel':'author'}),'href')
        author_name = get_text(head.find(attrs={'rel':'author'}))
        tags_html = article.find(class_='tags commas').find_all('li')
        tags = []
        for t in tags_html:
            tags.append({
                'tag_type':t['class'][0],
                'text':get_text(t.find('a')),
                'href':get_attr(t.find('a'),'href'),
            })
        summary = get_text(article.find(class_='userstuff summary'))

        status = []
        for k,v in zip(article.find(class_='stats').find_all('dt'),article.find(class_='stats').find_all('dd')):
            k = get_text(k)[:-1]
            v = get_text(v)
            status.append((k,v))
        article_info.append({
            'article_href':article_href,
            'article_name':article_name,
            'author_herf':author_herf,
            'author_name':author_name,
            'tags':tags,
            'status':status,
            'summary':summary,
        })
    return article_info


def get_data_Frame(detail):
    data = []
    for a in detail:
        t = []
        for b in a:
            t.append({
                'article_name':b.get('article_name',None),
                'author_name':b.get('author_name',None),
                'summary':b.get('summary',None),
            })
            if 'tags' in b:
                t[-1].update({d.get('tag_type',None):d.get('text',None) for d in b['tags']})
        data.append(t)
    data_pds = [pd.DataFrame(t) for t in data]
    return data_pds

if __name__ == '__main__':
    '''
    detail包括全量数据
    detail include all the data 
    data 是提取的数据
    data is the data we want: title, name of author, summary
    data_pds 是表格形式的数据
    data_pds is data organized in a dataframe
    '''
    
    witcherRelated=local_search('The Witcher')
    print('Showing search result of The Witcher')
    print()
    print(witcherRelated)
    print()
    #witcherRelated contains all works related to The Witcher

    #name, url, num = movie_list[1] 
    # 修改这里就能选择提取哪一个作品的信息,
    # modify this to choose which movie/game's information to extract, the code above should get the second movie in movie_list
    # now I want to get detail of articles about The Witcher
    # if any error appears, comment out the following line and uncommend line 252
    
    name, url, num = witcherRelated[1] 
    print('Getting related_articles and related_articles_detail of')
    print(witcherRelated[1])
    related_articles, related_articles_detail = get_all_info(name, url, num)

    json_str=json.dumps(related_articles)
    with open('related_articles.json','w') as json_file:
    	json_file.write(json_str)

    json_str=json.dumps(related_articles_detail)
    with open('related_articles_detail.json','w') as json_file:
    	json_file.write(json_str)


    #dataF = get_data_Frame(detail)
    # data = []
    # for a in detail:
    #     t = []
    #     for b in a:
    #         t.append({
    #             'article_name':b.get('article_name',None),
    #             'author_name':b.get('author_name',None),
    #             'summary':b.get('summary',None),
    #         })
    #         if 'tags' in b:
    #             t[-1].update({d.get('tag_type',None):d.get('text',None) for d in b['tags']})
    #     data.append(t)
    # data_pds = [pd.DataFrame(t) for t in data]

    # print("result of all information of The Witcher")
    # print()
    # print()
    # print(dataF)

 #    print("show game_list")
 #    print()
 #    print()

 #    print(game_list[:10])

 #    print()
 #    print()

	# print("show movie_list")
 #    print()
 #    print()

 #    print(movie_list[:10])
    
 #    print()
 #    print()

 #    print(detail[:2])
 #    print()
 #    print()

    #以上功能全部实现
    #the functions above are all impremented.

    #TODO: online search 还在开发

    #以下是user操作



