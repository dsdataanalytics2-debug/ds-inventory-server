from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Product, AddHistory, SellHistory, User, ActivityLog, UserRole as ModelUserRole
from schemas import AddProductRequest, SellProductRequest, UserCreate
from decimal import Decimal
from auth import get_password_hash
from activity import log_activity

def add_product(db: Session, request: AddProductRequest, current_user: User = None):
    """
    Enhanced add product with pricing:
    1. Check if product exists
    2. If not → create new entry in products
    3. Calculate total_amount = quantity × unit_price
    4. Insert record in add_history with quantity, unit_price, total_amount, date
    5. Update products: total_added_qty += quantity, total_added_amount += total_amount
    6. Recalculate available_stock = total_added_qty - total_sold_qty
    """
    
    # Check if product exists
    product = db.query(Product).filter(Product.name == request.product_name).first()
    
    # If not, create new product
    if not product:
        product = Product(
            name=request.product_name,
            total_added_qty=0,
            total_added_amount=Decimal('0.00'),
            total_sold_qty=0,
            total_sold_amount=Decimal('0.00'),
            available_stock=0
        )
        db.add(product)
        db.commit()
        db.refresh(product)
    
    # Calculate total_amount = quantity × unit_price
    total_amount = Decimal(str(request.quantity)) * request.unit_price
    
    # Insert record in add_history
    add_history = AddHistory(
        product_id=product.id,
        quantity=request.quantity,
        unit_price=request.unit_price,
        total_amount=total_amount,
        date=request.date
    )
    db.add(add_history)
    
    # Update products table
    product.total_added_qty += request.quantity
    product.total_added_amount += total_amount
    
    # Recalculate available_stock = total_added_qty - total_sold_qty
    product.available_stock = product.total_added_qty - product.total_sold_qty
    
    db.commit()
    db.refresh(product)
    
    # Log activity
    if current_user:
        log_activity(
            db, 
            current_user, 
            "Add Product", 
            f"product {request.product_name}",
            f"Added {request.quantity} units at ${request.unit_price} each (Total: ${total_amount})"
        )
    
    return product

def sell_product(db: Session, request: SellProductRequest, current_user: User = None):
    """
    Enhanced sell product with pricing:
    1. Check if product exists
    2. If not → return error ("Product not found")
    3. Check if available_stock >= quantity
    4. If not → return error ("Insufficient stock")
    5. Calculate total_amount = quantity × unit_price
    6. Insert record in sell_history with quantity, unit_price, total_amount, date
    7. Update products: total_sold_qty += quantity, total_sold_amount += total_amount
    8. Recalculate available_stock = total_added_qty - total_sold_qty
    """
    
    # Check if product exists
    product = db.query(Product).filter(Product.name == request.product_name).first()
    
    if not product:
        return {"error": "Product not found"}
    
    # Check if available_stock >= quantity
    if product.available_stock < request.quantity:
        return {"error": "Insufficient stock"}
    
    # Calculate total_amount = quantity × unit_price
    total_amount = Decimal(str(request.quantity)) * request.unit_price
    
    # Insert record in sell_history
    sell_history = SellHistory(
        product_id=product.id,
        quantity=request.quantity,
        unit_price=request.unit_price,
        total_amount=total_amount,
        date=request.date
    )
    db.add(sell_history)
    
    # Update products table
    product.total_sold_qty += request.quantity
    product.total_sold_amount += total_amount
    
    # Recalculate available_stock = total_added_qty - total_sold_qty
    product.available_stock = product.total_added_qty - product.total_sold_qty
    
    db.commit()
    db.refresh(product)
    
    # Log activity
    if current_user:
        log_activity(
            db, 
            current_user, 
            "Sell Product", 
            f"product {request.product_name}",
            f"Sold {request.quantity} units at ${request.unit_price} each (Total: ${total_amount})"
        )
    
    return product

def get_summary(db: Session):
    """
    Enhanced summary with financial analytics:
    For each product show:
    - name, total_added_qty, total_added_amount, total_sold_qty, total_sold_amount, available_stock
    - avg_purchase_price, avg_selling_price, profit_loss
    """
    products = db.query(Product).all()
    return products

def get_enhanced_summary(db: Session):
    """
    Get enhanced summary with financial calculations
    """
    products = db.query(Product).all()
    enhanced_products = []
    
    for product in products:
        # Calculate average prices
        avg_purchase_price = None
        avg_selling_price = None
        profit_loss = None
        
        if product.total_added_qty > 0:
            avg_purchase_price = product.total_added_amount / Decimal(str(product.total_added_qty))
        
        if product.total_sold_qty > 0:
            avg_selling_price = product.total_sold_amount / Decimal(str(product.total_sold_qty))
        
        # Simple profit calculation: total_sold_amount - total_added_amount
        if product.total_sold_amount and product.total_added_amount:
            profit_loss = product.total_sold_amount - product.total_added_amount
        
        # Create enhanced product object
        enhanced_product = {
            "id": product.id,
            "name": product.name,
            "total_added_qty": product.total_added_qty,
            "total_added_amount": product.total_added_amount,
            "total_sold_qty": product.total_sold_qty,
            "total_sold_amount": product.total_sold_amount,
            "available_stock": product.available_stock,
            "avg_purchase_price": avg_purchase_price,
            "avg_selling_price": avg_selling_price,
            "profit_loss": profit_loss
        }
        enhanced_products.append(enhanced_product)
    
    return enhanced_products

