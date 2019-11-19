from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
from pymongo import MongoClient
from itertools import islice
import json
import time


class TaobaoSpider:

	def __init__(self, username, password):

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
		self.web_driver = webdriver.Chrome(options = chrome_options)
		self.web_driver_wait = WebDriverWait(self.web_driver, 15)
		self.client = MongoClient('mongodb://localhost:27017/')

		self.url = 'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d9rqVarZ&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F'
		self.username = username
		self.password = password

	def login(self):

		self.web_driver.get(self.url)

		login_method_switch_button = self.web_driver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.login-box-warp .hd .login-switch')))
		login_method_switch_button.click()

		username_input = self.web_driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_Form .username-field #TPL_username_1')))
		username_input.send_keys(self.username)
		time.sleep(1)

		password_input = self.web_driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_Form .pwd-field #TPL_password_1')))
		password_input.send_keys(self.password)

		login_button = self.web_driver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_Form .submit .J_Submit')))
		login_button.click()

		name_tag = self.web_driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.site-nav-user .site-nav-login-info-nick')))
		print("Login Successful!", '\n', 'taobao ID is:', name_tag.text)
	
	def search(self, KEYWORD):

		keyword_input = self.web_driver_wait.until(EC.presence_of_element_located((By.ID, 'q')))
		keyword_input.send_keys(KEYWORD)

		search_button = self.web_driver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-search')))
		time.sleep(0.5)
		search_button.click()

	def get_pages(self):

		total_page_str = self.web_driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager .total')))
		total_page = int(total_page_str.text[2: -2])
		print("共", total_page, "页")

		for i in range(1, total_page + 1):
			print("正在爬取第", i, "页")

			try:
				if i > 1:
					page_input = self.web_driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager .form input.input.J_Input')))
					page_submit = self.web_driver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager .form span.btn.J_Submit')))
					page_input.clear()
					page_input.send_keys(i)
					time.sleep(2)
					page_submit.click()

				self.web_driver_wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager .active .num'), str(i)))
				print("页数加载完毕")
				self.web_driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
				print("商品加载完毕")
				self.get_products()

			except TimeoutException:
				print("time out error")
					
	def get_products(self):

		print("抓取商品...")
		html = self.web_driver.page_source
		doc = pq(html)
		items = doc('#mainsrp-itemlist .items .item').items()
		for item in islice(items, 1, None):
			product = {
				'image': item.find('.pic img').attr('data-src'),
				'price': item.find('.price strong').text(),
				'deal': item.find('.deal-cnt').text(),
				'title': item.find('.title').text(),
				'shop': item.find('.shop .shopname').text(),
				'location': item.find('.location').text()
			}
			print(product)
			self.save_to_mongo(product)

	def save_to_mongo(self, result):

		
		db = self.client.taobao_products
		collection = db.iPad
		
		try:
			if collection.insert(result):
				print('成功存储到MongoDB')

		except Exception:
			print("存储到MongoDB失败")

if __name__ == '__main__':
	username = input("请输入用户名:")
	password = input("请输入密码:")
	spider = TaobaoSpider(username, password)
	spider.login()
	KEYWORD = input("请输入要搜索的商品:")
	spider.search(KEYWORD)
	spider.get_pages()






