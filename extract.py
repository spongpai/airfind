__author__ = 'siripening'

from bs4 import BeautifulSoup
import urllib2, csv,  rauth, time, difflib, random

def read_items(file_name):
    srch_id = []; item_id = []; title = []; address = []
    with open(file_name, 'rU') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #print (row['item_title'] + row['item_add1'] + row['item_add2'])
            srch_id.append(row['srch_id'])
            item_id.append(row['item_id'])
            title.append(row['item_title'])
            address.append(row['item_add1'] + ', ' + row['item_add2'])
    return srch_id, item_id, title, address

def get_search_params(title, address):
    params = {}
    params['term'] = title
    params['location'] = address
    return params

def get_search_parameters(lat,long):
    #See the Yelp API for more details
    params = {}
    params["term"] = "restaurant"
    params["ll"] = "{},{}".format(str(lat),str(long))
    params["radius_filter"] = "2000"
    params["limit"] = "10"
    return params

def get_results(params):
    #Obtain these from Yelp's manage access page
    consumer_key = "TQhDb_uU1TY2TCbfKYnbKQ"
    consumer_secret = "1gVacsYzGBBI3PKpvQV60nThXlI"
    token = "MFtCZ-CzfXpHAsZKGqVqEjIh8J5ishx_"
    token_secret = "elW9AmsljVhaU-gcYLNdVZDQajw"
    session = rauth.OAuth1Session(
        consumer_key = consumer_key
        ,consumer_secret = consumer_secret
        ,access_token = token
        ,access_token_secret = token_secret)
    request = session.get("http://api.yelp.com/v2/search",params=params)

    #Transforms the JSON API response into a Python dictionary
    data = request.json()
    session.close()

    return data

def get_phone_search_params(phone):
    #See the Yelp API for more details
    params = {}
    params["phone"] = phone
    return params


def get_business(params):
    #Obtain these from Yelp's manage access page
    consumer_key = "TQhDb_uU1TY2TCbfKYnbKQ"
    consumer_secret = "1gVacsYzGBBI3PKpvQV60nThXlI"
    token = "MFtCZ-CzfXpHAsZKGqVqEjIh8J5ishx_"
    token_secret = "elW9AmsljVhaU-gcYLNdVZDQajw"
    session = rauth.OAuth1Session(
        consumer_key = consumer_key
        ,consumer_secret = consumer_secret
        ,access_token = token
        ,access_token_secret = token_secret)
    request = session.get("http://api.yelp.com/v2/phone_search",params=params)

    #Transforms the JSON API response into a Python dictionary
    data = request.json()
    session.close()

    return data


def write_text(data):
    with open('test.txt', 'a') as fp:
        for d in data:
            #print d
            fp.write(d)

from datetime import datetime


