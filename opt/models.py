from datetime import datetime
from flask_login import UserMixin
from opt import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
import json
from time import time

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))


followers = db.Table('followers',
            db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))




class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    password = db.Column(db.String(60), nullable=False)
   
    last_message_read_time = db.Column(db.DateTime)

    #relationships
    followed = db.relationship('User', secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
   
    liked = db.relationship('PostLike',foreign_keys='PostLike.user_id', 
                            backref='user', lazy='dynamic')

    posts = db.relationship('Post', backref='author', lazy=True)

    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')

    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')

    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')

    FileContent=db.relationship('FileContent',backref='owner',lazy=True)

    #functions
    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0


    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.date_posted.desc())

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)



    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class FileContent(db.Model):
    __tablename__='filecontent'
    id= db.Column(db.Integer, primary_key=True)
    filename=db.Column(db.String(400), nullable=False)
    path_file=db.Column(db.String(500),unique=True, nullable=False)
    date_upload= db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    down_date=db.Column(db.DateTime, nullable=True)
    extension=db.Column(db.String(5), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



class Message(db.Model):
    __tablename__='message'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)

class Notification(db.Model):
    __tablename__='notification'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted= db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    #foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"



class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))




#to define the category of underlying/Instrument: underyling or derivative
class Instrument(db.Model):
    __tablename__ = 'instrument'
    id = db.Column(db.Integer, primary_key=True)
    name_inst=db.Column(db.String(20), nullable=False)
    descr_inst=db.Column(db.String(20), nullable=False)
    
    #relationships
    instname= db.relationship('Stock', backref='inst_fin', lazy=True)
    

    def __repr__(self):
        return f"Instrument('{self.name_inst}')"



class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
     #underyling name/description
    stock_name=db.Column(db.String(20), nullable=False)
    stock_sym=db.Column(db.String(20), nullable=False)
       
    #relationships
    #opt_list=db.relationship('Options', backref='underlying', lazy=True)
    company_l=db.relationship('Companies', backref='stock_exch', lazy=True)  
      
    #foreign keys
    inst_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    
    def __repr__(self):
        return f"Stock('{self.stock_sym}', '{self.stock_name}')"

      
class Companies(db.Model):
   __tablename__='companies'
   id=db.Column(db.Integer,primary_key=True)
   name_company=db.Column(db.String(30), nullable=False)
   sym_company=db.Column(db.String(8), nullable=False)
   
   #foreign key
   stock_id = db.Column(db.Integer,db.ForeignKey('stock.id'), nullable=False)
   
   def __repr__(self):
       return f"Companies('{self.name_company}','{self.sym_company}')"
      
class Futures(db.Model):
    __tablename__ = 'futures'
    id = db.Column(db.Integer, primary_key=True)
    fut_name=db.Column(db.String(20), nullable=False)
    fut_sym=db.Column(db.String(8), nullable=False)
   
   #relationships
    fut_list=db.relationship('FutContract', backref='futures', lazy=True)
   
    #foreign keys
    inst_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    
    def __repr__(self):
        return f"Futures('{self.fut_name}', '{self.fut_sym}')"
      
class FutContract(db.Model):
    __tablename__ = 'futcontract'
    id = db.Column(db.Integer, primary_key=True)
    fut_year=db.Column(db.String(10), nullable=False)    
    futctr_sym=db.Column(db.String(8), nullable=False)
    fut_exp=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fut_price=db.Column(db.Float(8), nullable=False)
    date_price=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fut_sett=db.Column(db.Float(8),nullable=True)
    
    #relationships
    fut_list=db.relationship('Options', backref='fut_ctr', lazy=True)
    #foreign keys
    fut_id=db.Column(db.Integer,db.ForeignKey('futures.id'),nullable=False)  
    ctrf_month=db.Column(db.Integer,db.ForeignKey('month_c.id'),nullable=False)  
    
    def __repr__(self):
        return f"FutContract('{self.futctr_sym}', '{self.fut_price}','{self.fut_sett}' ,'{self.fut_exp}')"    
      
  
class MonthC(db.Model):
    __tablename__= 'month_c'
    id = db.Column(db.Integer, primary_key=True)
    month_name=db.Column(db.String(20), nullable=False)
    month_letter=db.Column(db.String(8), nullable=False)
    
   #relationship
    month_opt=db.relationship('Options', backref='ctr_month')
    month_fut=db.relationship('FutContract', backref='ctrfut_month')
    def __repr__(self):
        return f"MonthC('{self.month_name}','{self.month_letter}')"
   

   #It needs to be checked
class Options(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    under_n=db.Column(db.String(8), nullable=False)
    #date of calculation
    theo_price=db.Column(db.Float(8), nullable=False)
    date_calc=db.Column(db.DateTime, default=datetime.utcnow) 
    #strike price
    opt_strike=db.Column(db.Float(8), nullable=False)
    #symbol of option
    opt_sym=db.Column(db.String(8), nullable=False)
    # expiry date of option
    exp_date=db.Column(db.DateTime, default=datetime.utcnow) 
    #date of estimated value. for instance in 10 days
    date_val=db.Column(db.DateTime, default=datetime.utcnow) 
    vol_opt=db.Column(db.Float(6),nullable=False, default=0.30) 
      
    #relationship
    greeks=db.relationship('GreeksOpt',backref='option', lazy=True)
      
    #Foreign Keys
    futctr_id = db.Column(db.Integer, db.ForeignKey('futcontract.id'), nullable=False)
    contract= db.Column(db.Integer, db.ForeignKey('month_c.id'), nullable=False)
    def __repr__(self):
        return f"Options('{self.opt_sym}','{self.opt_strike}', '{self.exp_date}','{self.theo_price}')"



class GreeksOpt(db.Model):
    __tablename__='greeksopt'
    id = db.Column(db.Integer, primary_key=True)
    delta_put=db.Column(db.Float(10),nullable=False)
    delta_call=db.Column(db.Float(10),nullable=False)
   
    gamma_put=db.Column(db.Float(10),nullable=False)
    gamma_call=db.Column(db.Float(10),nullable=False)
    
    theta_put=db.Column(db.Float(10),nullable=False)
    theta_call=db.Column(db.Float(10),nullable=False)
   
    vega_put=db.Column(db.Float(10),nullable=False)
    vega_call=db.Column(db.Float(10),nullable=False)
   
    rho_put=db.Column(db.Float(10),nullable=False)
    rho_call=db.Column(db.Float(10),nullable=False)
   
   #Foreign Keys
    opt_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)
   
   
    def __repr__(self):
        return (f"GreeksOpt('{self.delta_put}','{self.gamma_put}', '{self.theta_put}','{self.vega_put}', '{self.rho_put}',\
                '{self.delta_call}','{self.gamma_call}', '{self.theta_call}','{self.vega_call}', '{self.rho_call})")

