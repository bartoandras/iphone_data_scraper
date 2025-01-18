from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import re

Base = declarative_base()

class IPhone(Base):
    __tablename__ = 'iphones'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, unique=True, nullable=False)
    model = Column(String)
    price = Column(Integer)
    condition = Column(String, nullable=True)
    battery = Column(String, nullable=True)
    url = Column(String)
    capacity = Column(Integer, nullable=True)
    is_pro = Column(Integer, default=0)
    is_max = Column(Integer, default=0)
    is_mini = Column(Integer, default=0)
    is_se = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def extract_product_id(url):
        """Extract product ID from URL"""
        match = re.search(r'/(\d+)$', url)
        return int(match.group(1)) if match else None

class Database:
    def __init__(self, db_path='/app/data/iphones.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_or_update_iphone(self, data):
        """Add or update iPhone record"""
        session = self.Session()
        
        # Extract product ID from URL
        product_id = IPhone.extract_product_id(data['url'])
        if not product_id:
            return False

        # Check if record exists
        iphone = session.query(IPhone).filter_by(product_id=product_id).first()
        
        if iphone:
            # Update existing record
            iphone.model = data.get('model')
            iphone.price = data.get('price')
            iphone.condition = data.get('condition')
            iphone.battery = data.get('battery')
            iphone.url = data.get('url')
            iphone.capacity = data.get('capacity')
            iphone.is_pro = int(data.get('pro', False))
            iphone.is_max = int(data.get('max', False))
            iphone.is_mini = int(data.get('mini', False))
            iphone.is_se = int(data.get('se', False))
        else:
            # Create new record
            iphone = IPhone(
                product_id=product_id,
                model=data.get('model'),
                price=data.get('price'),
                condition=data.get('condition'),
                battery=data.get('battery'),
                url=data.get('url'),
                capacity=data.get('capacity'),
                is_pro=int(data.get('pro', False)),
                is_max=int(data.get('max', False)),
                is_mini=int(data.get('mini', False)),
                is_se=int(data.get('se', False))
            )
            session.add(iphone)
        
        session.commit()
        session.close()
        return True

    def get_all_iphones(self):
        """Get all iPhone records"""
        session = self.Session()
        iphones = session.query(IPhone).all()
        session.close()
        return iphones
