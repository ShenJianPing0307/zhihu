# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from ..items import UserItem


class ZhSpider(scrapy.Spider):
    name = 'zh'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_url_token="excited-vczh"
    user_include="allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics"
    include="data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics"
    offset=0
    limit=20

    user_url="https://www.zhihu.com/api/v4/members/{url_token}?include={include}"
    following_url="https://www.zhihu.com/api/v4/members/{url_token}/followees?include={include}&offset={offset}&limit={limit}"
    follower_url = "https://www.zhihu.com/api/v4/members/{url_token}/followers?include={include}&offset={offset}&limit={limit}"

    def start_requests(self):

        """
        （1）获取用户个人信息、
        （2）获取他关注的所有用户列表、
        （3）获取关注他的所有用户列表
        :return:
        """
        yield scrapy.Request(self.user_url.format(url_token=self.start_url_token,include=self.user_include),self.parse_user)
        yield scrapy.Request(self.following_url.format(url_token=self.start_url_token,include=self.include,offset=self.offset,limit=self.limit),self.parse_following)
        yield scrapy.Request(self.follower_url.format(url_token=self.start_url_token,include=self.include,offset=self.offset,limit=self.limit),self.parse_follower)

    def parse_user(self, response):
        """
        （1）将个人信息进行处理
        （2）将获取他关注的人进行递归
        （3）将获取关注他的人进行递归
        :param response:
        :return:
        """
        results=json.loads(response.text)
        user_item=UserItem()
        for field in user_item.fields:
            if field in results.keys():
                user_item[field]=results.get(field)
        yield user_item

        yield scrapy.Request(
            self.following_url.format(url_token=results.get('url_token'), include=self.include, offset=self.offset,
                                      limit=self.limit), self.parse_following)
        yield scrapy.Request(self.follower_url.format(url_token=self.start_url_token,include=self.include,offset=self.offset,limit=self.limit),self.parse_follower)


    def parse_following(self,response):
        """
        (1)处理他关注的人的用户信息
       （2）分页处理
        :param response:
        :return:
        """
        results=json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield scrapy.Request(self.user_url.format(url_token=result.get('url_token'),include=self.include),self.parse_user)

        ############分页###########
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:

            next_page = results.get('paging').get('next')
            yield scrapy.Request(next_page,self.parse_following)

    def parse_follower(self,response):
        """
        (1)处理关注他的人的用户信息
       （2）分页处理
        :param response:
        :return:
        """
        results=json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield scrapy.Request(self.user_url.format(url_token=result.get('url_token'),include=self.include),self.parse_user)

        ############分页###########
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:

            next_page = results.get('paging').get('next')
            yield scrapy.Request(next_page,self.parse_follower)

