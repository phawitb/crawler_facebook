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
import configparser
# from webdriver_manager.chrome import ChromeDriverManager   #-------

if not os.path.exists('data/all'):
    os.makedirs('data/all')
if not os.path.exists('data/date'):
    os.makedirs('data/date')

MAX_COLLECT_EMOSION = 200
MAX_COLLECT_FOLLOW = 200

def get_config(key,l):
    config = configparser.ConfigParser()
    config.read('config.ini')
    values = config.get(key, l)
    values = values.split(',')
    values = [x.strip() for x in values if x]
    return values

def list_ixpath(l,i):
    list_xp = []
    for x in l:
        xx = x.split('{i}')
        list_xp.append(xx[0] + str(i) + xx[1])
    return(list_xp)

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
        elif red > 0.1 and blue < 0.001:
            label = 'care'
        elif not blue and not red:
            label = 'wow'
        elif blue and not red:
            label = 'sad'
        elif blue < 0.004 and 0.03 < red < 0.06:
            label = 'fun'
        elif blue < 0.009 and 0.001 < red < 0.004:
            label = 'angry'

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

def start_btn():
    global driver
    driver = webdriver.Chrome()
#     driver = webdriver.Chrome(ChromeDriverManager(version='108.0.5359.71').install())   #-----------------
    driver.get("https://www.facebook.com")
   
#     username = driver.find_element(By.NAME, 'email')
#     username.send_keys("")
#     password = driver.find_element(By.NAME, 'pass')
#     password.send_keys("")
#     password.send_keys(Keys.ENTER)


def add_target():
    e_text=box.get()
    print('addddd',e_text)

    TARGET_FBS = [e_text]
    person_NAME = json.load(open('fb_name.json'))
    for person in TARGET_FBS:
        if person not in person_NAME.keys(): 
            driver.get(person)
            fb_name = find_text(get_config('timeline_page','fb_name'))
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

def select_all():
    global ck_val
    for t in ck_val.keys():
        ck_val[t].select()
    print('select_all')
    
def gen_post_links(target_fb,N_TARGET):
    def get_link(i):
        post_link = list_ixpath(get_config('timeline_page','post_link'),i)
        for p in post_link:
            try:
                link = driver.find_element(By.XPATH,p).get_attribute("href")
                print(i,link)
                return link
            except:
                pass
        return None

    driver.get(target_fb)
    time.sleep(3)

    L = []
    i = 1
    while len(L) < N_TARGET and i < 2*N_TARGET:
        l = get_link(i)
        attemp = 0
        while not l and attemp < 10:
            driver.execute_script("window.scrollBy(0,500)","")
            time.sleep(0.1)
            l = get_link(i)
            attemp += 1
        if l:
            L.append(l)
        i +=1
    return L

def collect_postlinks():
    # status.config(text ='Start collect postlinks..')
    status.config(text ='Error! collect postlinks!')
    global TARGET_FBS
    ck = [x.get() for x in CB]

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

def window_scroll_down(scroll_time):
    source1 = driver.find_element(By.XPATH,get_config('emosion_page','tab_scrolling')[0])
    action = ActionChains(driver)
    for i in range(scroll_time):
        try:
            action.drag_and_drop_by_offset(source1, 0, 300).perform()
            time.sleep(1)
        except:
            pass
        
def find_text(xpaths):
    for x in xpaths:
        try:
            txt = driver.find_element(By.XPATH,x).text
            if txt:
                return txt
        except:
            pass
    return None

def find_text_c(xpaths,c):  #find text with constraint
    for x in xpaths:
        try:
            txt = driver.find_element(By.XPATH,x).text
            if txt == c:
                return txt,x
        except:
            pass
    return None,None

def find_src(xpaths):
    for x in xpaths:
        try:
            txt = driver.find_element(By.XPATH,x).get_attribute("src")
            return txt
        except:
            pass
    return None

def click_xpath(xpaths):
    for x in xpaths:
        try:
            txt = driver.find_element(By.XPATH,x)
            txt.click()
            return True
        except:
            pass
    return None

