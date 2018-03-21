from flask import Flask, render_template, g, request, redirect, url_for
import psycopg2
import humanize

app = Flask(__name__)

def get_db():
  """
  Returns the connection to the database, opening a new
  one if there is none
  """
  if not hasattr(g, 'db'):
    g.db = psycopg2.connect(dbname='flaskapp',
                            user='flaskapp',
                            password='hunter2',
                            host='127.0.0.1')

  return g.db


@app.teardown_appcontext
def close_db(error):
  """
  Closes the database connection on teardown
  """
  if hasattr(g, 'db'):
    g.db.close()

@app.route('/')
def show_guestbook():
  # Let's show all posts from the last week, with a maximum of
  # 100 posts
  sql = """
    SELECT 
      author, comment_text, posted_at 
    FROM 
      guestbook
    WHERE
      posted_at >= now() - interval '1 week'
    ORDER BY 
      posted_at DESC
    LIMIT
      100;
  """
  cur = get_db().cursor()
  cur.execute(sql)

  posts = []
  for post_in_db in cur.fetchall():
    posts.append({
      'author': post_in_db[0],
      'comment_text': post_in_db[1],
      'posted_at': humanize.naturaltime(post_in_db[2])
    })

  cur.close()

  return render_template('index.html', posts=posts)

@app.route('/add', methods=["POST"])
def add_post():
  sql = """
    INSERT INTO
      guestbook
      (author, comment_text, posted_at)
    VALUES
      (%s, %s, now());
  """
  db = get_db()
  cur = db.cursor()
  cur.execute(sql, (request.form['author'],
                    request.form['comment_text']))

  db.commit()
  return redirect(url_for('show_guestbook'))


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
