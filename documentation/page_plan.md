

date - 14.04.2026

plan - 'buy now' function update version
1. delete the code block of it
         a. copy the code block in one another file (for 'place order' function later use)
         b. delete the code
2. make the return statement triggers the 'place order' function
3. get the customer preferences from 'product detail' page
         a. size
         b. colour
         c. quantity
4. insert them into session like below
session['order_data'] = {
    'product_id': product_id,
    'size': size,
    'color': color,
    'quantity': quantity
}

plan - 'place order' function (briefe) update version
1. make function to work under 'GET' method also
2. under 'GET' method
        a. loads the 'place order form' page by fetching selected fields from table (copy from 'buy now' function)
        b. loads the other fields such like customer preferences from session     
3. under 'POST' method
         a. get the user preference fields from form (the fields user can modify in 'place order form' page)
              01) quantity

         b. get the other user preference fields from session
              01) size
              02) colour
         b. other fields from table (such like shipping, product detail, customer detail)
              01) shipping details
              02) product details
              03) customer details
         c. store them in suitable tables
          d. directs user to dashboard



date - 01.06.2026

plan - 'admin dashboard' function
1. check the login credential
2. direct the user to dashboard with flash message

error occured: able to access the dashboard page by clicking 'go back' button on browser
solution: added JS script code (force_reload.js) for force load

plan - admin logout
1. clear the session cookie
2. directs to home page (triggers the home function)
3. show flash message ('you have been logged out')
4. link the 'force_reload.js' file
3. test and check the function


date - 29.06.2026

plan - 'order detail' page and function
1. add the page simply
2. add the function with basic
3. add the navbar to page
4. fetch the data from the 'orders' table and pass it to 'order details' page
5. edit the variables name in 'order detail' page
6. check is that possible to get the admin selected id (for getting the suitable data from the customer, product, shipping tables)
7. plan for view the customer detail, shipping detail, product detail according to admin's selection

plan - 'product detail'  page and function
1. create the page with basics
2. create the function with basic
3. check is that possible view the page by clicking suitable link or button
4. use the variable which is passed by order details page to fetch the suitable product detail from products table
5. pass the fetched data to 'admin product detail' page
6. show the detail in table format

plan - 'customer detail'  page and function
1. create the page with basics
2. create the function with basic
3. check is that possible view the page by clicking suitable link or button
4. use the variable which is passed by order details page to fetch the suitable customer detail from customers or users table
5. pass the fetched data to 'admin customer detail' page
6. show the detail in table format

Plan - 'admin shipping detail'a page and function 
1. Create the page with basics
(Basically html tag and temporary header)
2. Create the function and with basic (just to access the page and fetch the variable)
3. Use the fetched data to fetch the shipping data from the table and fetch the needed data
4. Pass the fetched data to 'admin shipping detail' page
5. Show the data in table format

