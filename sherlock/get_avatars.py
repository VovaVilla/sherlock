from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from time import sleep
from selenium.common.exceptions import TimeoutException
import os
from selenium.webdriver.chrome.options import Options


def getSourcePageUsingRequests(link):
    try:
        page = requests.get(link, timeout = 3)
        return page.content
    except:
        return None


def getSourcePageUsingSelenium(link):
    # add options for invisible chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    # browser = webdriver.Chrome()


    # firefox_options = webdriver.FirefoxOptions()
    # firefox_options.headless = True
    # # firefox_options.add_argument('--window-size=1920,1080')
    # # firefox_options.add_argument('--lang=en')
    # firefox_binary = r'C:\Program Files\Firefox Developer Edition\firefox.exe'
    # browser = webdriver.Firefox(firefox_binary=firefox_binary,
    #                                  firefox_options=firefox_options, executable_path='geckodriver/geckodriver')


    browser.set_page_load_timeout(10)
    try:
        try:
            browser.get(link)
            sleep(3)
        except TimeoutException:
            pass

        result = browser.page_source
        browser.quit()
        return result
    except:
        browser.quit()
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

        # page_source = getSourcePageUsingSelenium(user_data.get('user_link'))
        # image_link = findImageSrcFromSourcePage(page_source)
        # if image_link:
        #     return {'website_name': user_data.get('website_name'), 'user_link': user_data.get('user_link'),
        #             'avatar_link': image_link}

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

# if __name__ == "__main__":
#     res = getAvatarLink({'website_name': 'facebook', 'user_link': 'https://www.facebook.com/vovavilla'})
#     pass

# import requests
# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from time import sleep
# import os
# import requests
#
#
#
# def getSrcAvatarImage(parents_list, images_list):
#     # check fix words in elements
#     fix_words = ['avatar', 'profile', 'user', 'profile photo', 'фото профиля']
#
#     idx = 0
#     for parent in parents_list:
#         # if numbers child of parent > 8 -> ignore
#         if len(parent.find_elements_by_xpath(".//*")) > 8:
#             idx += 1
#             continue
#
#         for word in fix_words:
#             if word in parent.get_attribute('outerHTML').lower():
#                 result = images_list[idx].get_attribute('src')
#
#                 if 'mds.yandex.net' in str(result):
#                     continue
#
#                 if 'http' in str(result):
#                     return result
#         idx += 1
#     return None
#
#
# def getAvatarLinkSelenium(link):
#     browser = webdriver.Chrome()
#     browser.set_page_load_timeout(10)
#     try:
#         # get page
#         try:
#             browser.get(link)
#             sleep(3)
#         except TimeoutException:
#             pass
#
#         # get all images
#         images = browser.find_elements_by_tag_name('img')
#
#         #get first level parents of images
#         images_parents = []
#         for i in images:
#             images_parents.append(i.find_element_by_xpath('..'))
#
#         #get second level parents of images
#         images_parents_parents = []
#         for i in images_parents:
#             images_parents_parents.append(i.find_element_by_xpath('..'))
#
#         #get link
#         src = getSrcAvatarImage(images_parents, images)
#         if not src:
#             src = getSrcAvatarImage(images_parents_parents, images)
#
#         browser.quit()
#         return src if src else None
#     except Exception as e:
#         browser.quit()
#         return None
#
#
# def getAvatarFromLink(user_data: dict):
#     image_link = getAvatarLinkSelenium(user_data.get('user_link'))
#     return {'website_name': user_data.get('website_name'), 'user_link': user_data.get('user_link'), 'avatar_link': image_link}
#
#
# def downloadAvatars(user_data: dict, folder_name):
#     try:
#         try:
#             os.mkdir(folder_name)
#         except:
#             pass
#         for user in user_data:
#             if not user.get('avatar_link'):
#                 continue
#             img_data = requests.get(user.get('avatar_link')).content
#             file = open(f"{folder_name}/{user.get('website_name')}.jpg", 'wb+')
#             file.write(img_data)
#             file.close()
#     except Exception as e:
#         raise e