def main(dir, input_file, deli, output_file, start, end, min_sleep, max_sleep):
    tstart = datetime.now()
    print 'start the process: ', tstart

    header = ['no', 'srch_id', 'item_id', 'input_title', 'input_address',
              'yelp_title', 'yelp_address', 'yelp_phone', 'match', 'sim_title', 'sim_address', 'sim_title_address',
              'price', 'review_count', 'avg_rate', '5star', '4star', '3star', '2star', '1star', 'first_review', 'url']

    biz_info_header = ['Takes Reservations', 'Delivery', 'Take-out', 'Accepts Credit Cards','Accepts Bitcoin',
              'Good For', 'Parking', 'Bike Parking', 'Wheelchair Accessible',
              'Good for Kids', 'Good for Groups', 'Attire','Ambience','Noise Level',
              'Alcohol', 'Outdoor Seating', 'Wi-Fi', 'Has TV', 'Waiter Service','Caters', 'Dogs Allowed',
              'Drive-Thru', 'Good For Dancing', 'Happy Hour', 'Smoking', 'biz_info', 'unknow_att']

    header_str =''
    for h in header:
        header_str += h + '\t'
    for b in biz_info_header:
        header_str += b + '\t'
    print header_str

    with open(dir+ '/' +output_file, 'a') as fp:
        fp.write(header_str + "\n")
    count = 0
    try:
        id, item_id, title, address = read_items(dir + '/' + input_file)
        result_list = []
        if start == '':
            start = 0
        if end == '':
            end = len(title)
        for i in range(start, end): #, len(title)):
            params = get_search_params(title[i], address[i])
            result = get_results(params)
            output = str(i) + deli + id[i] + deli + item_id[i] + deli + title[i] + deli + address[i] + deli
            count = count + 1
            yelp_dict = {'url':'', 'review':'', 'rate':''}
            if result and ('businesses' in result) and (len(result['businesses']) > 0):
                business = result['businesses'][0]
                yelp_dict['url'] = str(business['mobile_url'])
                yelp_dict['review'] = str(business['review_count'])
                yelp_dict['rate'] = str(business['rating'])
                biz_general, biz_info, rating = read_page(dir, item_id[i], yelp_dict['url'], biz_info_header)

                # find similarity value
                t1 = title[i]
                t2 = biz_general['yelp_title']
                a1 = address[i]
                a2 = biz_general['yelp_address']

                scoreT = difflib.SequenceMatcher(None,t1.lower(),t2.lower()).ratio()
                scoreA = difflib.SequenceMatcher(None,a1.lower(),a2.lower()).ratio()
                scoreTA = difflib.SequenceMatcher(None,(t1 + ',' + a1).lower(),(t2 + ',' + a2).lower()).ratio()
                if(scoreTA > 0.8):
                    match = '1'
                else:
                    match = '0'

                # print general info from yelp
                output += biz_general['yelp_title'] + deli + biz_general['yelp_address'] + deli + biz_general['yelp_phone'] \
                          + deli + match + deli + str(scoreT) + deli + str(scoreA) + deli + str(scoreTA) + deli \
                          + biz_general['price'] + deli + yelp_dict['review'] + deli + yelp_dict['rate'] + deli \
                          + rating[0] + deli + rating[1] + deli + rating[2] + deli + rating[3] + deli \
                          + rating[4] + deli + biz_general['first_review'] + deli + yelp_dict['url'] + deli

                # print business info from yelp
                for k in biz_info_header:
                    output += biz_info[k] + deli
                time.sleep(5)

                '''
                tend = datetime.now()
                diff = tend - tstart
                if diff.seconds > 3300:
                    print tend, " take a break!!! #items: ", str(count), ", running time: " , str(diff.seconds), " secs, ",  str(int(diff.seconds/ 60)), " mins"
                    time.sleep(600)
                    tstart = datetime.now()
                    count = 0
                    print tstart, " continue :)"
                else:
                    time.sleep(random.randint(min_sleep, max_sleep))
                '''
                '''
                if count%100 == 0:
                    time.sleep(300.0)
                else:
                    #time.sleep(30.0)
                    time.sleep(random.randint(min_sleep, max_sleep))
                '''
            print output
            output = output.encode('ascii', 'ignore')
            with open(dir + '/' + output_file, 'a') as fp:
                fp.write(output + "\n")
        return i, end, "DONE!!!"
    except ValueError as err:
        tend = datetime.now()
        diff = tend - tstart
        print err.args
        print "process end: ", str(tend)
        summary = "[mac] stop at: ", i, ", #items: ", str(count), ", running time: " , str(diff.seconds), " secs, ",  str(int(diff.seconds/ 60)), " mins"
        print summary
        return i, end, summary

