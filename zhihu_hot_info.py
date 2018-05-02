import requests
import json
import time
import random
from lxml import etree
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.zhihu_db

headers = {
	# 'Cookie': 'q_c1=92c243e2be934a46be193b721a7640e1|1525241530000|1525241530000; capsion_ticket=2|1:0|10:1525241439|14:capsion_ticket|44:NjAzNDAxM2VmYzQ5NDlkMTk0OWJiY2IxYTI1ZjJiNzU=|2cea3eff2509ee18e74a19644f7924d98fdf9b5cff3ade938f3f685ae318b845; aliyungf_tc=AQAAAPFGJhXaegAAApb4cpjRP/23YZHq; z_c0=2|1:0|10:1525241484|4:z_c0|92:Mi4xZy0wakJ3QUFBQUFBMEtCOEdvMTdEUXdBQUFCZ0FsVk5qT01RV3dDUXhWSXY4anU1a3dyS2FSVFREeEk5ZnM4OXln|a67bf045207c49267ea6650da053819ad4e5d6294e44a2d033a6ef62bfc635a1; unlock_ticket=AGDhIelJ7gwMAAAAYAJVTZRd6VrW4hj2EBFEwi2fmCdc_woCetd-cw==',
	'User-Agent': 'com.zhihu.android/Futureve/5.14.2 Mozilla/5.0 (Linux; Android 4.4.2; OPPO R11 Build/NMF26X) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36',
	'Authorization': 'Bearer 2.1g-0jBwAAAAAA0KB8Go17DQwAAABgAlVNjOMQWwCQxVIv8ju5kwrKaRTTDxI9fs89yg',
}

def get_info(url):
	# url = 'https://api.zhihu.com/topstory/hot-list?limit=10'

	r = requests.get(url, headers=headers)
	j = r.json()
	# pprint(j)
	all_data =j.get('data')
	question_id_list = []
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
	    question_id_list.append(str(d['question_id']))
	    data_list.append(d)
	collection = db.question_info
	collection.insert_many(data_list)
	return question_id_list

"""
 'paging': {'is_end': False,
            'is_start': True,
            'next': 'https://api.zhihu.com/questions/275021771/answers?limit=10&offset=10',
            'previous': 'https://api.zhihu.com/questions/275021771/answers?limit=10&offset=0',
            'totals': 7199}}
"""

def get_answer(url):
	# url = 'https://api.zhihu.com/questions/{}/answers?limit=10&offset=0'.format(question_id)
	# https://www.zhihu.com/question/275360633/answer/380321597
	r = requests.get(url, headers=headers)
	time.sleep(random.random() * 1.5)
	j = r.json()
	all_answer = j.get('data')

	# answer_list = []
	for answer in all_answer:
		d = dict()
		pprint(answer)
		print('*'*25)
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
		# d['answer_url'] = answer.get('url')
		d['updated_time'] = answer.get('updated_time')
		d['answer_id'] = answer.get('id')
		d['answer_url'] = 'https://www.zhihu.com/question/{}/answer/{}'.format(d['question_id'], 
			d['answer_id'])
		# pprint(d)
		# answer_list.append(d)

		# collection_name = 'question_' + str(d['question_id'])
		# collection = db[collection_name]
		# collection.insert_one(d)
		yield d

	paging = j.get('paging')
	is_end = paging.get('is_end')
	if not is_end:
		next_url = paging.get('next')
		get_answer(next_url)


def get_answer_data(d):
	answer_url = d.get('answer_url')
	time.sleep(random.random() * 1.5)
	# 'https://api.zhihu.com/answers/378472913'
	# https://www.zhihu.com/question/{}/answer/{}
	r = requests.get(answer_url, headers=headers)

	# file_name = '_'.join(answer_url.split('/')[-4:]) + '.html'
	# with open(file_name, 'wb') as f:
	# 	f.write(r.content)
	# j = r.json()
	# pprint(j)
	html = etree.HTML(r.text)
	d['upvote_count'] = html.xpath('//meta[@itemprop="upvoteCount"]/@content')
	d['comment_count'] = html.xpath('//meta[@itemprop="commentCount"]/@content')
	d['date_created'] = html.xpath('//meta[@itemprop="dateCreated"]/@content')
	d['date_modified'] = html.xpath('//meta[@itemprop="dateModified"]/@content')
	d['content'] = '\r\n'.join(html.xpath('//div[@class="RichContent-inner"]//p//text()'))

	collection_name = 'question_' + str(d['question_id'])
	collection = db[collection_name]
	collection.insert_one(d)
	print('-'*30)


def main():
	index_url = 'https://api.zhihu.com/topstory/hot-list'
	# https://api.zhihu.com/questions/275360633/answers?order_by=&offset=5
	q_url = 'https://api.zhihu.com/questions/{}/answers?order_by=&offset=0'
	question_id_list = get_info(index_url)
	for q_id in question_id_list:
		full_q_url = q_url.format(q_id)
		for d in get_answer(full_q_url):
			get_answer_data(d)



if __name__ == '__main__':
	main()