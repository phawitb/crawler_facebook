from tkinter import *
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import json
import os
import imutils
import cv2
import numpy as np
from matplotlib import pyplot as plt
import base64
from PIL import Image
from io import BytesIO

if not os.path.exists('data/all'):
    os.makedirs('data/all')
if not os.path.exists('data/date'):
    os.makedirs('data/date')

# def create_date(date):
#     print('=='*20)
#     print('date',date)
#     d = date.split()
#     if len(d) == 2:
#         date = str(datetime.date.today() + datetime.timedelta(days=-1*int(d[0])))
#     elif len(d) == 5:
#         date = f'{datetime.datetime.now().strftime("%Y")}-{month[d[1]]}-{d[0]} {d[3]}'
    
#     return date

def find_emotion(link):
    def mask_circle(img):
        w = int(np.average((img.shape[0],img.shape[1])))
        np.reshape(img,(w,w,3))
        mask = np.zeros_like(img)
        mask = cv2.circle(mask, (mask.shape[0]//2,mask.shape[0]//2), mask.shape[0]//2, (255,255,255), -1)
        masked = cv2.bitwise_and(img,mask)
        return masked

    def find_label(img):
        img = mask_circle(img)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0], None, [256], [0, 256])
        total = sum(hist)
        white = sum(hist[0:10])/total
        blue = sum(hist[95:105])/total
        red = sum(hist[166:186])/total
        label = ''
        if red > 0.4:
            label = 'love'
        elif blue > 0.1:
            label = 'like'
        elif red > 0.1 and not blue:
            label = 'care'
        elif not blue and not red:
            label = 'wow'
        elif blue and not red:
            label = 'sad'
        elif blue < 0.004 and 0.03 < red < 0.05:
            label = 'fun'
        elif blue < 0.009 and 0.001 < red < 0.004:
            label = 'angry'
        # else:
        #     label = 
    #     print('white,blue,red',white,blue,red,label)
        return label

    def base64_to_image(filename):
        f = open(filename, 'r')
        data = f.read()
        f.closed
        img = Image.open(BytesIO(base64.b64decode(data)))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img

    if link in label_emotions.keys():
        return label_emotions[link]
    else:
        img = imutils.url_to_image(link)
        e = find_label(img)
        if not e:
            e = link
        label_emotions[link] = e
        return e

def create_date(dd):
    if not dd:
        return None
    d = dd.split()
    if 'ชม.' in d:
        date = str(datetime.datetime.now() + datetime.timedelta(hours=-1*int(d[0])))
    elif 'วัน' in d:
        date = str(datetime.datetime.now() + datetime.timedelta(days=-1*int(d[0])))
    elif 'เวลา' in d:
        if len(d[0]) == 1: d[0] = '0'+d[0]
        date = f'{datetime.datetime.now().strftime("%Y")}-{month[d[1]]}-{d[0]} {d[3]}:00:000000'
    elif d[-1] in month:
        if len(d[0]) == 1: d[0] = '0'+d[0]
        date = f'{datetime.datetime.now().strftime("%Y")}-{month[d[1]]}-{d[0]} {str(datetime.datetime.now()).split()[-1]}'
    else:
        date = None
    return date

month = {
    'มกราคม' : 1,
    'กุมภาพันธ์' : 2,
    'มีนาคม' : 3,
    'เมษายน' : 4,
    'พฤษภาคม' : 5,
    'มิถุนายน' : 6,
    'กรกฎาคม' : 7,
    'สิงหาคม' : 8,
    'กันยายน' : 9,
    'ตุลาคม' : 10,
    'พฤศจิกายน' : 11,
    'ธันวาคม' : 12
}

window = Tk()
window.geometry('900x800')
window.config()

# driver = webdriver.Chrome()

def start_btn():
    global driver
    driver = webdriver.Chrome()
    driver.get("https://www.facebook.com")
   
    # username = driver.find_element(By.NAME, 'email')
    # username.send_keys("")
    # password = driver.find_element(By.NAME, 'pass')
    # password.send_keys("")
    # password.send_keys(Keys.ENTER)


def add_target():
    e_text=box.get()
    print('addddd',e_text)

    TARGET_FBS = [e_text]
    person_NAME = json.load(open('fb_name.json'))
    for person in TARGET_FBS:
        if person not in person_NAME.keys(): 
            driver.get(person)
            try:
                fb_name = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[1]/div/div/span/div/h1'
                fb_name = driver.find_element(By.XPATH,fb_name).text
            except:
                fb_name = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div/div/div[3]/div/div/div/div/div/div/span'
                fb_name = driver.find_element(By.XPATH,fb_name).text
            person_NAME[person] = fb_name

    out_file = open("fb_name.json", "w")
    json.dump(person_NAME, out_file, indent = 6)
    out_file.close()

    gen_checkboxs()
    box.delete(0, END)