def read_page(dir, id, url, biz_head):
    #url = 'http://www.yelp.com/biz/pizza-ville-restaurant-fond-du-lac'
    # add sort_by=date_asc to sort the reviews by date to find the earliest review (first review on yelp)
    page = urllib2.urlopen(url + '?sort_by=date_asc')
    page_content = page.read()
    soup = BeautifulSoup(page_content)

    h2 = soup.find('h2')
    if h2:
        content = soup.find('h2').get_text()
        if content and (content.find('Hey there') > -1):
            #print str(id) + ', stop!!' + content
            #exit()
            raise ValueError(str(id) + ', ' + content)
    #with open('fulldata/html/searchid_' + str(id) + '.html', 'w') as fid:
    #        fid.write(page_content)
    with open(dir + '/html/itemid_' + str(id) + '.html', 'w') as fid:
            fid.write(page_content)

    dict_general = {'yelp_title':'', 'yelp_address':'', 'yelp_phone':'', 'price':''}
    # get title
    title = soup.find('h1', class_='biz-page-title')
    if title:
        dict_general['yelp_title'] =  title.text.strip()

    # get address
    #address = soup.find('strong', class_='street-address')
    address = soup.find('address')
    if address:
        address_str = ''
        for add in address.children:
            address_str += add
        dict_general['yelp_address'] = address_str.strip()

    phone = soup.find('span', class_='biz-phone')
    if phone:
        dict_general['yelp_phone'] = phone.text.strip()

    # get price range
    price = soup.find('dd', class_='price-description')
    if price:
        dict_general['price'] = price.text.strip()

    # get biz info
    biz_info = soup.find('div', class_='short-def-list')

    # default biz value
    '''
    dict_bizinfo = {'Takes Reservations': '', 'Delivery':'', 'Take-out':'', 'Accepts Credit Cards':'', 'Accepts Bitcoin':'',
                    'Good For':'', 'Parking':'', 'Bike Parking':'', 'Wheelchair Accessible':'',
                    'Good for Kids':'', 'Good for Groups':'', 'Attire':'','Ambience':'','Noise Level':'',
                    'Alcohol':'', 'Outdoor Seating':'', 'Wi-Fi':'', 'Has TV':'', 'Waiter Service':'','Caters':''}
    '''
    dict_bizinfo = {}
    for b in biz_head:
        dict_bizinfo[b] = ''

    biz_keyval = ""
    biz_newatt = ""
    if biz_info:    # if biz info is found
        attribute_dt = biz_info.find_all('dt', class_='attribute-key')
        attribute_dd = biz_info.find_all('dd')

        i = 0
        for i in range(0, len(attribute_dt)):
            key = str(attribute_dt[i].get_text()).strip()
            val = str(attribute_dd[i].get_text()).strip()
            biz_keyval += key.strip() + ':' + val.strip() + ','
            if key in dict_bizinfo:
                dict_bizinfo[key] = val
            else:
                print '-------- new business info attribute ----------------- ' + key
                with open('new biz info', 'a') as fp:
                    fp.write(key + "\n")
                dict_bizinfo[key] = val
                biz_newatt += key + ':' + val + ','
    #print 'biz_keyval:' + biz_keyval
    dict_bizinfo['biz_info'] = biz_keyval
    dict_bizinfo['unknow_att'] = biz_newatt

    # get the first review published date
    key = 'datePublished" content="'
    index = page_content.find(key)
    if index != -1:
        dict_general['first_review'] = page_content[index + len(key): index + len(key) + 10]
    else:
        dict_general['first_review'] = ''

    # try to get rating detail
    try:
        # rating url
        rating_url = url + "/ratings_histogram/"
        page = urllib2.urlopen(rating_url)
        page_content = page.read()
        with open(dir + '/html/itemid_' + str(id) + '_ratings.html', 'w') as fid:
                fid.write(page_content)
        soup = BeautifulSoup(page_content)
        text = soup.get_text()
        rating = rating_histrogram(text)
    except ValueError as err:
        raise ValueError(str(id) + ', ' + err)

    return dict_general, dict_bizinfo, rating

def rating_histrogram(text):
    rating = []
    index = 0

    while index < len(text):
        # old layout, 'text-outside' class was used as a text style
        # index = text.find('text', index)
        # new layout (as of 06/04/2015), 'histogram_count' class was used as a text style
        index = text.find('histogram_count', index)
        if index == -1:
            break
        xx = text[index:index+40]
        ix = xx.find('u003e')
        iy = xx.find('\u003c')
        rating.append(xx[ix+5:iy])
        index += 4
    if rating == []:
        for i in range(0,5):
            rating.append('0')
    return rating

import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

def send_email(me, you, pwd, subj, text):

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (me, you, subj, text)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(me, pwd)
        server.sendmail(me, you, message)
        server.close()
        print 'successfully sent the mail'
    except ValueError as err:
        print "failed to send mail ", err


if __name__=="__main__":
    #main('fulldata/pizza_unique_all.csv', '\t', 'fulldata/result/biz_info.txt', 1774, 2000) #no.
    #read_page('xx', 'http://localhost/~siripening/searchid_613.html', biz_info_header)
    me = 'spongpai99@gmail.com'
    you = 'spongpai@gmail.com'
    pwd = ''
    # error: 2331
    start =2332
    end = 3000
    min_sleep = 10
    max_sleep = 20
    dir = 'food'
    while (start < end - 1):
        raw_input("Press Enter to continue")
        print (start, end, min_sleep, max_sleep)
        start, end, summary = main(dir, 'food_unique.csv', '\t', 'result/biz_info.txt', start, end, min_sleep, max_sleep)
        send_email(me, you, pwd, summary, "http://www.yelp.com/irvine-ca-us")

    # extract business info of pizza stores from yelp
    '''
    start = 9806
    end = 9808
    min_sleep = 10
    max_sleep = 20
    dir = 'fulldata'
    while (start < end - 1):
        raw_input("Press Enter to continue")
        print (start, end, min_sleep, max_sleep)
        start, end, summary = main(dir, 'pizza_unique_all.csv', '\t', 'result/biz_info.txt', start, end, min_sleep, max_sleep)
        send_email(me, you, pwd, summary, "http://www.yelp.com/irvine-ca-us")
    '''