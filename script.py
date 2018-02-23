# -*- coding: utf-8 -*-
import os
import sys
import re
import argparse
import cfscrape
import random
import string
import requests
import threading

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--threads', type=int, default=4, help='кол-во тредов')
parser.add_argument('-c', '--charset', default=None, help='маска, см. README.md')
parser_args = parser.parse_args()

storage_file = 'skip.txt'
img_dir = 'img'
chset_val = {'?d': string.digits, '?s': string.ascii_lowercase, '?a': string.digits + string.ascii_lowercase}
scraper = cfscrape.create_scraper()
if not os.path.exists(storage_file):
    open(storage_file, 'a').close()
if not os.path.exists(img_dir):
    os.mkdir(img_dir)

def main():
    start_url = make_string(parser_args.charset)
    url = 'http://prnt.sc/' + start_url
    print('[*] обрабатывается {}'.format(url))
    img_link = scrape_link(url)
    if img_link:
        print('[+] найдено {}'.format(img_link))
        save(start_url, img_link)
    else:
        print('[-] неудача, продолжаем поиск')

def make_string(mask):
    skipfile = open(storage_file, 'r')
    skip = [item.strip() for item in skipfile]
    skipfile.close()
    while True:
        final_string = gen_string(mask) 
        if final_string not in skip:
            write_to_skip(final_string)
            return final_string
        
def gen_string(mask):
    random_str = str()
    if mask:
        input = re.findall(r'{([^\{\}]+)}', mask)
        for symbol in input:
            if symbol in chset_val:
                random_str += chset_val[symbol][random.randint(0,len(chset_val[symbol])-1)]
            else:
                chars = re.findall(r'([a-z]-[a-z]|[a-z])', symbol)
                nums = re.findall(r'([0-9]-[0-9]|[0-9])', symbol)
                full_charset = ''
                if chars:
                    chars = chars[0].split('-')
                    full_charset += chset_val['?s'][chset_val['?s'].index(chars[0]):chset_val['?s'].index(chars[::-1][0])+1]
                if nums:
                    nums = nums[0].split('-')
                    full_charset += chset_val['?d'][chset_val['?d'].index(nums[0]):chset_val['?d'].index(nums[::-1][0])+1]
                random_str += full_charset[random.randint(0, len(full_charset)-1)]
        random_str = random_str[:6]
    while len(random_str) < 6:
        random_str += chset_val['?a'][random.randint(0,len(chset_val['?a'])-1)]
    return random_str
    
def write_to_skip(link):
    with open('skip.txt', 'a') as storage_file:
        storage_file.write(link + '\n')

def scrape_link(link):
    web_content = scraper.get(link).content.decode('utf-8')
    image_prntscr = re.search('http[s]*://image.prntscr.com/image/\w+.png', web_content)
    image_imgur = re.search('http[s]*://i.imgur.com/\w+.png', web_content)
    if (image_prntscr or image_imgur):
        return (image_prntscr or image_imgur).group()

def save(start_url, img_link):
    img = requests.get(img_link)
    with open('{0}/{1}.png'.format(img_dir, start_url), 'wb') as file:
        file.write(img.content)

def loop():
    while True:
        try:
            main()
        except KeyboardInterrupt:
            sys.exit()

threads = {}
for i in range(parser_args.threads):
    threads[i] = threading.Thread(target=loop)
    threads[i].start()