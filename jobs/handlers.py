from flask import render_template, g, request, redirect, url_for
import datetime
import jobs.db as db
from jobs.app import app

@app.teardown_appcontext
def close_connection(exception):
    connection = getattr(g, '_connection', None)
    if connection is not None:
        connection.close()

@app.route('/')
@app.route('/jobs')
def jobsview():
    jobs = db.execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id')
    return render_template('index.html', jobs=jobs)

@app.route('/job/<job_id>')
def jobview(job_id):
    job = db.execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id WHERE job.id = ?', [job_id], single=True)
    return render_template('job.html', job=job)

@app.route('/employer/<employer_id>')
def employerview(employer_id):
    employer = db.execute_sql( 'SELECT * FROM employer WHERE id=?', [employer_id], single=True)
    jobs = db.execute_sql('SELECT job.id, job.title, job.description, job.salary FROM job JOIN employer ON employer.id = job.employer_id WHERE employer.id = ?', [employer_id])
    reviews = db.execute_sql('SELECT review, rating, title, date, status FROM review JOIN employer ON employer.id = review.employer_id WHERE employer.id = ?', [employer_id])
    return render_template("employer.html", employer=employer, jobs=jobs, reviews=reviews)

@app.route('/employer/<employer_id>/review',methods=('GET', 'POST'))
def reviewview(employer_id):
    if request.method == 'POST':
        review = request.form['review']
        rating = request.form['rating']
        title = request.form['title']
        status = request.form['status']
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        db.execute_sql('INSERT INTO review (review, rating, title, date, status, employer_id) VALUES (?, ?, ?, ?, ?, ?)',(review, rating, title, date, status, employer_id),commit=True )
        return redirect(url_for('employer', employer_id=employer_id))
    return render_template('review.html', employer_id=employer_id)