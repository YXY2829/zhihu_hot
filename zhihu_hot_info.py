import requests
import json
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.zhihu_db

def get_info(url):
	# url = 'https://api.zhihu.com/topstory/hot-list?limit=10'

	headers = {
		'Cookie': 'aliyungf_tc=AQAAAEfwwzQLsQgAApb4cvj94waW0dUT',
		'User-Agent': 'com.zhihu.android/Futureve/5.14.2 Mozilla/5.0 (Linux; Android 4.4.2; OPPO R11 Build/NMF26X) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36',
		'Authorization': 'Bearer 2.1iyZ3CAAAAAAA0KB8Go17DQwAAABgAlVNzeoLWwA3BaZ3J_Lb_zT1YgRcDjW6DPJymg',
	}

	r = requests.get(url, headers=headers)
	j = r.json()
	# pprint(j)
	all_data =j.get('data')
	data_list = []
	for data in all_data:
	    d = dict()
	    d['detail_text'] = data.get('detail_text')
	    target = data.get('target', {})
	    d['answer_count'] = target.get('answer_count')
	    author = target.get('author')
	    d['author_name'] = author.get('name')
	    d['author_gender'] = author.get('gender')
	    d['headline'] = author.get('headline')
	    d['author_type'] = author.get('type')
	    d['author_url'] = author.get('url')
	    d['comment_count'] = target.get('comment_count')
	    d['created_time'] = target.get('created')
	    d['excerpt'] = target.get('excerpt')
	    d['follower_count'] = target.get('follower_count')
	    d['title'] = target.get('title')
	    d['question_id'] = target.get('id', '')
	    d['question_url'] = 'https://www.zhihu.com/question/' + str(d['question_id'])
	    data_list.append(d)
	collection = db.question_info
	collection.insert_many(data_list)
	return data_list

url = 'https://api.zhihu.com/topstory/hot-list'
data_list = get_info(url)
for da in data_list:
	pprint(da)


"""
 'paging': {'is_end': False,
            'is_start': True,
            'next': 'https://api.zhihu.com/questions/275021771/answers?limit=10&offset=10',
            'previous': 'https://api.zhihu.com/questions/275021771/answers?limit=10&offset=0',
            'totals': 7199}}
"""

def get_answer(url):
	# url = 'https://api.zhihu.com/questions/{}/answers?limit=10&offset=0'.format(question_id)
	r = requests.get(url, headers=headers)
	j = r.json()
	all_answer = j.get('data')

	answer_list = []
	for answer in all_answer:
		d = dict()
		author = answer.get('author', {})
		d['answer_author_name'] = author.get('name')
		d['answer_author_gender'] = author.get('gender')
		d['answer_author_headline'] = author.get('headline')
		d['answer_author_type'] = author.get('type')
		d['answer_author_url'] = author.get('url')
		d['answer_author_url_token'] = author.get('url_token')
		question = answer.get('question')
		d['question_id'] = question.get('id')
		d['question_title'] = question.get('title')
		d['answer_url'] = answer.get('url')
		d['updated_time'] = answer.get('updated_time')
		pprint(d)
		answer_list.append(d)

		collection_name = 'question_' + str(d['question_id'])
		collection = db[collection_name]
		collection.insert_many(answer_list)

	paging = j.get('paging')
	is_end = paging.get('is_end')
	if not is_end:
		next_url = paging.get('next')
		get_answer(next_url)


def get_answer_data(url):
	# 'https://api.zhihu.com/answers/378472913'
	r = requests.get(url, headers=headers)
	j = r.json()


def main():
	pass


if __name__ == '__main__':
	main()