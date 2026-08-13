from flask import Flask, render_template, request, flash, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'bloom_breez_key'

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def database():
    with sqlite3.connect('database.db') as conn:
        
        conn.execute('''CREATE TABLE IF NOT EXISTS admins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            address_line01 TEXT NOT NULL,
            address_line02 TEXT,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            admin_name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            admin_code TEXT NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    mobile_number TEXT NOT NULL,
                    address_line01 TEXT NOT NULL,
                    address_line02 TEXT,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    email TEXT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            file_path TEXT NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS variants(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     product_id INTEGER NOT NULL,
                     size TEXT NOT NULL,
                     colour TEXT,
                     price INTEGER NOT NULL,
                     stock TEXT NOT NULL,
                     SKU TEXT NOT NULL,
                     FOREIGN KEY (product_id) REFERENCES products(id))''')
        
        
        conn.execute('''CREATE TABLE IF NOT EXISTS shipping(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            address_line01 TEXT NOT NULL,
            address_line02 TEXT,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        
        conn.execute('''CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            shipping_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT NOT NULL,
            order_date TEXT,
            
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (shipping_id) REFERENCES shipping(id))''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS order_status_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            updated_date TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id))
            ''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS product_images(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id))''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS product_videos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id iNTEGER NOT NULL,
            file_path_video TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) )''')
        
        conn.commit()

@app.route('/')
def home():
    return render_template('home.html', selected='select')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    
    if request.method == 'POST':
        admin_name = request.form['admin_name']
        password = request.form['password']
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password FROM admins WHERE admin_name=?", (admin_name,))
            admin_data = cursor.fetchone()
            
            if admin_data:
                if password == admin_data[1]:
                    session['admin_id'] = admin_data[0]
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash("incorrect password")
                
            else:
                flash("Invalid adminname")
            
        
    
    return render_template('admin_login.html')

@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    admin_code = "bbadmin1125"
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        address_line01 = request.form['address_line01']
        address_line02 = request.form['address_line02']
        city = request.form['city']
        country = request.form['country']
        admin_name = request.form['admin_name']
        password = request.form['password']
        admin_verification_code = request.form['verification_code']
        
        if admin_verification_code == admin_code:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO admins (full_name, email, mobile_number, address_line01, address_line02, city, country, admin_name, password, admin_code) VALUES(?,?,?,?,?,?,?,?,?,?)", (full_name, email, mobile_number, address_line01, address_line02, city, country, admin_name, password, admin_code))
                conn.commit()
                
        
        # print(admin_verification_code)
        
        
        return redirect(url_for('admin_login'))
        
    return render_template('admin_signup.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    admin_id = session['admin_id']
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, admin_name FROM admins WHERE id=?", (admin_id,))
        admin_data = cursor.fetchone()
        if admin_data:
            full_name = admin_data[0]
            admin_name = admin_data[1]
        
        flash("you have successfully logged in")
    return render_template('admin_dashboard.html', full_name=full_name, admin_name=admin_name)

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin_order_details')
def admin_order_details():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * from orders")
        orders = cursor.fetchall()
    return render_template('admin_order_details.html', orders=orders)

@app.route('/admin_customer_detail/<int:user_id>')
def admin_customer_detail(user_id):
    print(user_id)
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            customer_data = user_data
        else:
            flash("Invalid customer id")
    
    print(customer_data)        
    return render_template('admin_customer_detail.html', customer_data=customer_data)

@app.route('/admin_product_detail/<int:product_id>')
def admin_product_detail(product_id):
    print(product_id)
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        print(product)
        
    return render_template('admin_product_detail.html', product=product)

@app.route('/admin_shipping_detail/<int:shipping_id>')
def admin_shipping_detail(shipping_id):
    print(shipping_id)
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT address_line01, address_line02, city, country FROM shipping WHERE id=?", (shipping_id,))
        shipping_data = cursor.fetchone()
        if shipping_data:
            shipping_detail = shipping_data
            print(shipping_detail)
        else:
            flash("shipping id not found")
    return render_template('admin_shipping_detail.html', shipping_detail=shipping_detail)

@app.route('/all_categories')
def all_categories():
    return render_template('all_categories.html', selected = 'all')

@app.route('/kid_items')
def kid_items():
    return render_template('kid_items.html', selected='kids')

@app.route('/men_clothing')
def men_clothing():
    return render_template('men_clothing.html', selected='men')

@app.route('/women_clothing')
def women_clothing():
    return render_template('women_clothing.html', selected='women')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("Select id,password From users Where username=?", (username,))
            user_data = cursor.fetchone()
            if user_data:
                if password == user_data[1]:
                    session['user_id'] = user_data[0]
                    return redirect(url_for('dashboard'))
                else:
                    flash("Incorrect Password")
            else:
                flash("Invalid username")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        mobile_number = request.form['mobile_number']
        address_line01 = request.form['address_line01']
        address_line02 = request.form['address_line02']
        city = request.form['city']
        country = request.form['country']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users Where username=?", (username,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO users (full_name, mobile_number, address_line01, address_line02, city, country, email, username, password) VALUES(?,?,?,?,?,?,?,?,?)", (full_name, mobile_number, address_line01, address_line02,city,country, email, username,password))
                
                user_id = cursor.lastrowid
                cursor.execute("INSERT INTO shipping (user_id, address_line01, address_line02, city, country) VALUES(?,?,?,?,?)", (user_id, address_line01, address_line02, city, country))
                
                flash("YOU have signed up successfully, login to continue")
                return redirect(url_for('login'))
            else:
                flash("username already exist, try different username")
                
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():   
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, full_name from users WHERE id=?", (user_id,))
        user_detail = cursor.fetchone()
        if user_detail:
            username= user_detail[0]
            full_name = user_detail[1]
            flash("You have successfully logged in")
            return render_template('dashboard.html', full_name=full_name, username=username, user_id=user_id)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/view_products')
def view_products():
    
    product_id_list = []
    name = []
    detail = []
    price = []
    colour = []
    file_path = []
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM products")
        product = cursor.fetchall()
        print("product: ", product)
        if product:
            for product_id_tuple in product:
                product_id = product_id_tuple[0]
                print("product_id: ", product_id)
                
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM products where id=?", (product_id,))
                    product_id_tuple02 = cursor.fetchall()
                    if product_id_tuple02:
                        product_id_list.append(product_id_tuple02[0][0])
                
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
                    product_name = cursor.fetchall()
                    print("product name", product_name)
                    if product_name:
                        name.append(product_name[0][0])
                
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT description FROM products WHERE id=?", (product_id,))
                    product_detail = cursor.fetchall()
                    print("product detail", product_detail)
                    if product_detail:
                        detail.append(product_detail[0][0])
                # commented bcz of error  (prodcuts table modified)
                #
                # with sqlite3.connect('database.db') as conn:
                #     cursor = conn.cursor()
                #     cursor.execute("SELECT price FROM variants WHERE product_id=?", (product_id,))
                #     product_price = cursor.fetchall()
                #     print("product price", product_price)
                #     if product_price:
                #         price.append(product_price[0][0])
                
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT colour FROM variants WHERE product_id=?", (product_id,))
                    product_colour = cursor.fetchall()
                    print("product name", product_colour)
                    if product_colour:
                        colour.append(product_colour[0][0])
                
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT file_path FROM products WHERE id=?", (product_id,))
                    product_file_path = cursor.fetchall()
                    print("product name", product_file_path)
                    if product_file_path:
                        file_path.append(product_file_path[0][0])
            
            # this block used for code fix
            #          
            # print("Product id list : ", product_id_list)             
            # print("names: ", name)
            # print("detail: ", detail)
            # print("colour: ", colour)
            # print("price: ", price)
            # print("file path", file_path)
            
            products_dictionary = {}
            
            # jus for finding the error
            
            print("lentgth of product id list: ", len(product_id_list), product_id)
            print("length of colour: ", len(colour), colour)
            
            # end of finding the error
                     
            products_dictionary = {}
            
            for k in range(len(product_id_list)):
                products_dictionary[product_id_list[k]] = {
                    'product_id': product_id_list[k],
                    'name': name[k],
                    'detail': detail[k],
                    
                    # commented bcz of error (prodcuts table modified)
                    #
                    'colour': colour[k],
                    # 'price': price[k],
                    'file_path': file_path[k]
                }
            
            print("Products: ", products_dictionary)
                
        else:
            flash("no Any products available")
    return render_template('bloom_breeze_store.html', products_dictionary = products_dictionary)

@app.route('/product_detail', methods=['GET', 'POST'])
def product_detail():
    if request.method == 'POST':
        product_id = request.form['product_id']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, description, file_path FROM products where id=?", (product_id,))
            product_data01 = cursor.fetchone()
            
            if product_data01:
                name = product_data01[0]
                detail = product_data01[1]
                # file_path = product_data01[2]
            else:
                print("product not available")
            
            cursor.execute("SELECT size, colour, price FROM variants WHERE product_id=?", (product_id,))
            product_detail02 = cursor.fetchone()
            
            if product_detail02:
                size = product_detail02[0]
                colour = product_detail02[1]
                price = product_detail02[2]
                
            else:
                print("variant for this product not available")
                
            cursor.execute("SELECT file_path FROM product_images WHERE product_id=?", (product_id,))
            product_detail03 = cursor.fetchall()
            
            if product_detail03:
                print("product detail03: ", product_detail03)
                file_paths = []
                print(len(product_detail03))
                for l in range(len(product_detail03)):
                    if l==0:
                        selected_image = product_detail03[l][0]
                        print("selected image", selected_image)
                    file_paths.append(product_detail03[l][0])
                print(file_paths)
            
            else:
                print("file path of the product is missing")
            
            
            cursor.execute("SELECT file_path_video FROM product_videos WHERE product_id=?",(product_id,))
            product_detail04 = cursor.fetchall()
            if product_detail04:
                # print("product_detail04: ",product_detail04)
                file_paths_video = []
                length_of_product_detail04 = len(product_detail04)
                for lpd4 in range(length_of_product_detail04):
                    file_paths_video.append(product_detail04[lpd4][0])
                print("file path video: ", file_paths_video)
                
            else:
                file_paths_video = None
                    
                
        
                
        product_detail = {
                'id': product_id,
                'name' : name,
                'detail' : detail,
                
                'size' : size,
                'colour' : colour,
                'price' : price,
                'selected_image': selected_image,
                'file_paths' : file_paths,
                'file_paths_video': file_paths_video
        }
        return render_template('product_detail.html', product_detail = product_detail)

@app.route('/view_ordered_items')
def view_ordered_items():
    return render_template('ordered_items.html')

@app.route('/buy_now', methods=['POST'])
def buy_now():
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    customer_data = None
    product_data = None

    if request.method == 'POST':
        size = request.form['size']
        colour = request.form['colour']
        quantity = request.form['quantity']
        product_id = request.form['product_id']
        
        session['product_detail'] = {
            'product_id' : product_id,
            'colour' : colour,
            'size' : size,
            'quantity' : quantity,
        }
        return redirect(url_for('place_order'))
    
@app.route('/place_order', methods=['GET','POST'])
def place_order():
    user_id = session['user_id']
    product_id = session['product_detail']['product_id']
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = request.form['quantity']
        total_price = request.form['total']
        name = request.form['full_name']
        address_line01 = request.form['address_line01']
        address_line02 = request.form['address_line02']
        city = request.form['city']
        country = request.form['country']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM shipping WHERE user_id=?", (user_id,))
            shipping_data = cursor.fetchone()
            
            if shipping_data:
                shipping_id = shipping_data[0]
                # print(shipping_id)
                
        status = 'order placed(payment required)'
        current_date = datetime.now().date()
        # print(current_date)
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO orders (user_id, product_id, shipping_id, quantity, total_price, status, order_date) VALUES(?,?,?,?,?,?,?)", (user_id, product_id, shipping_id, quantity, total_price, status, current_date))
        
            order_id = cursor.lastrowid
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO order_status_history (order_id, status, updated_date) VALUES(?,?,?)", (order_id,status, current_date))
        # with sqlite3.connect('database.db') as conn:
        #     cursor = conn.cursor()
            
        #     cursor.execute("INSERT INTO shipping (user_id, address_line01, address_line02, city, country) VALUES(?,?,?,?,?)", (user_id, address_line01, address_line02, city, country,))
        #     conn.commit()
        
        # with sqlite3.connect('database.db') as conn:
        #     cursor = conn.cursor()
            
        #     cursor.execute("")
            
        flash("Your order has been placed. payment required, we'll contact you ASAP")
        return redirect(url_for('dashboard'))
    
        
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, mobile_number,email From users Where id=?", (user_id,))
        customer_details = cursor.fetchone()
            
        if customer_details:
            customer_data = {
            'full_name' : customer_details[0],
            'mobile_number' : customer_details[1],
            # 'address_line01' : customer_details[2],
            # 'address_line02' : customer_details[3],
            # 'city' : customer_details[4],
            # 'country' : customer_details[5],
            'email': customer_details[2]
            }
            
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, description FROM products Where id=?", (product_id,))
        product_details = cursor.fetchone()
            
        if product_details:
            product_data = {
            'product_id' : product_id,
            'product_name' : product_details[0],
                
            # bcz of error occuring (products table modified)
            # 
            # 'colour' : product_details[1],
            # 'size' : product_details[2],
            'detail' : product_details[1],
            # 'price_per_piece' : product_details[4]
            }
                
                
        else:
            flash("product not found")
            return redirect(url_for('view_products'))
            
    
    
    with sqlite3.connect('database.db') as conn:
        conn.cursor()
        cursor.execute("SELECT price FROM variants WHERE product_id=?", (product_id,))
        variant_detail = cursor.fetchone()
            
        if variant_detail:
            product_data02 = {
                
                # bcz fetchine these two fields from session
                # 'colour': variant_detail[0],
                # 'size': variant_detail[1],
                'price_per_piece': variant_detail[0]
                    
            }
        else:
            flash("product_not_found")
            return redirect(url_for('view_products'))
            
    colour = session['product_detail']['colour']
    size = session['product_detail']['size']
    quantity = session['product_detail']['quantity']
    
    customer_preference = {
        'size': size,
        'colour': colour,
        'quantity': quantity,
    }
       
    with sqlite3.connect('database.db') as conn:
        conn.cursor()
        cursor.execute("SELECT address_line01, address_line02, city, country FROM shipping WHERE user_id =?", (user_id,))
        shipping_detail = cursor.fetchone()
        if shipping_detail:
            shipping_data = {
                'address_line01': shipping_detail[0],
                'address_line02' : shipping_detail[1],
                'city': shipping_detail[2],
                'country': shipping_detail[3],
                    
            }
                
            
    return render_template('place_order.html', customer_data=customer_data, product_data= product_data, product_data02= product_data02, customer_preference=customer_preference, shipping_data = shipping_data)

@app.route('/edit_shipping_address', methods = ['GET', 'POST'])
def edit_shipping_address():
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    shipping_data= None
    
    
    if request.method == 'POST':
        address_line01 = request.form['address_line01']
        address_line02 = request.form['address_line02']
        city = request.form['city']
        country = request.form['country']
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE shipping SET address_line01=?, address_line02=?, city=?, country=? WHERE user_id=?", (address_line01, address_line02, city, country, user_id,))
            conn.commit()
        
        print(address_line01)
        
        return redirect(url_for('place_order'))

    
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT address_line01, address_line02, city, country FROM shipping WHERE user_id=?", (user_id,))
        shipping_detail = cursor.fetchone()
        if shipping_detail:
            shipping_data = {
                'address_line01' : shipping_detail[0],
                'address_line02' : shipping_detail[1],
                'city': shipping_detail[2],
                'country' : shipping_detail[3]
            }
            
            
    return render_template('edit_shipping_address.html', shipping_data = shipping_data)


    
@app.route('/track_item')
def track_item():
    return render_template('track_item.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if password.strip() == "":
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
                user_detail = cursor.fetchone()
                if user_detail:
                    password = user_detail[0]
                else:
                    flash("some issue occured")
                    
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET username=?, email=?, password=? WHERE id=?", (username, email, password, user_id))
            conn.commit()
        print("new password:", password)
        flash (f"you have updated the profile succesfully,username - {username}, password - {password}, email - {email}")
        return redirect(url_for('dashboard'))
    
    with sqlite3.connect('database.db') as conn:
        cursor= conn.cursor()
        cursor.execute("SELECT username, email FROM users WHERE id=?", (user_id,))
        user_detail = cursor.fetchone()
        if user_detail:
            username = user_detail[0]
            email = user_detail[1]
        else:
            flash("some errors occured")
            
    user_data = {
        'username':username,
        'email': email
    }
    return render_template('edit_profile.html', user_data=user_data)


if __name__ == '__main__':
    database()
    app.run(port=2500, debug=True)