def get_date_range_summary(db: Session, start_date: str, end_date: str):
    """
    Enhanced date range summary with financial data:
    - Sum all add_history & sell_history between dates (qty and amount)
    - Return totals & product-wise summary
    """
    
    # Get all products
    products = db.query(Product).all()
    
    # Calculate totals within date range
    total_added_qty_in_range = 0
    total_added_amount_in_range = Decimal('0.00')
    total_sold_qty_in_range = 0
    total_sold_amount_in_range = Decimal('0.00')
    
    # Sum from add_history within date range
    add_records = db.query(AddHistory).filter(
        and_(AddHistory.date >= start_date, AddHistory.date <= end_date)
    ).all()
    
    for record in add_records:
        total_added_qty_in_range += record.quantity
        total_added_amount_in_range += record.total_amount
    
    # Sum from sell_history within date range
    sell_records = db.query(SellHistory).filter(
        and_(SellHistory.date >= start_date, SellHistory.date <= end_date)
    ).all()
    
    for record in sell_records:
        total_sold_qty_in_range += record.quantity
        total_sold_amount_in_range += record.total_amount
    
    return {
        "products": products,
        "total_added_qty_in_range": total_added_qty_in_range,
        "total_added_amount_in_range": total_added_amount_in_range,
        "total_sold_qty_in_range": total_sold_qty_in_range,
        "total_sold_amount_in_range": total_sold_amount_in_range
    }

def get_all_products(db: Session):
    """Get all product names for dropdown selection"""
    products = db.query(Product).all()
    return [product.name for product in products]

def get_daily_history(db: Session, start_date: str = None, end_date: str = None):
    """
    Get daily history aggregating add and sell transactions by date.
    
    Logic:
    1. Query all add_history and sell_history records
    2. Filter by date range if provided
    3. Group by date and sum quantities/amounts
    4. Merge add and sell data by date
    5. Fill missing dates with zeros
    6. Return sorted list of daily totals
    """
    from collections import defaultdict
    from datetime import datetime, timedelta
    
    # Initialize aggregation dictionaries
    add_daily = defaultdict(lambda: {'qty': 0, 'amount': Decimal('0.00')})
    sell_daily = defaultdict(lambda: {'qty': 0, 'amount': Decimal('0.00')})
    
    # Query add_history
    add_query = db.query(AddHistory)
    if start_date and end_date:
        add_query = add_query.filter(
            and_(AddHistory.date >= start_date, AddHistory.date <= end_date)
        )
    add_records = add_query.all()
    
    # Aggregate add data by date
    for record in add_records:
        date = record.date
        add_daily[date]['qty'] += record.quantity
        add_daily[date]['amount'] += record.total_amount
    
    # Query sell_history
    sell_query = db.query(SellHistory)
    if start_date and end_date:
        sell_query = sell_query.filter(
            and_(SellHistory.date >= start_date, SellHistory.date <= end_date)
        )
    sell_records = sell_query.all()
    
    # Aggregate sell data by date
    for record in sell_records:
        date = record.date
        sell_daily[date]['qty'] += record.quantity
        sell_daily[date]['amount'] += record.total_amount
    
    # Get all unique dates from both add and sell records
    all_dates = set(add_daily.keys()) | set(sell_daily.keys())
    
    # Create final daily history list
    daily_history = []
    for date in sorted(all_dates):
        daily_item = {
            "date": date,
            "total_added_qty": add_daily[date]['qty'],
            "total_added_amount": add_daily[date]['amount'],
            "total_sold_qty": sell_daily[date]['qty'],
            "total_sold_amount": sell_daily[date]['amount']
        }
        daily_history.append(daily_item)
    
    return daily_history

def get_transaction_history(db: Session, start_date: str = None, end_date: str = None):
    """
    Get individual transaction history combining add and sell records.
    
    Logic:
    1. Query add_history with product names (JOIN products table)
    2. Query sell_history with product names (JOIN products table) 
    3. Combine both into single list with transaction_type field
    4. Filter by date range if provided
    5. Sort by date descending
    6. Return list of individual transaction records
    """
    
    transactions = []
    
    # Query add_history with product names
    add_query = db.query(AddHistory, Product.name).join(Product, AddHistory.product_id == Product.id)
    if start_date and end_date:
        add_query = add_query.filter(
            and_(AddHistory.date >= start_date, AddHistory.date <= end_date)
        )
    add_records = add_query.all()
    
    # Convert add records to transaction format
    for add_record, product_name in add_records:
        transactions.append({
            "id": add_record.id,
            "date": add_record.date,
            "product_name": product_name,
            "transaction_type": "add",
            "quantity": add_record.quantity,
            "unit_price": add_record.unit_price,
            "total_amount": add_record.total_amount
        })
    
    # Query sell_history with product names
    sell_query = db.query(SellHistory, Product.name).join(Product, SellHistory.product_id == Product.id)
    if start_date and end_date:
        sell_query = sell_query.filter(
            and_(SellHistory.date >= start_date, SellHistory.date <= end_date)
        )
    sell_records = sell_query.all()
    
    # Convert sell records to transaction format
    for sell_record, product_name in sell_records:
        transactions.append({
            "id": sell_record.id,
            "date": sell_record.date,
            "product_name": product_name,
            "transaction_type": "sell",
            "quantity": sell_record.quantity,
            "unit_price": sell_record.unit_price,
            "total_amount": sell_record.total_amount
        })
    
    # Sort by date descending (most recent first)
    transactions.sort(key=lambda x: x["date"], reverse=True)
    
    return transactions