def get_detail(link):
    def get_fdetail(link):
        print(link)
        driver.get(link)
        time.sleep(3)
        location = ''
        creator = find_text(get_config('post_page','creator'))
        date = find_text(get_config('post_page','dates'))
        
        n_like = find_text(get_config('post_page','n_likes'))
        n_comment = find_text(get_config('post_page','n_comments'))
        n_share = find_text(get_config('post_page','n_shares'))
        texts = find_text(get_config('post_page','texts'))
        comments = []
        for i in range(1,51):
            c = find_text(list_ixpath(get_config('post_page','comment_persons'),i))  
            if c:
                comments.append(c)

        click_xpath(get_config('post_page','n_likes'))

        return date,n_like,n_comment,n_share,texts,comments,location,creator

    def get_emosions(N_target):
        def read_person(N_target):
            Emosions = {}
            P = []
            p = True
            i = 1
            while p and i <= N_target:
                emontion_person  =  list_ixpath(get_config('emosion_page','emontion_person'),i)
                emosion_icon  =  list_ixpath(get_config('emosion_page','emosion_icon'),i)

                p = find_text(emontion_person)

                if p:
                    icon_link = find_src(emosion_icon)
                    icon = find_emotion(icon_link)
    #                 print(icon,p)
                    try:
                        Emosions[icon].append(p)
                    except:
                        Emosions[icon] = [p]

                    P.append(p) 
                i+=1
            return P,Emosions

        attemp = 0
        persons = []
        while len(persons) < N_target and attemp < 10:
            persons,Emosions = read_person(N_target)
            print(len(persons))
            try:
                window_scroll_down(10)
            except:
                pass
            attemp += 1

        len(persons)
        return Emosions

    def gen_n_like(n_like):
        try:
            n_like = int(n_like)
            return n_like
        except:
            try:
                if n_like.split()[1] == 'หมื่น':
                    d = 10000
                elif n_like.split()[1] == 'พัน':
                    d = 1000
                elif n_like.split()[1] == 'แสน':
                    d = 100000
                elif n_like.split()[1] == 'ล้าน':
                    d = 1000000
                return int(float(n_like.split()[0])*d)
            except:
                return n_like
    
    date,n_like,n_comment,n_share,texts,comments,location,creator = get_fdetail(link)

    try:
        n_comment = int(n_comment.split()[1])
    except:
        pass
    try:
        n_share = int(n_share.split()[1])
    except:
        pass
    
    n_like = gen_n_like(n_like)
    if isinstance(n_like, int):
        if n_like > MAX_COLLECT_EMOSION:
            N_target_emosion = MAX_COLLECT_EMOSION
        else:
            N_target_emosion = n_like
    else:
        N_target_emosion = 10
    time.sleep(3)
    EMOTION = get_emosions(N_target_emosion)
    
    Detail = {
#         'creator' : creator,
#         'date' : create_date(date),
        'location' : location,
        'n_like' : n_like,
        'n_comment' : n_comment,
        'n_share' : n_share,
        'text' : texts,
        'comments' : comments,
        'emotions' : EMOTION,
        'link' : link,
#         'xcomments' : xcomments
    }
    
    return creator,create_date(date),Detail
        


def crawling_batch_btn():
    print('crawling........')
    # status.config(text ='Start crawling........')
    status.config(text ='Error! crawling!')
    POSTS = json.load(open('post_links.json'))
    LINKS = []
    for i in POSTS.keys():
        LINKS += POSTS[i]

    crawling(LINKS)


def crawling_one_btn():
    # status.config(text ='Start crawling........')
    status.config(text ='Error! crawling!')
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

        creator,date,Detail = get_detail(link)
        print('s-'*100)
        print('creator',creator)
        print('date',date)
        print('Detail',Detail)
        print('e='*100)

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

    status.config(text ='creawling finish!')
        
def isChecked():
    ck = [x.get() for x in CB]
    print(ck)

