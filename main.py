#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask import render_template
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import requests
from DataframeManager import DataframeManager
from form import LoginForm, RegisterForm, AddExercise, EditWorkout, SearchUser


app = Flask(__name__)
app.secret_key = "GRHGRTHJJ2349qGFHHTHcdfseghGRYHJ9898897MLPKLqX"
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///gym_data_tracker.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CONFIGURE TABLES
Base = declarative_base()

# ETABLISH LOGIN
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    # Relation with Exercise table :
    exercises = relationship("Exercise", back_populates="author")

    # Relation with ExercisePerformance table :
    performances = relationship("ExercisePerformance", back_populates="exercise_performance_user")


class Exercise(db.Model):
    __tablename__ = "exercise_details"
    id = db.Column(db.Integer, primary_key=True)

    # ForeignKey User (primary key of User):
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    exercise_name = db.Column(db.String(30), nullable=False)

    author = relationship("User", back_populates="exercises")
    performance = relationship("ExercisePerformance", back_populates="exercise")


class ExercisePerformance(db.Model):
    __tablename__ = "exercise_performance"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table :
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    exercise_performance_user = relationship("User", back_populates="performances")

    # Relation with Exercise table :
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise_details.id"))
    exercise = relationship("Exercise", back_populates="performance")

    date_performance = db.Column(db.String(20), nullable=True)
    global_performance = db.Column(db.String(30), nullable=False)

    three_reps = db.Column(db.Integer, nullable=True)
    three_rpe = db.Column(db.Integer, nullable=True)
    two_reps = db.Column(db.Integer, nullable=True)
    two_rpe = db.Column(db.Integer, nullable=True)
    one_reps = db.Column(db.Integer, nullable=True)
    one_rpe = db.Column(db.Integer, nullable=True)
    ten_reps = db.Column(db.Integer, nullable=True)
    fifteen_reps = db.Column(db.Integer, nullable=True)
    twenty_reps = db.Column(db.Integer, nullable=True)


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            get_username = User.query.filter_by(username=form.username.data).first()
            if get_username:
                if check_password_hash(pwhash=get_username.password, password=form.password.data):
                    login_user(get_username)
                    return redirect(url_for("dashboard"))
                else:
                    flash("Mot de passe incorrect")
                    return redirect(url_for("login"))
            else:
                flash("Pseudonyme incorrect")
                return redirect(url_for('login'))
        return render_template("login.html", form=form, is_logged=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash("Cet email est déjà associé à un compte.")
                return redirect(url_for('register'))
            elif User.query.filter_by(username=form.username.data).first():
                flash("Ce pseudo est déjà utilisé.")
                return redirect(url_for('register'))
            else:
                hash_and_salted_password = generate_password_hash(
                    password=form.password.data,
                    method='pbkdf2:sha256',
                    salt_length=8
                )
                new_user = User(
                    email=form.email.data,
                    username=form.username.data,
                    password=hash_and_salted_password
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for("dashboard"))
        return render_template("register.html", form=form, is_logged=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route('/dashboard')
@login_required
def dashboard():
    # Create a global performance DataFrame :
    dataframe_manager = DataframeManager()
    df_exercise_performance = dataframe_manager.create_global_dataframe(table=ExercisePerformance,
                                                                        user_id=current_user.id)
    df_exercise_performance = df_exercise_performance.sort_values(by="Date", ascending=False)[:15]

    # Create a new specific DataFrame for each Exercise :
    get_unique_exercise = Exercise.query.filter_by(user_id=current_user.id).all()
    unique_exercise = []
    for exercise in get_unique_exercise:
        unique_exercise.append(exercise.exercise_name)

    all_specific_exercises_df = []
    for _exercise in unique_exercise:
        current_exercise = Exercise.query.filter_by(user_id=current_user.id, exercise_name=_exercise).first()
        current_performances = ExercisePerformance.query.filter_by(user_id=current_user.id,
                                                                   exercise_id=current_exercise.id).all()
        # print(f"{current_performances[0].exercise.exercise_name} : {current_performances[0].global_performance}")

        new_df = dataframe_manager.create_specific_dataframe(table=Exercise,
                                                             exercise_id=current_exercise.id).sort_values(by="Date",
                                                                                                          ascending=
                                                                                                          False)
        all_specific_exercises_df.append(new_df)

    # Delete 'performance_id' column of specific exercise DataFrame :
    for df in all_specific_exercises_df:
        df = df.drop(['performance_id'], axis=1, inplace=True)

    # Get all exercises names from Database :
    get_all_exercises = Exercise.query.filter_by(user_id=current_user.id).all()
    all_exercises_names = [exercise.exercise_name.title() for exercise in get_all_exercises]

    if len(df_exercise_performance) == 0:
        has_data = False
    else:
        has_data = True

    # Check if the first letter username is a vowel :
    vowel = ["A", "E", "I", "O", "U"]
    if current_user.username[0] in vowel:
        title_content = f"Tableau de bord d'{current_user.username}"
    else:
        title_content = f"Tableau de bord de {current_user.username}"

    return render_template("dashboard.html",
                           is_logged=current_user.is_authenticated,
                           global_performance_tables=[df_exercise_performance.to_html(classes='data', index=False)],
                           global_performance_title="Vos 15 dernières performances globales :",
                           specific_tables=[df.to_html(classes='data', index=False) for df in all_specific_exercises_df],
                           specific_titles=all_exercises_names,
                           has_data=has_data,
                           title_content=title_content)


@app.route('/<int:user_id>/add', methods=['POST', 'GET'])
@login_required
def add_new_exercise(user_id):
    form = AddExercise()
    if form.validate_on_submit():
        if user_id != current_user.id:
            abort(404)
        else:
            new_exercise = Exercise(
                exercise_name=form.exercise_name.data,
                author=current_user
            )
            db.session.add(new_exercise)
            db.session.commit()
            flash("L'exercice a été ajouté avec succès.")
            return redirect(url_for('show_workout', user_id=current_user.id))
    return render_template("add.html", form=form, is_logged=current_user.is_authenticated,
                           title_content="Commencer à tracker un nouvel exercice")


@app.route('/show-workout/<int:user_id>')
@login_required
def show_workout(user_id):
    if user_id != current_user.id:
        abort(404)
    else:
        all_exercises = Exercise.query.filter_by(user_id=user_id).all()
        return render_template("show_workout.html", is_logged=current_user.is_authenticated, all_exercises=all_exercises,
                               user_id=user_id,
                               title_content="Ajouter une nouvelle performance")


@app.route('/edit-workout/<int:user_id>/<int:exercise_id>', methods=['POST', 'GET'])
@login_required
def edit_workout(user_id, exercise_id):
    exercise = Exercise.query.get(exercise_id)
    # print(exercise)
    form = EditWorkout()
    if form.validate_on_submit():
        new_performance = ExercisePerformance(
            date_performance=form.date_field.data,
            exercise_performance_user=current_user,
            exercise=exercise,
            global_performance=form.global_performance.data,
            three_reps=form.three_reps.data,
            three_rpe=form.three_rpe.data,
            two_reps=form.two_reps.data,
            two_rpe=form.two_rpe.data,
            one_reps=form.one_reps.data,
            one_rpe=form.one_rpe.data,
            ten_reps=form.ten_reps.data,
            fifteen_reps=form.fifteen_reps.data,
            twenty_reps=form.twenty_reps.data,
        )
        db.session.add(new_performance)
        db.session.commit()
        flash("Les nouvelles données ont correctement été ajoutées.")
        return redirect(url_for('dashboard'))
    return render_template("edit_workout.html", is_logged=current_user.is_authenticated, exercise=exercise, form=form,
                           title_content=f"{exercise.exercise_name.title()} : Ajout d'une nouvelle performance")


@app.route('/advanced-edit/<int:user_id>/<int:exercise_id>')
@login_required
def advanced_edit(user_id, exercise_id):
    dataframe_manger = DataframeManager()
    exercise_df = dataframe_manger.create_specific_dataframe(table=Exercise, exercise_id=exercise_id)
    exercise_df['Editer'] = "Editer"
    exercise_df['Delete'] = "Supprimer"
    if len(exercise_df) == 0:
        has_data = False
    else:
        has_data = True
    return render_template("advanced_edit.html",
                           is_logged=current_user.is_authenticated,
                           column_names=exercise_df.columns.values,
                           row_data=list(exercise_df.values.tolist()),
                           link_delete="Delete",
                           link_edit="Editer",
                           zip=zip,
                           exercise=dataframe_manger.exercise,
                           tables=[exercise_df.to_html(classes='data', index=True)],
                           has_data=has_data,
                           title_content=f"{dataframe_manger.exercise.exercise_name} : Modification d'une performance")


@app.route('/delete_performance/<int:user_id>/<int:performance_id>', methods=['POST', 'GET'])
@login_required
def delete_performance(user_id, performance_id):
    if request.method == 'POST':
        performance_to_delete = ExercisePerformance.query.filter_by(id=performance_id).first()
        get_exercise_id = performance_to_delete.exercise.id
        db.session.delete(performance_to_delete)
        db.session.commit()
        flash('Les données ont correctement été supprimées.')
        return redirect(url_for('advanced_edit', exercise_id=get_exercise_id, user_id=current_user.id))
    return redirect(url_for('dashboard'))


@app.route('/edit_performance/<int:user_id>/<int:performance_id>', methods=['POST', 'GET'])
@login_required
def edit_performance(user_id, performance_id):
    if request.method == 'POST':
        get_performance_data = ExercisePerformance.query.filter_by(id=performance_id).first()
        return render_template("change_performance.html", performance_data=get_performance_data,
                               title_content=f"Performance id{get_performance_data.id} : Modification")
    return redirect(url_for('dashboard', title_content=f"Tableau de bord de {current_user.username}"))


@app.route('/new_edit_performance/<int:user_id>/<int:performance_id>', methods=['POST'])
@login_required
def get_edit_performance(user_id, performance_id):
    print(performance_id)
    new_date_performance = request.form['date_performance']
    new_global_performance = request.form['global_performance']
    new_three_reps = request.form['three_reps']
    new_two_reps = request.form['two_reps']
    new_one_reps = request.form['one_reps']
    new_ten_reps = request.form['ten_reps']
    new_fifteen_reps = request.form['fifteen_reps']
    new_twenty_reps = request.form['twenty_reps']

    performance_to_update = ExercisePerformance.query.get(performance_id)
    performance_to_update.date_performance = new_date_performance
    performance_to_update.global_performance = new_global_performance
    performance_to_update.three_reps = new_three_reps
    performance_to_update.two_reps = new_two_reps
    performance_to_update.one_reps = new_one_reps
    performance_to_update.ten_reps = new_ten_reps
    performance_to_update.fifteen_reps = new_fifteen_reps
    performance_to_update.twenty_reps = new_twenty_reps
    db.session.commit()
    flash('Les données ont correctement été modifiées.')

    return redirect(url_for('advanced_edit', exercise_id=performance_to_update.exercise.id, user_id=current_user.id))


@app.route('/delete_workout/<int:user_id>/<int:exercise_id>')
@login_required
def delete_workout(user_id, exercise_id):
    # Delete all performances for the exercise :
    performance_to_delete = ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
    for performance in performance_to_delete:
        db.session.delete(performance)
        db.session.commit()

    # Finally, delete the exercise :
    exercise_to_delete = Exercise.query.filter_by(user_id=current_user.id, id=exercise_id).first()
    db.session.delete(exercise_to_delete)
    db.session.commit()

    flash("L'exercice a correctement été supprimé.")

    return redirect(url_for('dashboard'))


@app.route('/search', methods=['POST', 'GET'])
@login_required
def search_user():
    form = SearchUser()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.search_field.data).first()
        if user:
            return redirect(url_for('show_user', username=user.username))
        else:
            flash("Cet utilisateur n'existe pas.")
            return redirect(url_for('search_user'))
    return render_template("search.html",
                           is_logged=current_user.is_authenticated,
                           title_content="Rechercher un utilisateur",
                           form=form)


@app.route('/show-user/<path:username>')
@login_required
def show_user(username):
    get_user_info = User.query.filter_by(username=username).first()
    get_user_performance = ExercisePerformance.query.filter_by(user_id=get_user_info.id).all()
    dataframe_manager = DataframeManager()
    df_exercise_performance = dataframe_manager.create_global_dataframe(table=ExercisePerformance,
                                                                        user_id=get_user_info.id).sort_values(
        by="Date",
        ascending=False
    )[:15]
    if get_user_performance:
        has_data = True
    else:
        has_data = False

    # Generate Avatar :
    url_avatar = f"https://avatars.dicebear.com/api/miniavs/{get_user_info.username}.svg?b=%2333276d&r=50&size=100&scale=92"

    return render_template("show_user.html",
                           is_logged=current_user.is_authenticated,
                           url_avatar=url_avatar,
                           has_data=has_data,
                           user=get_user_info,
                           title_content=f"Profil de {get_user_info.username}",
                           global_performance_tables=[df_exercise_performance.to_html(classes='data', index=False)],
                           global_performance_title=f"Les 15 dernières performances globales ajoutées par {get_user_info.username} :",
                           )


if __name__ == "__main__":
    app.run(debug=True)