def del_target():
    global TARGET_FBS,ck_val
    ck = [x.get() for x in CB]
    SELECT_FB = [TARGET_FBS[x] for x in [i for i,x in enumerate(ck) if x]]
    person_NAME = json.load(open('fb_name.json'))

    for t in ck_val.keys():
        ck_val[t].destroy()

    print('ck_val',ck_val)
    for t in SELECT_FB:
        del person_NAME[t]
        # ck_val[t].destroy()
        del ck_val[t]

    
    out_file = open("fb_name.json", "w")
    json.dump(person_NAME, out_file, indent = 6)
    out_file.close()

    for i in ck_val.keys():
        ck_val[i].destroy()

    

    gen_checkboxs()
    box.delete(0, END)
    

    

    # print('TARGET_FB',TARGET_FB)
    # print('person_NAME',person_NAME)


def gen_post_links(target_fb,N_TARGET):
    def get_link(i):
        link = None
        try:
            p = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{i}]/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a'
            link = driver.find_element(By.XPATH,p).get_attribute("href")
        except:
            try:
                p = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a'
                link = driver.find_element(By.XPATH,p).get_attribute("href")
            except:
                try:
                    p = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a'
                    link = driver.find_element(By.XPATH,p).get_attribute("href")
                except:
                    try:
                        p = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a'
                        link = driver.find_element(By.XPATH,p).get_attribute("href")
                    except:
                        try:
                            p = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[1]/div[{i+1}]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a'
                            link = driver.find_element(By.XPATH,p).get_attribute("href")
                        except:
                            try:
                                p = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a'
                                link = driver.find_element(By.XPATH,p).get_attribute("href")
                            except:
                                pass
                        pass
        return link

    def posts():
        POSTS = []
        for i in range(1,50):
            l = get_link(i)
            POSTS.append(l)

        return [x for x in POSTS if x]
    
    driver.get(target_fb)
    time.sleep(3)

    attemp = 0
    p = []
#     N_TARGET = 30
    while len(p) <= N_TARGET:
        if attemp > 10:
            break
        for i in range(10):
            driver.execute_script("window.scrollBy(0,500)","")
            time.sleep(0.1)
        attemp += 1
        p = posts()

    return p[:N_TARGET]

def collect_postlinks():
    status.config(text ='Start collect postlinks..')
    global TARGET_FBS
    ck = [x.get() for x in CB]

    # print('collect_postlinks',sc_var.get(),ck)
    # print('TARGET_FBS',TARGET_FBS)

    TARGET_FB = [TARGET_FBS[x] for x in [i for i,x in enumerate(ck) if x]]
    NUMBER_POSTS = int(sc_var.get())

    print('NUMBER_POSTS',NUMBER_POSTS,type(NUMBER_POSTS))
    print('TARGET_FB',TARGET_FB)

    POSTS = {}
    for target_fb in TARGET_FB:
        POSTS[target_fb] = gen_post_links(target_fb,NUMBER_POSTS)
        
    out_file = open("post_links.json", "w")
    json.dump(POSTS, out_file, indent = 6)
    out_file.close()

    status.config(text ='collect postlinks finish!')




#crawl........
# LIKE = ['https://web.facebook.com/reaction/image/1635855486666999/?size=20&scale=2']
# LOVE = ['https://web.facebook.com/reaction/image/1678524932434102/?size=20&scale=2']
# WOW = ['https://web.facebook.com/reaction/image/478547315650144/?size=20&scale=2']
# FUNNY = ['https://web.facebook.com/reaction/image/115940658764963/?size=20&scale=2']
# CARE = ['https://web.facebook.com/reaction/image/613557422527858/?size=20&scale=2']

label_emotions = {}

def window_scroll_down(scroll_time):
    source1 = driver.find_element(By.XPATH,'/html/body/div[1]/div[1]/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[3]')
    action = ActionChains(driver)
    for i in range(scroll_time):
        try:
            action.drag_and_drop_by_offset(source1, 0, 300).perform()
            time.sleep(1)
        except:
            pass
        
def get_detail(link):
    
    driver.get(link)
    
    try:
        location = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/span/h2/span/strong[3]/span/a/span/span'
        location = driver.find_element(By.XPATH,header).text
    except:
        location = None
    
    try:
        text = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[3]/div[1]/div/div/div/span/div/div'
        text = driver.find_element(By.XPATH,text).text
    except:
        text = None
    
    try:
        xn_like = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[2]/span/span'
        n_like = int(driver.find_element(By.XPATH,xn_like).text)
    except:
        try:
            xn_like = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[1]/span/span'
            n_like = int(driver.find_element(By.XPATH,xn_like).text)
        except:
            n_like = None
    
