from opt import db,app
from opt.models import *


def main():
    f=open('file.csv')
    reader=csv.reader(f)
    for name, letter in reader:
        month=MonthC(month_name=name,month_letter=letter)
        db.session.add(month)
        print(f'The month {name} has been added')
    db.session.commit()
    



if __name__ == '__main__':
    main()