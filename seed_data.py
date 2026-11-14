import os
import sys
import shutil
import django

# Set UTF-8 for console output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatkart.settings')
django.setup()

from category.models import Category
from store.models import Product

def run():
    print("Bat dau nap du lieu mau...")
    
    # 1. Tao thu muc media neu chua co
    os.makedirs('media/photos/products', exist_ok=True)
    os.makedirs('media/photos/categories', exist_ok=True)
    
    # 2. Tao danh muc mau
    categories_data = [
        {"name": "Shirts", "slug": "shirts", "desc": "Cac loai ao so mi nam nu thoi trang"},
        {"name": "T-Shirts", "slug": "t-shirts", "desc": "Ao thun nang dong tre trung"},
        {"name": "Jeans", "slug": "jeans", "desc": "Quan jeans chat luong cao"},
        {"name": "Shoes", "slug": "shoes", "desc": "Giay the thao, thoi trang"},
        {"name": "Jackets", "slug": "jackets", "desc": "Ao khoac mua dong va thu"},
    ]
    
    cat_objs = {}
    for c in categories_data:
        cat, created = Category.objects.get_or_create(
            category_name=c["name"],
            defaults={"slug": c["slug"], "description": c["desc"]}
        )
        cat_objs[c["name"]] = cat
        print(f"Danh muc: {cat.category_name} ({'Moi tao' if created else 'Da ton tai'})")

    # 3. Tao san pham mau dung nhu trong hinh anh bai viet
    products_data = [
        {
            "name": "ATX Jeans", "slug": "atx-jeans", "price": 199, "stock": 50,
            "category": "Jeans", "img_src": "4.jpg", "desc": "Quan jeans ATX co gian thoai mai, phong cach tre trung."
        },
        {
            "name": "Blue Shirt", "slug": "blue-shirt", "price": 189, "stock": 40,
            "category": "Shirts", "img_src": "1.jpg", "desc": "Ao so mi xanh duong thanh lich, phu hop cong so va di choi."
        },
        {
            "name": "Great T-Shirt", "slug": "great-t-shirt", "price": 209, "stock": 60,
            "category": "T-Shirts", "img_src": "5.jpg", "desc": "Ao thun GreatKart cotton 100% thoang mat."
        },
        {
            "name": "Jordan True Shoe", "slug": "jordan-true-shoe", "price": 199, "stock": 30,
            "category": "Shoes", "img_src": "2.jpg", "desc": "Giay the thao Jordan em ai, bam duong cuc tot."
        },
        {
            "name": "Puma Ferrari Shoe", "slug": "puma-ferrari-shoe", "price": 199, "stock": 25,
            "category": "Shoes", "img_src": "6.jpg", "desc": "Giay the thao Puma Ferrari phien ban gioi han ca tinh."
        },
        {
            "name": "US Polo Assn Jacket", "slug": "us-polo-assn-jacket", "price": 189, "stock": 20,
            "category": "Jackets", "img_src": "3.jpg", "desc": "Ao khoac du US Polo am ap, chong gio mua dong."
        },
        {
            "name": "Wrangler Shirt", "slug": "wrangler-shirt", "price": 199, "stock": 35,
            "category": "Shirts", "img_src": "7.jpg", "desc": "Ao so mi hoa tiet Wrangler dam chat phong cach."
        },
        {
            "name": "Pim Jeans", "slug": "pim-jeans", "price": 201, "stock": 45,
            "category": "Jeans", "img_src": "8.jpg", "desc": "Quan bo Pim Jeans ong dung thoi thuong."
        },
    ]

    for p in products_data:
        src_path = os.path.join('greatkart', 'static', 'images', 'items', p["img_src"])
        dest_filename = p["img_src"]
        dest_path = os.path.join('media', 'photos', 'products', dest_filename)
        
        if os.path.exists(src_path):
            shutil.copyfile(src_path, dest_path)
            rel_media_path = f"photos/products/{dest_filename}"
        else:
            rel_media_path = ""

        prod, created = Product.objects.get_or_create(
            product_name=p["name"],
            defaults={
                "slug": p["slug"],
                "price": p["price"],
                "stock": p["stock"],
                "is_available": True,
                "category": cat_objs[p["category"]],
                "description": p["desc"],
                "images": rel_media_path,
            }
        )
        print(f"San pham: {prod.product_name} - ${prod.price} ({'Moi tao' if created else 'Da ton tai'})")

    print("\n=> Hoan tat nap du lieu mau!")

if __name__ == '__main__':
    run()
