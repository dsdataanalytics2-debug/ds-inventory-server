from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    total_added_qty = Column(Integer, default=0)
    total_added_amount = Column(Numeric(10, 2), default=0.00)
    total_sold_qty = Column(Integer, default=0)
    total_sold_amount = Column(Numeric(10, 2), default=0.00)
    available_stock = Column(Integer, default=0)
    
    add_histories = relationship("AddHistory", back_populates="product")
    sell_histories = relationship("SellHistory", back_populates="product")

class AddHistory(Base):
    __tablename__ = "add_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))
    total_amount = Column(Numeric(10, 2))
    date = Column(String)
    
    product = relationship("Product", back_populates="add_histories")

class SellHistory(Base):
    __tablename__ = "sell_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))
    total_amount = Column(Numeric(10, 2))
    date = Column(String)
    
    product = relationship("Product", back_populates="sell_histories")

class UserRole(enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    editor = "editor"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)  # Full name field
    password_hash = Column(String)
    role = Column(Enum(UserRole), default=UserRole.viewer)
    created_at = Column(DateTime, default=func.now())
    
    activity_logs = relationship("ActivityLog", back_populates="user")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # "Add", "Edit", "Delete", "Sell"
    target = Column(String)  # Target description (e.g., "product Paracetamol")
    details = Column(String)  # Additional details about the action
    timestamp = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="activity_logs")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String)
    quantity_sold = Column(Integer)
    total_amount = Column(Numeric(10, 2))
    customer_name = Column(String, nullable=True)
    customer_address = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    sale_date = Column(DateTime, default=func.now())
    created_by = Column(String)  # Username from JWT token
    
    product = relationship("Product")