#     try:
#         n_comment = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div/div[1]/div/div[2]/div[2]/span/div/span'
#         n_comment = driver.find_element(By.XPATH,n_comment).text
#     except:
#         n_comment = None
        
#     try:
#         xcomments = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[2]/ul'
#         xcomments = driver.find_element(By.XPATH,xcomments).text
# #         print('comments :',comments)
#         c = xcomments.split('\n')
#         c = [x for i,x in enumerate(c) if 'ตอบกลับ' not in x and 'ถูกใจ' not in x]
#         comments = [x for i,x in enumerate(c) if i%3==0]
#     except:
#         comments = None
#         xcomments = None

    try:
        n_comment = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div/div[1]/div/div[2]/div[2]/span/div/span'
        n_comment = driver.find_element(By.XPATH,n_comment).text
        n_comment = int(n_comment.split()[1])
    except:
        n_comment = 0

    comments = []
    for i in range(1,n_comment+1):
        try:
            try:
                c = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[2]/ul/li[{i}]/div[1]/div[2]/div/div[1]/div/div/div/div/span/a/span/span'
                c = driver.find_element(By.XPATH,c).text
            except:
                try:
                    c = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[2]/ul/li[{i}]/div[1]/div[2]/div[1]/div[1]/div/div/span/a/span/span'
                    c = driver.find_element(By.XPATH,c).text
                except:
                    c = f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[2]/ul/li[{i}]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/span/a/span/span'
                    c = driver.find_element(By.XPATH,c).text
            comments.append(c)
        except:
            pass
    
    try:
        date = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a/span'
        date =  driver.find_element(By.XPATH,date).text
    except:
        date = None

    try:
        #     creator = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/span/h2/span/strong[1]/span/a/span/span'
        creator = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/span/h2/span/a/strong/span'
        creator = driver.find_element(By.XPATH,creator).text
    except:
        try:
            creator = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/span/h2/span/strong/span/a/span/span'
            creator = driver.find_element(By.XPATH,creator).text
        except:
            try:
                creator = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/span/h2/div/div'
                creator = driver.find_element(By.XPATH,creator).text
            except:
                creator = None
    #craw emotions

    try:
        driver.find_element(By.XPATH,xn_like).click()
    except:
        try:
            xn_like = '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[2]/span/span'
            driver.find_element(By.XPATH,xn_like).click()
        except:
            pass
        


    time.sleep(3)

    EMOTION = {}

    if n_like:
        for ii in range(0,7):
            e1 = f'/html/body/div[1]/div[1]/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[1]/div/div/div/div[2]/div[{ii}]/div'
            try:
                driver.find_element(By.XPATH,e1).click()
                time.sleep(1)

                n_emotion = int(driver.find_element(By.XPATH,e1).text)
                scroll_time = n_emotion//4
                window_scroll_down(scroll_time)

                icon_link = driver.find_element(By.XPATH,e1 + '[1]/div[1]/img').get_attribute("src")
                icon = find_emotion(icon_link)
                # if icon_link in LIKE:
                #     icon = 'like'
                # elif icon_link in LOVE:
                #     icon = 'love'
                # elif icon_link in WOW:
                #     icon = 'wow'
                # elif icon_link in FUNNY:
                #     icon = 'funny'
                # elif icon_link in CARE:
                #     icon = 'care'
                # else:
                #     icon = icon_link

                p = '/html/body/div[1]/div[1]/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[1]'
                person = [x for x in driver.find_element(By.XPATH,p).text.split('\n') if 'เพิ่มเป็นเพื่อน' not in x and 'มีเพื่อนร่วมกัน' not in x and 'ติดตาม' not in x and 'ส่งข้อความ' not in x]

    #             print(icon)
    #             print(n_emotion,len(person))
                EMOTION[icon] = {
                    'count' : n_emotion,
                    'person' : person
                }

            except:
                pass
        
    
    Detail = {
#         'creator' : creator,
#         'date' : create_date(date),
        'location' : location,
        'n_like' : n_like,
        'n_comment' : n_comment,
        'text' : text,
        'comments' : comments,
        'emotions' : EMOTION,
        'link' : link,
#         'xcomments' : xcomments
        
        
        
    }
    
    return creator,create_date(date),Detail
        


def crawling_batch_btn():
    print('crawling........')
    status.config(text ='Start crawling........')
    # POSTS = json.load(open('post_links.json'))
    # LINKS = []
    # for i in POSTS.keys():
    #     for ii in POSTS[i].keys():
    #         link = POSTS[i][ii]['link']
    #         LINKS.append(link)
    POSTS = json.load(open('post_links.json'))
    LINKS = []
    for i in POSTS.keys():
        LINKS += POSTS[i]

    crawling(LINKS)

    # D = {}

