import time
import os
import requests
import json
from bs4 import BeautifulSoup
import pymysql
import uuid


headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36','Accept-Language':'en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4'
           }
ss = requests.session()


#through Filmography_id to get cast list
def Filmography_cast_list(Filmography_id):
    cast_link = f"https://www.imdb.com/title/{Filmography_id}/fullcredits"
    cast_res = ss.get(cast_link, headers=headers)
    cast_soup = BeautifulSoup(cast_res.text, "html.parser")
    cast_list = []

    for i in range(len(cast_soup.select('table[class="cast_list"] a'))):
        try:
            cast_name = cast_soup.select('table[class="cast_list"] a')[i].img['alt']
            cast_list.append(cast_name)
        except:
            pass
    return cast_list

#through Filmography_link to get film score
def Filmography_score(Filmography_link):
    try:
        url = Filmography_link
        res = ss.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        rating_score = soup.select('div[class="ipc-button__text"] span')[0].text
        # rating_number = soup.select('div[class="AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3 jkCVKJ"]')[0].text
        score_number =rating_score
        return score_number
    except:
        return 'Null'
    
#through Filmography_link to get movie content
def  Filmography_content(Filmography_link):
    url = Filmography_link
    res = ss.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    try:
        content = soup.select('p[class="GenresAndPlot__OffsetPlot-cum89p-7 iuGjVe"] span')[0].text
        return content
    except:
        content = soup.select('p[class="GenresAndPlot__Plot-cum89p-6 bUyrda"] span')[0].text
        return content

#through Filmography_id to get the cover of movie, using uuid for saving file to local drive
def Filmography_image(Filmography_id,uuid1):
    url = f'https://www.imdb.com/title/{Filmography_id}'
    res = ss.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    image_link = 'https://www.imdb.com' + soup.select('a[class="ipc-lockup-overlay ipc-focusable"]')[0]['href']
    image_res = requests.get(image_link, headers=headers)
    image_soup = BeautifulSoup(image_res.text, "html.parser")
    try:
        image_url = image_soup.select('div[class="MediaViewerImagestyles__PortraitContainer-sc-1qk433p-2 iUyzNI"] img')[0]['src']
        image_content = requests.get(image_url)
        img = image_content.content
        with open(r'%s/%s.jpg' % (r'./static/images', uuid1), 'wb') as f:#requests download
            f.write(img) #requests download
    except:
        pass
    
#through searching_name(cast full name) to get the details of movie from IMDb
def IMDb_crawler_by_python(searching_name,cur): # can change searching name by yourself
    url = "https://www.imdb.com/find?q={}"
    res = ss.get(url.format(searching_name), headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    link_url = 'https://www.imdb.com' + soup.select('tr[class="findResult odd"]')[0].a['href']
    link_res = ss.get(link_url, headers=headers)
    link_soup = BeautifulSoup(link_res.text, 'html.parser')
    # print(link_soup)

    for i in range(len(link_soup.select('div[class="filmo-category-section"]')[0].select("div[id]"))):
        Filmography_title_id_list = link_soup.select('div[class="filmo-category-section"]')[0].select("div[id]")[i]
        Filmography_type = link_soup.select('div[class="filmo-category-section"]')[0].select("div[id]")[i].text
        if 'TV Series' in Filmography_type:
            pass
        elif 'Video Game' in Filmography_type:
            pass
        elif 'TV Mini Series' in Filmography_type:
            pass
        else:
            Filmography_title_id = Filmography_title_id_list['id']
            if len(Filmography_title_id) > 20:
                pass
            else:
                #film id
                Filmography_id = Filmography_title_id.split('-')[1]
                #film is released year
                Filmography_year = link_soup.select(f'div[id={Filmography_title_id}]')[0].span.text.strip()
                Filmography_title = link_soup.select(f'div[id={Filmography_title_id}]')[0].a.text
                Filmography_link = 'https://www.imdb.com' + link_soup.select(f'div[id={Filmography_title_id}]')[0].a['href']

                                               
                #don't insert data repeatly
                selectSql='''select movie_id from movie where movie_name = %s ;'''
                cur.execute(selectSql,Filmography_title)
                movie_data = cur.fetchall()
                isMovieExist =False
                for row in movie_data:
                    uuid12 = uuid.uuid1()
                    sql2 = '''INSERT INTO movie_actor_ref VALUES (%s,%s,%s,%s); '''
                    cur.execute(sql2,(uuid12,searching_name,str(row[0]),Filmography_title))
                    isMovieExist= True
                    
                if(isMovieExist):
                    continue
                
                #insert data to MySql the table of movie
                score = Filmography_score(Filmography_link)
                uuid1 = uuid.uuid1()
                sql1 = '''INSERT INTO movie VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s); '''
                cur.execute(sql1,(uuid1,Filmography_title,'',score,'','',Filmography_year,'https://www.tibame.com',0))
                
                Filmography_image(Filmography_id,uuid1)
                
                uuid12 = uuid.uuid1()
                sql2 = '''INSERT INTO movie_actor_ref VALUES (%s,%s,%s,%s); '''
                cur.execute(sql2,(uuid12,searching_name,uuid1,Filmography_title))
                print(Filmography_title)
                print('=======================')



if __name__ == "__main__":
    #connect MySQL by python
    import pymysql
    conn = pymysql.Connect(host='chatbot_db',
                            port=3306,
                            user='root',
                            passwd='123456',
                            db='TFB103d_azure',
                            charset='utf8')
    cur = conn.cursor()

    actor_name='Gal Gadot'

    IMDb_crawler_by_python(actor_name,cur)