def delete_add_history(db: Session, add_history_id: int, current_user: User = None):
    """
    Delete an add_history record and update product totals accordingly.
    
    Logic:
    1. Find the add_history record by id
    2. Get the associated product
    3. Subtract the quantity and total_amount from product totals
    4. Recalculate available_stock = total_added_qty - total_sold_qty
    5. Delete the add_history record
    6. Return updated product
    """
    
    # Find the add_history record
    add_record = db.query(AddHistory).filter(AddHistory.id == add_history_id).first()
    
    if not add_record:
        return {"error": "Add history record not found"}
    
    # Get the associated product
    product = db.query(Product).filter(Product.id == add_record.product_id).first()
    
    if not product:
        return {"error": "Associated product not found"}
    
    # Update product totals by subtracting the deleted record values
    product.total_added_qty -= add_record.quantity
    product.total_added_amount -= add_record.total_amount
    
    # Recalculate available_stock = total_added_qty - total_sold_qty
    product.available_stock = product.total_added_qty - product.total_sold_qty
    
    # Delete the add_history record
    db.delete(add_record)
    
    # Commit the changes
    db.commit()
    db.refresh(product)
    
    # Log activity
    if current_user:
        log_activity(
            db, 
            current_user, 
            "Delete Add History", 
            f"product {product.name}",
            f"Deleted add history record (ID: {add_history_id}) - {add_record.quantity} units @ ${add_record.unit_price}"
        )
    
    return product

def delete_sell_history(db: Session, sell_history_id: int, current_user: User = None):
    """
    Delete a sell_history record and update product totals accordingly.
    
    Logic:
    1. Find the sell_history record by id
    2. Get the associated product
    3. Subtract the quantity and total_amount from product totals
    4. Recalculate available_stock = total_added_qty - total_sold_qty
    5. Delete the sell_history record
    6. Return updated product
    """
    
    # Find the sell_history record
    sell_record = db.query(SellHistory).filter(SellHistory.id == sell_history_id).first()
    
    if not sell_record:
        return {"error": "Sell history record not found"}
    
    # Get the associated product
    product = db.query(Product).filter(Product.id == sell_record.product_id).first()
    
    if not product:
        return {"error": "Associated product not found"}
    
    # Update product totals by subtracting the deleted record values
    product.total_sold_qty -= sell_record.quantity
    product.total_sold_amount -= sell_record.total_amount
    
    # Recalculate available_stock = total_added_qty - total_sold_qty
    product.available_stock = product.total_added_qty - product.total_sold_qty
    
    # Delete the sell_history record
    db.delete(sell_record)
    
    # Commit the changes
    db.commit()
    db.refresh(product)
    
    # Log activity
    if current_user:
        log_activity(
            db, 
            current_user, 
            "Delete Sell History", 
            f"product {product.name}",
            f"Deleted sell history record (ID: {sell_history_id}) - {sell_record.quantity} units @ ${sell_record.unit_price}"
        )
    
    return product

# User Management Functions
def create_user(db: Session, user_create: UserCreate, current_user: User):
    """Create a new user (only superadmin can do this)"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        return {"error": "Username already exists"}
    
    # Convert string role to enum
    role_str = user_create.role if isinstance(user_create.role, str) else user_create.role.value
    try:
        role_enum = ModelUserRole(role_str)
    except ValueError:
        return {"error": f"Invalid role: {role_str}. Must be one of: superadmin, admin, editor, viewer"}
    
    # Create new user
    hashed_password = get_password_hash(user_create.password)
    new_user = User(
        username=user_create.username,
        password_hash=hashed_password,
        role=role_enum
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log activity
    log_activity(
        db, 
        current_user, 
        "Create User", 
        f"user {user_create.username}",
        f"Created new user with role {role_str}"
    )
    
    return new_user

def get_users(db: Session):
    """Get all users"""
    return db.query(User).all()

def delete_user(db: Session, user_id: int, current_user: User):
    """Delete a user (only superadmin can do this)"""
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        return {"error": "User not found"}
    
    if user_to_delete.id == current_user.id:
        return {"error": "Cannot delete your own account"}
    
    username = user_to_delete.username
    db.delete(user_to_delete)
    db.commit()
    
    # Log activity
    log_activity(
        db, 
        current_user, 
        "Delete User", 
        f"user {username}",
        f"Deleted user account"
    )
    
    return {"message": f"User {username} deleted successfully"}
