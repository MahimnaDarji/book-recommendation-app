from flask import Flask,render_template,request,redirect,session
import mysql.connector
import os
import pickle
import numpy as np

popular_df = pickle.load(open('Templates/popular.pkl','rb'))
pt = pickle.load(open('Templates/pt.pkl','rb'))
books = pickle.load(open('Templates/books.pkl','rb'))
similarity_scores = pickle.load(open('Templates/similarity_scores.pkl','rb'))

app=Flask(__name__)
app.secret_key=os.urandom(24)

conn=mysql.connector.connect(host="localhost",user="root",database="thereadingroom")
cursor=conn.cursor()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/home')
def home():
    if 'database' in session:
        return render_template('index.html')
    else:
        return redirect('/')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')

    cursor.execute("""SELECT * FROM `database` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email,password))
    users=cursor.fetchall()
    if len(users)>0:
        session['database']=users[0][0]
        return redirect('/home')
    else:
        return redirect('/')

@app.route('/add_user',methods=['POST'])
def add_user():
    name=request.form.get('uname')
    email=request.form.get('uemail')
    password=request.form.get('upassword')

    cursor.execute("""INSERT INTO `database` (`user_id`,`name`,`email`,`password`)
    VALUES(NULL,'{}','{}','{}')""".format(name,email,password))
    conn.commit()
    return redirect('/')

@app.route('/trendingbooks')
def trendingbooks():
    return render_template('trendingbooks.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['Num_Ratings'].values),
                           rating=list(popular_df['Avg_Rating'].values))

@app.route('/browse')
def browse():
    return render_template('browse.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)

    print(data)

    return render_template('browse.html',data=data)

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/logout')
def logout():
    session.pop('database')
    return render_template('/login.html')

if __name__=="__main__":
    app.run(debug=True)