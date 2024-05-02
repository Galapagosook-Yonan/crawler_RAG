'''
네이버 식물백과 크롤링 후 csv로 저장하는 파일

네이버 식물백과는 글 부분과 이미지 부분이 나눠져있어서 이미지는 url로 저장함
'''

import csv
import requests
from bs4 import BeautifulSoup
import re

def crawl_naver_terms_with_images(url):
    response = requests.get(url)
    terms_with_images = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        for li in soup.select('ul.content_list > li'):
            term_info = {
                'title': '',
                'description': '',
                'details': [],
                'image_url': ''
            }

            title = li.find('strong', class_='title')
            if title and title.find('a'):
                term_info['title'] = title.find('a').text.strip()

            desc = li.find('p', class_='desc')
            if desc:
                term_info['description'] = desc.text.strip()

            related_info = li.find('div', class_='related')
            if related_info:
                for info in related_info.find_all('span', class_='info'):
                    detail = info.text.strip()
                    term_info['details'].append(detail)

            # 이미지 URL 추출
            image_tag = li.find('img')
            if image_tag and 'src' in image_tag.attrs:
                # 이미지 URL 추출을 위한 정규 표현식
                pattern = r'https://dthumb-phinf.pstatic.net/\?src=[^"]+'
                match = re.search(pattern, str(image_tag))
                if match:
                    # 이미지 URL이 있으면, 디코딩하여 추가
                    image_url = match.group().replace('&amp;', '&')
                    term_info['image_url'] = image_url
                else:
                    # 이미지 URL이 없으면, "이미지 없음"으로 표시
                    term_info['image_url'] = "이미지 없음"
            else:
                # 이미지 태그가 없으면, "이미지 없음"으로 표시
                term_info['image_url'] = "이미지 없음"

            terms_with_images.append(term_info)
    else:
        print("Error:", response.status_code)

    return terms_with_images

def save_to_csv(terms_data, filename):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'description', 'details', 'image_url'])
        writer.writeheader()
        for term in terms_data:
            writer.writerow(term)

    print(f"{filename}에 데이터 저장 완료.")

def crawl_pages(base_url, last_page):
    all_terms_with_images = []
    for page_number in range(1, last_page + 1):
        page_url = f"{base_url}&page={page_number}"
        print(f"Crawling page {page_number}...")  # 각 페이지 번호 출력
        terms_with_images = crawl_naver_terms_with_images(page_url)
        all_terms_with_images.extend(terms_with_images)
    return all_terms_with_images


if __name__ == "__main__":
    base_url = "https://terms.naver.com/list.naver?cid=46676&categoryId=46676"
    last_page = 5  # 끝 페이지 번호를 지정
    all_terms_with_images = crawl_pages(base_url, last_page)
    save_to_csv(all_terms_with_images, 'naver_terms_with_images.csv')