from sqlalchemy.orm import sessionmaker
from models import Deals, db_connect, create_deals_table


class LivingSocialPipeline(object):
    '''Pipeline for storing scraped items in database'''
    def __init__(self):
        '''Inits db connection and sessionmaker. Creates deals table.'''
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        '''Save deal item in database. Called for every pipeline item.'''
        session = self.Session()
        deals = Deals(**item)
        try:
            session.add(self)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item
