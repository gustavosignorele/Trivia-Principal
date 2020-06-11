#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apptrivia import db
from models.models import  User, Role

# agregamos 2 usuarios
u1 = User(name='user1', email='bla@antel.com.uy')
u2 = User(name='user2', email='bla2@antel.com.uy')
u1.set_password("bla")
u2.set_password("bla2")
db.session.add_all([u1, u2])
db.session.commit()

db.session.add_all(
         [Role(rolename='admin', user=u1),
          Role(rolename='user', user=u1),  # multiples roles
          Role(rolename='user', user=u2)])
db.session.commit()