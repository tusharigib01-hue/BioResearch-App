from flask import Flask, render_template, redirect, url_for, request, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import io, csv
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ====================
# UPLOAD CONFIG
# ====================
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'fastq', 'fq', 'bam', 'cram', 'vcf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ====================
# MODELS
# ====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    samples = db.relationship('Sample', backref='project', lazy=True)

class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_code = db.Column(db.String(50))
    sample_type = db.Column(db.String(50))
    disease = db.Column(db.String(100))
    storage = db.Column(db.String(50))
    status = db.Column(db.String(50))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

# ====================
# HELPERS
# ====================
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ====================
# LOGIN MANAGER
# ====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ====================
# INIT DB + DEFAULT DATA
# ====================
with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password='admin'))

    if not Project.query.first():
        db.session.add_all([
            Project(title='Cancer Genomics'),
            Project(title='Infectious Diseases'),
            Project(title='Population Genetics')
        ])

    db.session.commit()

# ====================
# AUTH ROUTES
# ====================
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ====================
# DASHBOARD
# ====================
@app.route('/dashboard')
@login_required
def dashboard():
    total_users = User.query.count()
    total_projects = Project.query.count()
    total_samples = Sample.query.count()

    active_samples = Sample.query.filter_by(status='Active').count()
    used_samples = Sample.query.filter_by(status='Used').count()
    archived_samples = Sample.query.filter_by(status='Archived').count()

    projects = Project.query.all()
    project_labels = [p.title for p in projects]
    project_counts = [len(p.samples) for p in projects]

    return render_template(
        'dashboard/dashboard.html',
        total_users=total_users,
        total_projects=total_projects,
        total_samples=total_samples,
        active_samples=active_samples,
        used_samples=used_samples,
        archived_samples=archived_samples,
        project_labels=project_labels,
        project_counts=project_counts
    )

# ====================
# SAMPLES CRUD
# ====================
@app.route('/samples')
@login_required
def samples():
    samples = Sample.query.all()
    return render_template('samples/samples.html', samples=samples)

@app.route('/samples/add', methods=['GET', 'POST'])
@login_required
def add_sample():
    projects = Project.query.all()

    if request.method == 'POST':
        sample = Sample(
            sample_code=request.form['sample_code'],
            sample_type=request.form['sample_type'],
            disease=request.form['disease'],
            storage=request.form['storage'],
            status=request.form['status'],
            project_id=request.form['project_id']
        )
        db.session.add(sample)
        db.session.commit()
        flash('Sample added successfully', 'success')
        return redirect(url_for('samples'))

    return render_template('samples/add_sample.html', projects=projects)

@app.route('/samples/edit/<int:sample_id>', methods=['GET', 'POST'])
@login_required
def edit_sample(sample_id):
    sample = Sample.query.get_or_404(sample_id)
    projects = Project.query.all()

    if request.method == 'POST':
        sample.sample_code = request.form['sample_code']
        sample.sample_type = request.form['sample_type']
        sample.disease = request.form['disease']
        sample.storage = request.form['storage']
        sample.status = request.form['status']
        sample.project_id = request.form['project_id']

        db.session.commit()
        flash('Sample updated successfully', 'success')
        return redirect(url_for('samples'))

    return render_template('samples/edit_sample.html', sample=sample, projects=projects)

@app.route('/samples/delete/<int:sample_id>', methods=['POST'])
@login_required
def delete_sample(sample_id):
    sample = Sample.query.get_or_404(sample_id)
    db.session.delete(sample)
    db.session.commit()
    flash('Sample deleted successfully', 'warning')
    return redirect(url_for('samples'))

# ====================
# EXPORT CSV
# ====================
@app.route('/samples/export')
@login_required
def export_samples():
    samples = Sample.query.all()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Sample Code', 'Project', 'Type', 'Disease', 'Storage', 'Status'])

    for s in samples:
        cw.writerow([
            s.sample_code,
            s.project.title if s.project else '',
            s.sample_type,
            s.disease,
            s.storage,
            s.status
        ])

    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)

    return send_file(output, mimetype='text/csv',
                     download_name='samples.csv',
                     as_attachment=True)

# ====================
# LAB MODULE ROUTES
# ====================
@app.route('/genomics')
@login_required
def genomics():
    return render_template('labs/genomics.html')

@app.route('/proteomics')
@login_required
def proteomics():
    return render_template('labs/proteomics.html')

@app.route('/clinical')
@login_required
def clinical():
    return render_template('labs/clinical.html')

# ====================
# UPLOAD SEQUENCING DATA (REAL SAVE)
# ====================
@app.route('/labs/<lab>/upload', methods=['POST'])
@login_required
def upload_sequencing(lab):
    file = request.files.get('sequencing_file')

    if not file or file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for(lab))

    if not allowed_file(file.filename):
        flash('Invalid file type', 'danger')
        return redirect(url_for(lab))

    filename = secure_filename(file.filename)
    lab_folder = os.path.join(app.config['UPLOAD_FOLDER'], lab)
    os.makedirs(lab_folder, exist_ok=True)

    file.save(os.path.join(lab_folder, filename))

    flash(f'File saved to {lab} lab successfully', 'success')
    return redirect(url_for(lab))

# ====================
# RUN
# ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
