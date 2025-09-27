from parentify.models.models import User
def add_super_admin(orm, email, first_name, last_name, password):
    user = orm.query(User).filter(User.email==email).first()
    if not user:
        user = User.create(orm, email, first_name, last_name, password, True, True)
    return user
# add_super_admin(orm,"admin@gmail.com", "adminadmin")