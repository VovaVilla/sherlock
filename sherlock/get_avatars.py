"""
Sherlock: Find Usernames Across Social Networks Module

This module contains functions for searching and downloading
user avatars from social networks found by Sherlock
"""

from bs4 import BeautifulSoup
import requests
import os


def getSourcePageUsingRequests(link):
    try:
        page = requests.get(link, timeout=3)
        return page.content
    except:
        return None


def findImageSrcFromSourcePage(page_source, using_grandparents=False):
    # get links
    soup = BeautifulSoup(page_source, 'html.parser')
    images = soup.find_all('img')

    images_parents = []
    for i in images:
        images_parents.append(i.parent)

    if using_grandparents:
        # get second level parents of images
        images_parents_parents = []
        for i in images_parents:
            images_parents_parents.append(i.parent)
        images_parents = images_parents_parents

    # check fix words in elements
    fix_words = ['avatar', 'profile', 'user', 'profile photo', 'фото профиля']

    idx = 0
    for parent in images_parents:
        # if numbers child of parent > 8 -> ignore
        if len(parent.findChildren(recursive=True)) > 8:
            idx += 1
            continue

        result = None
        for word in fix_words:
            if word in str(parent).lower():
                try:
                    result = images[idx]['src']
                except Exception as e:
                    pass

                # yandex advertising may contain fix words
                if 'mds.yandex.net' in str(result):
                    continue

                if 'http' in str(result):
                    return result
        idx += 1

    if using_grandparents:
        return None
    else:
        return findImageSrcFromSourcePage(page_source, using_grandparents=True)


def getAvatarLink(user_data: dict):
    # site_name = user_data.get('website_name')
    # print(f'[-] Check Sherlock avatar on {site_name}')

    empty_result = {'website_name': user_data.get('website_name'), 'user_link': user_data.get('user_link'),
                    'avatar_link': None}

    exceptions_list = ['ebay', 'boingboing.net', 'askfm', 'gravatar', 'smule', 'wordpress', 'reddit', 'medium',
                       'tiktok', 'flickr', 'taringa', 'spotify']
    if user_data.get('website_name').lower() in exceptions_list:
        return empty_result

    try:
        page_source = getSourcePageUsingRequests(user_data.get('user_link'))
        image_link = findImageSrcFromSourcePage(page_source)
        if image_link:
            return {'website_name': user_data.get('website_name'), 'user_link': user_data.get('user_link'),
                    'avatar_link': image_link}
        return empty_result
    except:
        return empty_result


def downloadAvatars(user_data: dict, folder_name):
    try:
        try:
            os.mkdir(folder_name)
        except:
            pass
        for user in user_data:
            if not user.get('avatar_link'):
                continue
            try:
                img_data = requests.get(user.get('avatar_link')).content
            except:
                continue

            file = open(f"{folder_name}/{user.get('website_name')}.jpg", 'wb+')
            file.write(img_data)
            file.close()
    except Exception as e:
        return