'''
Upload pics
'''
import matplotlib
matplotlib.use('Agg')
import datetime
from imgurpython import ImgurClient
client_id = '7e073260d098344'
client_secret = '75a31c61503bd934f884fbffe955fe6981f2285d'
album_id = 'utjyeVo'
access_token = '5152e80d42f915e6dacf7d342b2571e327c9cf3d'
refresh_token = 'c195cf62e30ef044fb85564310b76cf4b44d2c1c'

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
        imgurl = client.upload_from_path(fileName+'.jpg', config=config, anon=False)['link']
        #string to dict
        print("[log:INFO]Done upload. ")
    except :
        # if faild to upload
        imgurl = 'https://i.imgur.com/RFmkvQX.jpg'
        print("[log:ERROR]Unable upload ! ")
        
    
    return imgurl
