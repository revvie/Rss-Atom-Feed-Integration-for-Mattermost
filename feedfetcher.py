#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'elpatron@mailbox.org'
# Derived from https://github.com/mattermost/mattermost-integration-gitlab

import requests
import json
import feedparser
import time
import sys
import logging
import settings

mattermost_webhook_url = settings.mattermost_webhook_url
mattermost_channel = settings.mattermost_channel
delay_between_pulls = settings.delay_between_pulls
verify_cert = settings.verify_cert
feeds = settings.feeds

def post_text(text, username, channel):
    """
    Mattermost POST method, posts text to the Mattermost incoming webhook URL
    """
    data = {}
    data['text'] = text
    if len(username) > 0:
        data['username'] = username
    if len(channel) > 0:
        data['channel'] = channel

    headers = {'Content-Type': 'application/json'}
    r = requests.post(mattermost_webhook_url, headers=headers, data=json.dumps(data), verify=verify_cert)

    if r.status_code is not requests.codes.ok:
        logging.debug('Encountered error posting to Mattermost URL %s, status=%d, response_body=%s' %
                      (mattermost_webhook_url, r.status_code, r.json()))


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    if len(mattermost_webhook_url) == 0:
        print('mattermost_webhook_url must be configured. Please see instructions in README.md')
        sys.exit()

    while 1:
        for feed in feeds:
            try:
                d = feedparser.parse(feed.Url)
                feed.NewTitle = d['entries'][0]['title']
                feed.ArticleUrl = d['entries'][0]['link']
                feed.Description = d['entries'][0]['description']
                if feed.LastTitle != feed.NewTitle:
                    logging.debug('Feed url: ' + feed.Url)
                    logging.debug('Title: ' + feed.NewTitle + '\n')
                    logging.debug('Link: ' + feed.ArticleUrl + '\n')
                    logging.debug('Posted text: ' + feed.jointext())
                    post_text(feed.jointext(), feed.User, feed.Channel)
                    feed.LastTitle = feed.NewTitle
                else:
                    logging.debug('Nothing new. Waiting for good news...')
            except:
                logging.critical('Error fetching feed.')
                continue

        time.sleep(delay_between_pulls)