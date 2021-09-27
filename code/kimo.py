def KiMoScore_Desc(actor_name,cur):
    import requests,pymysql
    from bs4 import BeautifulSoup

    KiMo = []

    #using cast name for searching yahoo movie
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        "referer": 'https://movies.yahoo.com.tw/'}
    searchUrl = "https://movies.yahoo.com.tw/moviesearch_result.html?keyword={}&type=movie".format(actor_name)
    searchRes = requests.get(searchUrl, headers=headers)
    searchsoup = BeautifulSoup(searchRes.text, 'html.parser')
    #crawling the number of movie
    number =searchsoup.select_one("div.search_num._c span")
    total_num = number.text

    #crawling the link of movie
    page = 1
    movie_links = []
    while len(movie_links) < int(total_num):
        searchUrl = "https://movies.yahoo.com.tw/moviesearch_result.html?keyword={}&type=movie&page={}".format(actor_name, page)
        searchRes = requests.get(searchUrl, headers=headers)
        searchsoup = BeautifulSoup(searchRes.text, 'html.parser')
        # crawling the link of movie content
        NameAndLink = searchsoup.select("div.en a")
        for i in NameAndLink:
            movie_links.append(i["href"])
        page += 1
    
    #crawling the content of movie
    for movieUrl in movie_links:
        infoRes = requests.get(movieUrl, headers=headers)
        infosoup = BeautifulSoup(infoRes.text, 'html.parser')

        #crawling the name of movie
        MovieName = infosoup.select_one("div.movie_intro_info_r h3")
        name = MovieName.text

        #crawling the score of movie
        MovieScore = infosoup.select_one("div.score_num.count")
        score = float(MovieScore.text)
        
        #crawling the briefing of movie
        MovieIntro = infosoup.select_one("span#story")
        Intro = MovieIntro.text.split("\n            ")[1]

        # output list object [["movie_name","kimo_rating", "movie_desc"],...]
        KiMo.append([name,score,Intro,movieUrl])

        
        #if data is updated than run the code
        sql2 = '''UPDATE movie
                     SET movie_desc = %s ,
                         kimo_rating = %s ,
                         link = %s
                   WHERE movie_name = %s ;'''
        cur.execute(sql2,(Intro,score,movieUrl,name))
    return KiMo
#Test
# print(KiMoScore_Desc("Tom Hardy"))
# print(KiMoScore_Desc("Leonardo DiCaprio"))


if __name__ == "__main__":
    import pymysql
    conn = pymysql.Connect(host='chatbot_db',
                            port=3306,
                            user='root',
                            passwd='123456',
                            db='TFB103d_azure',
                            charset='utf8')
    cur = conn.cursor()

    actor_name='Pedro Pascal'

    KiMoScore_Desc(actor_name,cur)



