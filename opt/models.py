from datetime import datetime
from flask_login import UserMixin
from opt import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

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



class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    #foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


#to define the category of underlying/Instrument: underyling or derivative
class Instrument(db.Model):
    __tablename__ = 'instrument'
    id = db.Column(db.Integer, primary_key=True)
    name_inst=db.Column(db.String(20), nullable=False)
    descr_inst=db.Column(db.String(20), nullable=False)
    
    #relationships
    instname= db.relationship('Stock', backref='inst_fin', lazy=True)
    
    def __repr__(self):
        return f"Instrument('{self.name_inst}', '{self.descr_inst}')"



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
   
class Options(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    #date of calculation
    theo_price=db.Column(db.Float(8), nullable=False)
    date_calc=db.Column(db.DateTime, default=datetime.utcnow) 
    #strike price
    opt_strike=db.Column(db.Float(8), nullable=False)
    #symbol of option
    opt_sym=db.Column(db.String(8), default=datetime.utcnow)
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
        return f"GreeksOpt('{self.delta_put}','{self.gamma_put}', '{self.theta_put}','{self.vega_put}', '{self.rho_put}')"
        return f"Greeks('{self.delta_call}','{self.gamma_call}', '{self.theta_call}','{self.vega_call}', {'self.rho_call'})"
