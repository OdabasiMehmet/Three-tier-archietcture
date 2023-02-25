from flask import Flask, render_template, request, redirect
import pymysql.cursors
import boto3
import os

# Configure Flask app
app = Flask(__name__)
app.config['BLOG_TITLE'] = 'My Blog' # Specify your blog title here

# Configure RDS database connection
db = pymysql.connect(host='database-1.cezykzodxgyd.us-east-1.rds.amazonaws.com', user='admin', password=os.environ['DB_PASSWORD'], db='dailyblog', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

# Configure S3 bucket
s3 = boto3.client('s3', region_name='us-east-1')
bucket_name = 'bucketforblog'

# Define routes
@app.route('/')
def index():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY created DESC')
    posts = cursor.fetchall()
    return render_template('index.html', posts=posts)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files['image']
        
        # Upload image to S3 bucket
        image_key = image.filename
        s3.upload_fileobj(image, bucket_name, image_key, ExtraArgs={'ACL': 'public-read'})
        
        # Insert post into database
        cursor = db.cursor()
        cursor.execute('INSERT INTO posts (title, content, image_key) VALUES (%s, %s, %s)', (title, content, image_key))
        db.commit()
        
        return redirect('/')
    else:
        return render_template('create_post.html', title=app.config['BLOG_TITLE'])

# Start the Flask app
if __name__ == '__main__':
    app.run()

