from pydantic import BaseModel, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import enum

class AddProductRequest(BaseModel):
    product_name: str
    quantity: int
    unit_price: Decimal
    date: str

class SellProductRequest(BaseModel):
    product_name: str
    quantity: int
    unit_price: Decimal
    date: str

class ProductBase(BaseModel):
    name: str
    total_added_qty: int
    total_added_amount: Decimal
    total_sold_qty: int
    total_sold_amount: Decimal
    available_stock: int

class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

class AddHistoryBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    date: str

class AddHistory(AddHistoryBase):
    id: int
    
    class Config:
        from_attributes = True

class SellHistoryBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    date: str

class SellHistory(SellHistoryBase):
    id: int
    
    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    products: List[Product]
    
class DateRangeSummaryResponse(BaseModel):
    products: List[Product]
    total_added_qty_in_range: int
    total_added_amount_in_range: Decimal
    total_sold_qty_in_range: int
    total_sold_amount_in_range: Decimal

class ProductResponse(BaseModel):
    success: bool
    message: str
    product: Optional[Product] = None

class ProductAnalytics(ProductBase):
    id: int
    avg_purchase_price: Optional[Decimal] = None
    avg_selling_price: Optional[Decimal] = None
    profit_loss: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class EnhancedSummaryResponse(BaseModel):
    products: List[ProductAnalytics]

class DailyHistoryItem(BaseModel):
    date: str
    total_added_qty: int
    total_added_amount: Decimal
    total_sold_qty: int
    total_sold_amount: Decimal

class DailyHistoryResponse(BaseModel):
    daily_history: List[DailyHistoryItem]

class TransactionHistoryItem(BaseModel):
    id: int  # Transaction ID for deletion
    date: str
    product_name: str
    transaction_type: str  # "add" or "sell"
    quantity: int
    unit_price: Decimal
    total_amount: Decimal

class TransactionHistoryResponse(BaseModel):
    transactions: List[TransactionHistoryItem]

class DeleteResponse(BaseModel):
    success: bool
    message: str
    updated_product: Optional[Product] = None

# Authentication Schemas
class UserBase(BaseModel):
    username: str
    role: str  # Changed from UserRole enum to string for compatibility

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "viewer"  # Accept lowercase role string
    
    @validator('role')
    def validate_role(cls, v):
        # Automatically convert to lowercase to ensure consistency
        if isinstance(v, str):
            v = v.lower()
        # Validate it's a valid role
        valid_roles = ['superadmin', 'admin', 'editor', 'viewer']
        if v not in valid_roles:
            raise ValueError(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
        return v

class User(UserBase):
    id: int
    created_at: datetime
    
    @validator('role', pre=True)
    def convert_role_enum_to_string(cls, v):
        """Convert UserRole enum to string value"""
        if hasattr(v, 'value'):
            return v.value  # If it's an enum, return its value
        return v  # If it's already a string, return as-is
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class ActivityLogBase(BaseModel):
    action: str
    target: str
    details: Optional[str] = None

class ActivityLog(ActivityLogBase):
    id: int
    user_id: int
    timestamp: datetime
    username: str  # Denormalized for easy display
    user_role: str
    
    class Config:
        from_attributes = True

class ActivityLogResponse(BaseModel):
    logs: List[ActivityLog]

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[Token] = None

class UsersResponse(BaseModel):
    users: List[User]

class DeleteUserResponse(BaseModel):
    success: bool
    message: str

# Profile Management Schemas
class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserMeResponse(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    role: str
    created_at: datetime
    
    @validator('role', pre=True)
    def convert_role_enum_to_string(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v
    
    class Config:
        orm_mode = True

class ProfileUpdateResponse(BaseModel):
    message: str
