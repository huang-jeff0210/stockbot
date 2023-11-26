'''
Upload pics
'''
import matplotlib
matplotlib.use('Agg')
import datetime
from imgurpython import ImgurClient
client_id = '447033fdae16e0d'
client_secret = '54b7828028af07868ba2ce03779d2ae2c0360030'
album_id = 'utjyeVo'
access_token = 'c9b7bff6c4c86a091d52d54dd7c8ccd6d95bd288'
refresh_token = '59e144b544f1fc35aeb15982e436bd47f5f4deaa'

def showImgur(fileName):
    # connect imgur
    client= ImgurClient(client_id, client_secret, access_token, refresh_token)

    # params
    config = {
        'album': album_id, # album name
        'name': fileName, # pics name
        'title': fileName, # pics title
        'description': str(datetime.date.today())
        }
    
    # Upload file
    try:
        print("[log:INFO]Uploading image... ")
        imgurl = client.upload_from_path(fileName+'.png', config=config, anon=False)['link']
        #string to dict
        print("[log:INFO]Done upload. ")
    except :
        # if faild to upload
        imgurl = 'https://i.imgur.com/RFmkvQX.jpg'
        print("[log:ERROR]Unable upload ! ")
        
    
    return imgurl
