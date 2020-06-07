# ---- index page ----
def index():
    session.message = 'Next delivery: Jul 2, 2020'
    message = session.message
    return locals()

@auth.requires_login()
def order():
    message = session.message
    rows = db(db.products).select()
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
