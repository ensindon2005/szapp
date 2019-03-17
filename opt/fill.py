from opt import db,app
from opt.models import *


month=['January','February', 'March','April','May',
        'June','July','August','September','October','November','December']

letter=['F','G','H','J','K','M','N','Q','U','V','X','Z']


def main():
    result= zip(month,letter)
    print(result)
'''
def main():
    with open('file.csv',r) as f:
        reader=csv.reader(f)
        for name, letter in reader:
            month=MonthC(month_name=name,month_letter=letter)
            db.session.add(month)
            print(f'The month {name} has been added')
        db.session.commit()
    
'''


if __name__ == '__main__':
    main()