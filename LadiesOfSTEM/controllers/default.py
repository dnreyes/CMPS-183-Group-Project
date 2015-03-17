# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

POSTS_PER_PAGE = 10

def index():
    """
    If the user is logged in, redirect to their homepage
    """
    if auth.user is not None:
        redirect(URL('default', 'private'))
    ##If logged in, but no profile, then it would go to make a profile

    return dict()
    
############################################################################
# Forums

def get_category():
    category_name = request.args(0)
    category = db.category(name=category_name)
    if not category:
        session.flash = 'page not found'
        redirect(URL('index'))
    return category

@auth.requires_login()
def forum():
    """ Displays the list of the forum threads """
    rows = db(db.category).select()
    return locals()

@auth.requires_login()
def create_post():
    category = get_category()
    db.post.category.default = category.id
    form = SQLFORM(db.post).process(next='view_post/[id]')
    return locals()

@auth.requires_login()
def edit_post():
    id = request.args(0,cast=int)
    form = SQLFORM(db.post, id, showid=False).process(next='view_post/[id]')
    return locals()

@auth.requires_login()
def view_post():
    id = request.args(0,cast=int)
    post = db.post(id) or redirect(URL('forum'))
    comment = db(db.comm.post==post.id).select(orderby=~db.comm.created_on,limitby=(0,1)).first()
    db.comm.post.default = id
    db.comm.parent_comm.default = comment
    form = SQLFORM(db.comm).process()
    comments = db(db.comm.post==post.id).select(orderby=db.comm.created_on)
    return locals()

@auth.requires_login()
def list_posts_by_datetime():
    category = get_category()
    page = request.args(1,cast=int,default=0)
    start = page*POSTS_PER_PAGE # if on page 0, starts with post#0; if page 1, starts with post#10
    stop = start+POSTS_PER_PAGE
    rows = db(db.post.category==category.id).select(orderby=~db.post.created_on,limitby=(start,stop)) # ~ means reverse order
    return locals()
    
#####################################################################################################################
# Profiles

@auth.requires_login()
def private():
    """ Currently displays the member list."""
    q = db.profile

        
    def generate_view_button(row):
        view_button = A("View", _class='btn' 'btn-primary',_href=URL('default', 'view_profile',args=[row.id]))
        return view_button

    links = [
        dict(header="", body=generate_view_button),
            ]

    form = SQLFORM.grid(q,
            fields=[db.profile.profile_pic,
                    db.profile.name,
                    db.profile.user_id,
                    db.profile.I_am_a,
                    db.profile.area_of_study,
                    db.profile.about_you],
        create=False,
        editable=False,
        deletable=False,
        details=False,
        links=links,
        paginate=10,
        csv=False,
        )
    return dict(form=form)

@auth.requires_login()
def add_profile():
    """Add a post."""
    form = SQLFORM(db.profile)
    if form.process().accepted:
        # Successful processing.
        session.flash = T("inserted")
        db.profile(request.args(0)) or redirect(URL('default', 'private'))
    return dict(form=form)


@auth.requires_login()
def edit_profile():
    id = request.args(0,cast=int)
    form = SQLFORM(db.profile, id, showid=False).process(next='view_profile/[id]')
    return locals()

def view_profile():
	""" View profile """
	p = db.profile(request.args(0)) or redirect(URL('default','index'))
	form = SQLFORM(db.profile, record=p, readonly=True)
	return dict(form=form)

#########################################
#################Inbox Messaging
@auth.requires_login()
def sendmessage():

    '''Messaging System Part 1: The Sending'''
    form = SQLFORM.factory(
    Field('sendTo', author(auth.user_id), label="To", requires=IS_NOT_EMPTY()),
    Field('Subject', 'string', default = 'No Subject', length=255),
    Field('Body', 'text', default='', label="Content")
    )
    form.add_button('Cancel', URL('default', 'index'))
    if form.process().accepted:
        #Needs to push into the inbox table
        db.inbox.insert(fromwho = form.vars.sendTo, subj = form.vars.Subject.lower(),stuff = form.vars.Body)
        session.flash = T('Sent')
        redirect(URL('default', 'viewmessage'))
    return dict(form=form)

@auth.requires_login()
def viewmessage():

    '''Messaging System Part 2: The Viewing'''
    #Needs to be worked on
    q = db.inbox
    start_index = 1 
    form = SQLFORM.grid(q, 
    args=request.args[:start_index],
    fields=[db.inbox.subj, db.inbox.fromwho, db.inbox.datereceived],
    create = False,
    editable = False,
    #details = False,
    csv=False,
    )

    return dict(form=form)

    
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