def gen_checkboxs():
    global CB,TARGET_FBS,ck_val
    TARGET_FBS = []
    person_NAME = json.load(open('fb_name.json'))
    ck_val = {}
    CB = []
    for i,k in enumerate(person_NAME.keys()):
        name = person_NAME[k]
        CB.append(BooleanVar())
        TARGET_FBS.append(k)
        # ck_val[k].destroy()
        if i%2 == 0:
            ck_val[k] = Checkbutton(text = name,variable = CB[i], onvalue=True, offvalue=False, command=isChecked)
            ck_val[k].grid(row=2+i//2, column=1,sticky=W)
        else:
            ck_val[k] = Checkbutton(text = name,variable = CB[i], onvalue=True, offvalue=False, command=isChecked)
            ck_val[k].grid(row=2+i//2, column=2,sticky=W)

def find_follow(target_fb,MAX_COLLECT_FOLLOW):
    driver.get(target_fb)
    time.sleep(3)
    
    sub_name0 = ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/span/a[1]']
    sub_name1 = ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/span/a[2]']
    sub_name0 = find_text(sub_name0)
    sub_name1 = find_text(sub_name1)

    print(sub_name0)
    print(sub_name1)

    dict_unit = {
        'พัน' : 1000,
        'หมื่น' : 10000,
        'แสน' : 100000, 
        'ล้าน' : 10000000
    }

    n_friend = None
    n_follower = None
    n_following = None
    n_mutual = None
    if sub_name0:
        if 'เพื่อน' in sub_name0.split():
            try:
                n_friend = int(float(sub_name0.split()[1])* dict_unit[sub_name0.split()[2]])
            except:
                n_friend = int(float(sub_name0.split()[1]))
                               
        elif 'ผู้ติดตาม' in sub_name0:
            try:
                n_follower = int(float(sub_name0.split()[1])* dict_unit[sub_name0.split()[2]])
            except:
                n_follower = int(float(sub_name0.split()[1]))           
        elif 'เพื่อนที่มีร่วมกัน' in sub_name0:
            n_mutual = int(float(sub_name0.split()[1]))

    if sub_name1 and 'กำลังติดตาม' in sub_name1:
        n_following = int(sub_name1.split()[0])

    print('n_friend',n_friend)
    print('n_follower',n_follower)
    print('n_following',n_following)
    print('n_mutual',n_mutual)
    
    follow = ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/a[4]/div[1]/span',
          '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div[2]/a[5]/div[1]/span',
         '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div[2]/a[3]/div/span',
         '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/a[3]/div[1]/span']

    t,x = find_text_c(follow,'เพื่อน')
    if x:
        print(t)
        click_xpath([x])
        time.sleep(2)
    else:
        t,x = find_text_c(follow,'ผู้ติดตาม')
        print(t)
        click_xpath([x])
        time.sleep(2)
    
        following = ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[2]/a[2]/div[1]/span']
        click_xpath(following)
        time.sleep(2)
    
    P = []
    i = 1
    ii = 1
    if n_following:
        n_follow = n_following
    elif n_friend:
        n_follow = n_friend
    elif n_mutual:
        n_follow = n_mutual
    else:
        n_follow = 10
    if n_follow > MAX_COLLECT_FOLLOW:
        n_follow = MAX_COLLECT_FOLLOW
    print(n_follow)


    while len(P) < n_follow and ii <= 2*n_follow:
        p = [f'/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[3]/div[{i}]/div[2]/div[1]/a/span']
        p = find_text(p)
        print(i,p)
        if p:
            P.append(p)
            i += 1
        else:
            driver.execute_script("window.scrollBy(0,500)","")
            time.sleep(1)
        ii += 1

    return P

def crawling_follow():
    # status.config(text ='Start crawling follow....')
    status.config(text ='Error! crawling follow!')
    ck = [x.get() for x in CB]
    TARGET_FB = [TARGET_FBS[x] for x in [i for i,x in enumerate(ck) if x]]
    print('TARGET_FB',TARGET_FB)

    for target_fb in TARGET_FB:
        follow = find_follow(target_fb,MAX_COLLECT_FOLLOW)
        person_NAME = json.load(open('fb_name.json'))
        fb_name = person_NAME[target_fb]
        print(fb_name,follow)

        current_date = str(datetime.date.today())

        if not os.path.exists(f'data/date/{current_date}'):
            os.makedirs(f'data/date/{current_date}')

        try:
            d1 = json.load(open(f"data/all/{fb_name}_follow.json"))
        except:
            d1 = {}
        d1[current_date] = {
            'follows' : follow
        }
        out_file = open(f"data/all/{fb_name}_follow.json", "w")
        json.dump(d1, out_file, indent = 6)
        out_file.close()

        try:
            d2 = json.load(open(f"data/date/{current_date}/{fb_name}_follow.json"))
        except:
            d2 = {}
        d2[current_date] = {
            'follows' : follow
        }
        out_file = open(f"data/date/{current_date}/{fb_name}_follow.json", "w")
        json.dump(d2, out_file, indent = 6)
        out_file.close()
    
    status.config(text ='Crawling follow finish!')

#----------------------------------------------------------------------------------------

CB = []

label_emotions = {}
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
window.geometry('1100x800')
window.config()

bt0 = Button(text="Add",command = add_target)
bt4 = Button(text="Delete",command = del_target)
bt7 = Button(text="Select All",command = select_all)
bt1 = Button(text='Start',command = start_btn)
bt5 = Button(text='Crawling current page',command=crawling_one_btn)
bt6 = Button(text='Crawling Folllow',command=crawling_follow)
bt2 = Button(text='1.Collect posts url',command=collect_postlinks)
bt3 = Button(text='2.Crawling Batch',command=crawling_batch_btn)

box = Entry()
status = Label(text='status : wevwevwevwevwevwdvwev')

Label(text='facebook link :').grid(row=0, column=0,sticky=E)
Label(text='collect posts :').grid(row=1, column=0,sticky=E)

box.grid(row=0, column=1,sticky=NW,ipadx=100,columnspan=2)
sc_var=StringVar()
scale_bar = Scale(variable=sc_var,from_=0, to=50, orient=HORIZONTAL).grid(row=1, column=1,sticky=EW,columnspan=2)
sc_var.set(1)

gen_checkboxs()

bt0.grid(row=0, column=3,sticky=EW)
bt4.grid(row=1, column=3,sticky=EW)
bt7.grid(row=2, column=3,sticky=EW)

bt1.grid(row=0, column=4,sticky=EW)
bt5.grid(row=1, column=4,sticky=EW)
bt6.grid(row=2, column=4,sticky=EW)
bt2.grid(row=4, column=4,sticky=EW)
bt3.grid(row=5, column=4,sticky=EW)
status.grid(row=6, column=4,sticky=EW)  #status.config(text ='')

status.config(text ='Press Start for login facebook')

mainloop()




# Checkbutton
# bt0.grid(row=0, column=0,sticky=EW,ipady=25)
# bt1.grid(row=1, column=0,sticky=EW,ipady=25)
# bt2.grid(row=2, column=0,sticky=EW,ipady=50)   # padx=10, pady=10,ipadx=50)
# bt3.grid(row=0, column=1, padx=10, pady=10,sticky=N)
# bt5.grid(row=1, column=1, padx=10, pady=10,columnspan=1,ipadx=10, ipady=10)
# bt6.grid(row=2, column=1, padx=10, pady=10,sticky=NW)


# dict_xpath = {
#     'fb_name' : get_config('timeline_page','fb_name'),
#     'post_link' : get_config('timeline_page','post_link'),
#     'creator' : get_config('post_page','creator'),
#     'dates' : get_config('post_page','dates'),
#     'n_likes' : get_config('post_page','n_likes'),
#     'n_comments' : get_config('post_page','n_comments'),
#     'n_shares' : get_config('post_page','n_shares'),
#     'texts' : get_config('post_page','texts'),
#     'comment_persons' : get_config('post_page','comment_persons'),
#     'tab_scrolling' : get_config('emosion_page','tab_scrolling')[0],
#     'emontion_person' : get_config('emosion_page','emontion_person'),
#     'emosion_icon' : get_config('emosion_page','emosion_icon')
    
# }

# dict_xpath = {
#     'fb_name' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[1]/div/div/span/div/h1',
#                 '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div/div/div[3]/div/div/div/div/div/div/span',
#                 '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div[2]/div/div/div[1]/h2/span/span'],
    
#     'post_link' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a',
#                 '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[2]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a',
#                 '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{i}]/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[3]/span/a',
#                 '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[3]/span/a',
#                 '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a',
#                 '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/div[2]/div/div/div[{i}]/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a',            
#                 '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/div[2]/div/div/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a',
#                 '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/div/div/div/div[{i}]/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a',
#                 '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/div/div/div/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a',
#                 '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/div[2]/div/div/div[{i}]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a'],
    
#     'creator' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/span/h2/span/a/strong/span',
#                 '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/span/h2/span/strong/span/a/span/span'],
#     'dates' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a/span',
#               '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[3]/span/a/span'],
#     'n_likes' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[2]/span/span',
#                 '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[1]/span/span',
#                 '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div[2]/div[1]/div[2]/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[2]',
#                 '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div/div/div[2]/div[1]/div/div[1]/div/div/div[2]/div[1]/div/div[1]/div/span/div/span[2]/span/span'],
#     'n_comments' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[2]/div[2]/span/div/span'],
#     'n_shares' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[2]/div[3]/span/div/span'],
#     'texts' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div/div/span/div'],
#     'comment_persons' : ['/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[2]/ul/li[{i}]/div[1]/div[2]/div[2]/div[1]/div[1]/div/div/span[1]/a/span/span',
#                   '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[2]/ul/li[{i}]/div[1]/div/div[2]/div/div[1]/div/div[1]/div/div/span/a/span/span',
#                   '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[2]/ul/li[{i}]/div[1]/div[2]/div[1]/div[1]/div/div/span/a/span/span',
#                   '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[2]/ul/li[{i}]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/span/a/span/span'],

#     'tab_scrolling' : '/html/body/div[1]/div[1]/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[3]',
#     'emontion_person' : ['/html/body/div[1]/div[1]/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[1]/div[{i}]/div/div/div[2]/div[1]/div/div/div/span/div/a'],
#     'emosion_icon' : ['/html/body/div[1]/div[1]/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[1]/div[{i}]/div/div/div[1]/div/a/div/div[2]/div/div[1]/img']
# }
