
def rotten_tomato_score(actor_name,cur):
    import pymysql, json, requests
    from bs4 import BeautifulSoup
    

    userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    headers = {
        'User-Agent':userAgent
    }
	
    #adjust actor_name for searching
    names = actor_name.split(' ')
    name=''
    for i in names:
        if i != names[0]:
            name += "-"
        name += i

    
    urls = ['https://www.rottentomatoes.com/napi/search/all?type=movie&searchQuery=',
           'https://www.rottentomatoes.com/napi/search/all?after=MQ%3D%3D&type=movie&searchQuery=',
           'https://www.rottentomatoes.com/napi/search/all?after=Mg%3D%3D&type=movie&searchQuery=',
           'https://www.rottentomatoes.com/napi/search/all?after=Mw%3D%3D&type=movie&searchQuery=',
           'https://www.rottentomatoes.com/napi/search/all?after=NA%3D%3D&type=movie&searchQuery=']

    
    num = 0

    
    for url in urls:
        res = requests.get(url+name, headers=headers)
        movies = res.json()
        for movie in movies['movie']['items']:

            
            if movie['tomatometerScore']!={}:

                num += 1


                sql = '''UPDATE movie
                        SET tomato_rating = %s
                        WHERE movie_name = %s;
                        '''
                tomatoRating =float(movie['tomatometerScore']['score']) / 10
                cur.execute(sql,(tomatoRating, movie['name']))