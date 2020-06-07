# ---- index page ----
def index():
    session.message = 'Next delivery: Jul 2, 2020'
    message = session.message
    return locals()

@auth.requires_login()
def order():
    message = session.message
    rows = db(db.products).select()
    ## rows will be used in view to build html with {{=rows}} whereas same_rows is used below
    ## to generate listeners for buttons which will be used in view as {{=XML(js)}}
    same_rows = db.executesql('SELECT * FROM products;')
    js = ''
    index = 0
    # generate js for plus, minus buttons and input element
    while index < len(rows):
        row = same_rows[index]
        js += '<script>const minusButton'
        js += str(row[0])
        js += '= document.getElementById("minus'
        js += str(row[0])
        js += '");const plusButton'
        js += str(row[0])
        js += ' = document.getElementById("plus'
        js += str(row[0])
        js += '");const inputField'
        js += str(row[0])
        js += ' = document.getElementById("input'
        js += str(row[0])
        js += '");minusButton'
        js += str(row[0])
        js += '.addEventListener("click", event => {event.preventDefault();const currentValue'
        js += str(row[0])
        js += '= Number(inputField'
        js += str(row[0])
        js += '.value) || 0;inputField'
        js += str(row[0])
        js += '.value = currentValue'
        js += str(row[0])
        js += '- 1;}); plusButton'
        js += str(row[0])
        js += '.addEventListener("click", event => {event.preventDefault();const currentValue'
        js += str(row[0])
        js += '= Number(inputField'
        js += str(row[0])
        js += '.value) || 0; inputField'
        js += str(row[0])
        js += '.value = currentValue'
        js += str(row[0])
        js += '+ 1;});</script>'
        index += 1
    ## generate js for top submit button
    js += '<script>const submit1 = document.getElementById("submit1");' + '\n' + 'var url = "http://127.0.0.1:8000/vgs_step3/default/cart.html*?"'
    js += '\n'+ 'submit1.addEventListener("click", event => {' + '\n'
    index = 0
    while index < len(rows) -1:
        js += 'url += "' + str(index) + '=" + ' + 'inputField'
        js += str(index + 1)
        js += '.value.toString()' + '+ "&";' + '\n'
        index += 1
    js += 'url += "' + str(index) + '=" + ' + 'inputField'
    js += str(index + 1)
    js += '.value.toString();' + '\n'
    js += 'location.replace(url)' + '\n' + '});</script>\n'
    ## generate js for bottom submit button
    js += '<script>const submit2 = document.getElementById("submit2");' + '\n' + 'var url = "http://127.0.0.1:8000/vgs_step3/default/cart.html*?"'
    js += '\n'+ 'submit2.addEventListener("click", event => {' + '\n'
    index = 0
    while index < len(rows) -1:
        js += 'url += "' + str(index) + '=" + ' + 'inputField'
        js += str(index + 1)
        js += '.value.toString()' + '+ "&";' + '\n'
        index += 1
    js += 'url += "' + str(index) + '=" + ' + 'inputField'
    js += str(index + 1)
    js += '.value.toString();' + '\n'
    js += 'location.replace(url)' + '\n' + '});</script>\n'
    return locals()


@auth.requires_login()
def cart():
    from datetime import datetime
    message = session.message
    carts_id = db.carts.insert(user_id = auth.user_id, cart_time = datetime.now())
    item_num = len(request.vars)
    cart_total = 0.0
    index = 0
    while index < len(request.vars):
        if str(request.vars[str(index)]) != '0':
            rows = (db(db.products.id == index + 1).select())
            item_name = rows[0].name
            item_desc = rows[0].description
            item_unit = rows[0].unit
            item_est_price = rows[0].est_price
            item_qty = request.vars[str(index)]
            item_total = item_est_price * int(item_qty)
            cart_total = float(item_total) + cart_total
            db.cart_items.insert(cart_id = carts_id, product_id = index, name = item_name, description = item_desc, unit = item_unit, est_price = item_est_price, qty = item_qty, total = item_total)
        index += 1
    rows = db(db.cart_items.cart_id == carts_id).select()
    return locals()


@auth.requires_login()
def history():
    return dict()

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
