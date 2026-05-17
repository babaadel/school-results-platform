import pandas as pd
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_results.db'
app.config['SECRET_KEY'] = '123'
db = SQLAlchemy(app)

class StudentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    grade = db.Column(db.String(20))
    status = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    count = StudentResult.query.count()
    return render_template('index.html', count=count)

@app.route('/search', methods=['POST'])
def search():
    sid = request.form.get('student_id').strip()
    student = StudentResult.query.filter_by(student_id=sid).first()
    count = StudentResult.query.count()
    
    if student:
        print(f"✅ تم العثور على الطالب: {student.name}")
        return render_template('index.html', student=student, count=count)
    else:
        print(f"❌ لم يتم العثور على الرقم: {sid}")
        flash(f'الرقم {sid} غير موجود في قاعدة البيانات')
        return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        file = request.files.get('excel_file')
        try:
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                sid = str(row['الرقم المدرسي']).strip()
                # إذا كان الرقم ينتهي بـ .0 (بسبب اكسل) سنحذفه
                if sid.endswith('.0'): sid = sid[:-2]
                
                existing = StudentResult.query.filter_by(student_id=sid).first()
                if existing:
                    existing.name = row['الاسم']
                    existing.grade = str(row['المعدل'])
                    existing.status = row['الحالة']
                else:
                    new_student = StudentResult(student_id=sid, name=row['الاسم'], 
                                               grade=str(row['المعدل']), status=row['الحالة'])
                    db.session.add(new_student)
            db.session.commit()
            return "<h2>تم الرفع بنجاح!</h2> <a href='/'>اذهب للبحث الآن</a>"
        except Exception as e:
            return f"خطأ في الرفع: {e}"
    return '<form method="post" enctype="multipart/form-data"><input type="file" name="excel_file"><button>رفع</button></form>'

if __name__ == '__main__':
    app.run(debug=True)
