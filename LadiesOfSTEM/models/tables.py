# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from datetime import datetime

def get_first_name():
    name = 'Nobody'
    if auth.user:
        name = auth.user.first_name
    return name

#Categories - dnreyes
GRAD_YEARS = ['0', '1', '2', '3', '4', '5+','N/A']
FIELDS = ['Applied Mathemathics & Stats', 'Computer Science', 'Computer Engineering', 'Biomolecular Engineering',
                    'Electrical Engineering', 'Technology Management','Other', 'N/A']
GRADE = ['Fifth Year', 'Fourth Year', 'Third Year', 'Second Year', 'First Year', 'Transfer','12th', '11th', '10th', '9th', '6-8th', 
         '1-5th', 'N/A']
TYPE = ['middle/highschool', 'undergraduate', 'graduate', 'professional']

#Table for people's profiles - dnreyes
db.define_table('profile',
                 Field("profile_pic", 'upload'),
                 Field('user_id', db.auth_user),
                 Field('I_am_a', requires = IS_IN_SET(TYPE)),
                 Field('name'),
                 Field('age'),
                 Field('email'),
                 Field('city_from'),
                 Field('schooling'),
                 Field('grade', requires = IS_IN_SET(GRADE)),
                 Field('area_of_study', requires = IS_IN_SET(FIELDS)),
                 Field('grad_years_completed', requires = IS_IN_SET(GRAD_YEARS)),
                 Field('employment'),
                 Field('about_you', 'text'),
                 Field('specify', 'text'),
                 Field('hopes', 'text'),
                 )

#Stuff for profiles
db.profile.name.default = get_first_name()
db.profile.name.writable = False
db.profile.user_id.default = auth.user_id
db.profile.user_id.writable = False
db.profile.user_id.readable = False
db.profile.age.required = True
db.profile.age.required = IS_INT_IN_RANGE(0, 100, error_message='Please provide your age.')
db.profile.email.requires = IS_EMAIL()
db.profile.email.readable = False
db.profile.schooling.required = True
db.profile.specify.default = 'What have you worked on or studied in your field? We wanna hear what you do!'
db.profile.about_you.default = "What's your story?"
db.profile.hopes.default = 'What do you hope to get from Ment-Her?'

########################################################################################

# Forums

db.define_table('category',
                Field('name', requires=(IS_SLUG(),IS_LOWER(), IS_NOT_IN_DB(db, 'category.name'))))

db.define_table('post',
                Field('category', 'reference category', writable = False, readable = False),
                Field('date_posted', 'datetime', default=datetime.utcnow()),
                Field('title', 'string', requires = IS_NOT_EMPTY()),
                Field('body', 'text', requires = IS_NOT_EMPTY()),
                auth.signature) # created_on, created_by, modified_on, modified_by, is_active

db.define_table('comm',
                Field('post','reference post',writable = False, readable = False),
                Field('parent_comm','reference comm',writable = False, readable = False),
                Field('body','text'),
                auth.signature)


def author(id):
    if id is None:
        return "Anonymous"
    else:
        user = db.auth_user(id)
        return ('%(first_name)s %(last_name)s' % user)

#Table for Inbox  
db.define_table('inbox',
  Field('subj', 'string', label="Subject"),
  Field('fromwho', db.auth_user, label="From"),
  Field('datereceived', 'datetime', label="Date: "),
  Field('stuff', 'text', label="Content"),
  Field('opened', 'boolean')
  )
  #Stuff for messages

db.inbox.id.readable = False
db.inbox.datereceived.default = datetime.utcnow()
db.inbox.datereceived.writable = False
db.inbox.opened.readable = False