import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, RadioField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_wtf import RecaptchaField
from utils import process_images

main = Flask(__name__)

main.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
main.config['UPLOAD_FOLDER'] = 'static/uploads'
main.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  

main.config['RECAPTCHA_PUBLIC_KEY'] = '6Ld6hscsAAAAAErc3DKGtKqxtYjS7DRPZ4dT6f7y'
main.config['RECAPTCHA_PRIVATE_KEY'] = '6Ld6hscsAAAAAJxlyG0agjtJA440k9CBQcQLzN7n'
main.config['RECAPTCHA_USE_SSL'] = False

bootstrap = Bootstrap(main)

os.makedirs(main.config['UPLOAD_FOLDER'], exist_ok=True)

class MergeForm(FlaskForm):
    image1 = FileField('Первое изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])
    image2 = FileField('Второе изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])
    direction = RadioField('Направление склейки', choices=[
        ('horizontal', 'По горизонтали (слева направо)'),
        ('vertical', 'По вертикали (сверху вниз)')
    ], default='horizontal', validators=[DataRequired()])
    
    recaptcha = RecaptchaField()
    submit = SubmitField('Склеить и показать графики')

@main.route('/', methods=['GET', 'POST'])
def index():
    form = MergeForm()
    result_data = None
    
    if form.validate_on_submit():
        f1 = form.image1.data
        f2 = form.image2.data
        
        filename1 = "img1_" + f1.filename
        filename2 = "img2_" + f2.filename
        
        path1 = os.path.join(main.config['UPLOAD_FOLDER'], filename1)
        path2 = os.path.join(main.config['UPLOAD_FOLDER'], filename2)
        
        f1.save(path1)
        f2.save(path2)
        
        try:
            result_data = process_images(path1, path2, form.direction.data)
        except Exception as e:
            flash(f'Ошибка при обработке изображений: {str(e)}', 'danger')
            return redirect(url_for('index'))

    return render_template('index.html', form=form, result=result_data)

if __name__ == '__main__':
    main.run(debug=True)