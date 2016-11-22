# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
import livingsocial.models as models


class LivingSocialPipeline(object):
    '''Pipeline for storing scraped items in database'''
    def __init__(self):
        '''Inits db connection and sessionmaker. Creates deals table.'''
        engine = models.db_connect()
        models.create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        '''Save deal item in database. Called for every pipeline item.'''
        session = self.Session()
        deal = models.Deal(**item)
        try:
            session.add(deal)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item
