import requests
import json

url = 'https://www.aladin.co.kr/ttb/api/ItemSearch.aspx'
default_params={'ttbkey':'ttbhsubin971744001','Query':'수레 바퀴','output':'js','QueryType':'keyword','SearchTarget':'Book','Version':20131101,'MaxResults':20}
# QueryType=['Keyword','Title','Author', 'Publisher'] 필요없을듯.

def getBookLists(book, params=default_params):
    book_lists=None
    results=0
    keys={'publisher':'Publisher', 'author':'Author','title':'Title'}
    
    for key, keyword in {'title':'Title','author':'Author'}.items():
        if keyword in book.keys():
            book_lists,results=getBookswith(book[keyword])
        if results>0:
            del keys[key]
            break
    if results==0:
        book_lists=None
    return book_lists, keys

def getBookswith(keyword, params=default_params):
    params['Query']=keyword
    response=requests.get(url, params=params)
    if response.status_code == 200 and 'item' in response.text:
        response=json.loads(response.content)
        return response['item'], response['totalResults']
    return None, 0


def checkBookswith(books, key, keyword):
    for bk in books:
        if keyword in bk.keys():
            return bk
    return None

def chooseOneBook(book, books, rstKeys):
    choosedOne=None
    if books is None:
        book['ISBN']='error!'
        return book, True
    
    for key, keyword in rstKeys.items():
        if choosedOne is not None:
            break
        if keyword in book.keys():
            choosedOne=checkBookswith(books, key,book[keyword])

    if choosedOne is None:
        if 'title' in rstKeys:
            book['ISBN']='error!'
            book['etc']=(books[0]['title'],books[0]['cover'])
            return book, True
        choosedOne=books[0]

    book['ISBN']=choosedOne['isbn']
    book['Title']=choosedOne['title']
    book['Aladin']=choosedOne['link']
    book['Author']=choosedOne['author']
    book['image']=choosedOne['cover']
    return book, False