def crawling_one_btn():
    status.config(text ='Start crawling........')
    box_url = box.get()
    if box_url:
        LINKS = [box_url]
    else:
        LINKS = [driver.current_url]
   
    crawling(LINKS)


def crawling(LINKS):
    for link in LINKS:

        current_date = str(datetime.date.today())
        if not os.path.exists(f'data/date/{current_date}'):
            os.makedirs(f'data/date/{current_date}')

        if not os.path.exists(f'data/all'):
            os.makedirs(f'data/all')

        creator,date,Detail = get_detail(link)

        if date:
            
            try:
                d = json.load(open(f"data/all/{creator}.json"))
            except:
                d = {}
                
            try:
                d2 = json.load(open(f"data/date/{current_date}/{creator}.json"))
            except:
                d2 = {}
            
            
            
            
                
            d[date] = Detail
            out_file = open(f"data/all/{creator}.json", "w")
            json.dump(d, out_file, indent = 6)
            out_file.close()
            
            d2[date] = Detail

            
            out_file = open(f"data/date/{current_date}/{creator}.json", "w")
            json.dump(d2, out_file, indent = 6)
            out_file.close()
            
        #     if creator not in D.keys():
        #         D[creator] = {}
        #     D[creator][date] = Detail

            print('creator:',creator,'date:',date)
            print('Detail:',Detail)
            print('-'*50)

    status.config(text ='creawling finish!')
        
    # out_file = open(f"data/date/{str(datetime.datetime.now())}.json", "w")
    # json.dump(D, out_file, indent = 6)
    # out_file.close()

    

    


def isChecked():
    ck = [x.get() for x in CB]
    print(ck)
   



CB = []

def gen_checkboxs():
    global CB,TARGET_FBS,ck_val
    TARGET_FBS = []
    person_NAME = json.load(open('fb_name.json'))
    ck_val = {}
    CB = []
    for i,k in enumerate(person_NAME.keys()):
        name = person_NAME[k]
        # Checkbutton(text = name).grid(row=2+i, column=1,sticky=W)

        # CB[i] = BooleanVar()
        CB.append(BooleanVar())
        TARGET_FBS.append(k)


        # ck_val[k].destroy()
        
        if i%2 == 0:
            ck_val[k] = Checkbutton(text = name,variable = CB[i], onvalue=True, offvalue=False, command=isChecked)
            ck_val[k].grid(row=2+i//2, column=1,sticky=W)
        else:
            ck_val[k] = Checkbutton(text = name,variable = CB[i], onvalue=True, offvalue=False, command=isChecked)
            ck_val[k].grid(row=2+i//2, column=2,sticky=W)





bt0 = Button(text="Add",command = add_target)
bt4 = Button(text="Delete",command = del_target)
bt1 = Button(text='Start',command = start_btn)
bt5 = Button(text='Crawling current page',command=crawling_one_btn)
bt2 = Button(text='1.Collect posts url',command=collect_postlinks)
bt3 = Button(text='2.Crawling Batch',command=crawling_batch_btn)

box = Entry()
status = Label(text='status : wevwevwevwevwevwdvwev')

print('bt0',bt0)

Label(text='facebook link :').grid(row=0, column=0,sticky=E)
Label(text='collect posts :').grid(row=1, column=0,sticky=E)

box.grid(row=0, column=1,sticky=NW,ipadx=100,columnspan=2)
sc_var=StringVar()
scale_bar = Scale(variable=sc_var,from_=0, to=30, orient=HORIZONTAL).grid(row=1, column=1,sticky=EW,columnspan=2)
sc_var.set(1)

gen_checkboxs()


bt0.grid(row=0, column=3,sticky=EW)
bt4.grid(row=1, column=3,sticky=EW)

bt1.grid(row=0, column=4,sticky=EW)
bt5.grid(row=1, column=4,sticky=EW)
bt2.grid(row=3, column=4,sticky=EW)
bt3.grid(row=4, column=4,sticky=EW)
status.grid(row=5, column=4,sticky=EW)  #status.config(text ='')

status.config(text ='Press Start for login facebook')











mainloop()




# Checkbutton
# bt0.grid(row=0, column=0,sticky=EW,ipady=25)
# bt1.grid(row=1, column=0,sticky=EW,ipady=25)
# bt2.grid(row=2, column=0,sticky=EW,ipady=50)   # padx=10, pady=10,ipadx=50)
# bt3.grid(row=0, column=1, padx=10, pady=10,sticky=N)
# bt5.grid(row=1, column=1, padx=10, pady=10,columnspan=1,ipadx=10, ipady=10)
# bt6.grid(row=2, column=1, padx=10, pady=10,sticky=NW)