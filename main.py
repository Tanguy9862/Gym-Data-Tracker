#!/usr/bin/env python
import pandas
import pandas as pd
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask import render_template
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from DataframeManager import DataframeManager
from UserData import GetUserData
from PRManager import ManagerPR
from PlotData import Plot
from WilksCalculator import WilksCalculator
from form import LoginForm, RegisterForm, AddExercise, EditWorkout, SearchUser, AddPersonalRecord, EditBodyWeight
from datetime import datetime



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

# CREATE DATAFRAME MANAGER OBJECT
dataframe_manager = DataframeManager()

# CREATE PLOT OBJECT
plot_function = Plot()

# CREATE PR MANAGER OBJECT
pr_manager = ManagerPR()

# CREATE USER DATA OBJECT
user_data = GetUserData()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(15), nullable=False)

    # Relation with Exercise table:
    exercises = relationship("Exercise", back_populates="author")

    # Relation with ExercisePerformance table:
    performances = relationship("ExercisePerformance", back_populates="exercise_performance_user")

    # Relation with PrDetails table:
    prs = relationship("PrDetails", back_populates="prdetails_user")

    # Relation with Wilks table:
    wilks = relationship("Wilks", back_populates="wilks_data")


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

    date_performance = db.Column(db.String(20), nullable=False)
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


class PrDetails(db.Model):
    __tablename__ = "pr_details"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table:
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    prdetails_user = relationship("User", back_populates="prs")

    # PR Data:
    date = db.Column(db.String(20), nullable=False)
    lift_id = db.Column(db.Integer, nullable=True)
    max_bench = db.Column(db.Float, nullable=True)
    max_squat = db.Column(db.Float, nullable=True)
    max_deadlift = db.Column(db.Float, nullable=True)
    bodyweight = db.Column(db.Float, nullable=True)


class Wilks(db.Model):
    __tablename__ = "wilks_data"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table:
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    wilks_data = relationship("User", back_populates="wilks")

    # Wilks Data:
    date = db.Column(db.String(20), nullable=False)
    bodyweight = db.Column(db.Float, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    wilks_coeff = db.Column(db.Float, nullable=False)


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            if len(username) and len(password) != 0:
                get_username = User.query.filter_by(username=username).first()
                if get_username:
                    if check_password_hash(pwhash=get_username.password, password=password):
                        login_user(get_username)
                        return redirect(url_for("dashboard"))
                    else:
                        flash("Mot de passe incorrect")
                        return redirect(url_for("login"))
                else:
                    flash("Pseudonyme incorrect")
                    return redirect(url_for('login'))
            else:
                flash("Veuillez remplir les champs vides")
        return render_template("login.html", is_logged=current_user.is_authenticated)


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

                if form.sex.data == "Masculin":
                    form.sex.data = "Male"
                else:
                    form.sex.data = "Female"

                new_user = User(
                    email=form.email.data,
                    username=form.username.data,
                    password=hash_and_salted_password,
                    sex=form.sex.data
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
    df_exercise_performance = dataframe_manager.create_global_dataframe(table=ExercisePerformance,
                                                                        user_id=current_user.id)
    df_exercise_performance = df_exercise_performance.sort_values(by="Date", ascending=False)[:15]

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


@app.route('/show_workout/<int:user_id>')
@login_required
def show_workout(user_id):
    if user_id != current_user.id:
        abort(404)
    else:
        get_all_exercises = {exercise.id: exercise.exercise_name.title() for exercise in
                             Exercise.query.filter_by(user_id=current_user.id).all()}

        if len(get_all_exercises) == 0:
            has_data = False
        else:
            has_data = True

        return render_template("show_workout.html",
                               is_logged=current_user.is_authenticated,
                               user_id=user_id,
                               all_exercises=get_all_exercises,
                               has_data=has_data,
                               title_content="Ajouter une nouvelle performance")


@app.route('/get_workout_details/<int:user_id>/<int:exercise_id>')
@login_required
def get_workout_details(user_id, exercise_id):

    if user_id != current_user.id:
        abort(404)
    else:
        # poo
        ###
        def get_all_performances_by_id(exercise_id, user_id):
            try:
                all_performances_current_exercise = ExercisePerformance.query.filter_by(
                    exercise_id=exercise_id, user_id=user_id).all()
            except IndexError:
                return False
            else:
                return all_performances_current_exercise
        ####

        get_exercise_name = Exercise.query.filter_by(user_id=current_user.id, id=exercise_id).first().exercise_name

        # Create global performance DF:
        global_df = pd.DataFrame(columns=['Date', 'Performance globale', 'Notes'])
        get_global_performances = []
        performances_data = ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()

        if len(performances_data) == 0:
            global_data = False
        else:
            global_data = True
            for perf in performances_data:
                get_global_performances.append(
                    {
                        'date': perf.date_performance,
                        'performance': perf.global_performance
                    }
                )

            for perf in get_global_performances:
                global_df = global_df.append({'Date': perf['date'],
                                              'Performance globale': perf['performance'],
                                              'Notes': 'notes_desc'},
                                             ignore_index=True)

            global_df = global_df.sort_values(by='Date', ascending=False)

        # Create strength DF:
        strength_df = pd.DataFrame(columns=['Date', '3 répétitions', '2 répétitions', '1 répétition'])

        get_strength_performance = []

        for perf in ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all():
            if perf.three_reps != "" or perf.two_reps != "" or perf.one_reps != "":
                get_strength_performance.append({
                    'date': perf.date_performance,
                    'x3': perf.three_reps if perf.three_reps != "" else "-",
                    'x2': perf.two_reps if perf.two_reps != "" else "-",
                    'x1': perf.one_reps if perf.one_reps != "" else "-",
                })

        if len(get_strength_performance) == 0:
            strength_data = False
            graphJSON_1 = None

        else:
            strength_data = True

            for strength_perf in get_strength_performance:
                strength_df = strength_df.append({'Date': strength_perf['date'],
                                                  '3 répétitions': strength_perf['x3'],
                                                  '2 répétitions': strength_perf['x2'],
                                                  '1 répétition': strength_perf['x1']},
                                                 ignore_index=True)

            strength_df = strength_df.sort_values(by='Date', ascending=False)

            # Generate DF for plotting strength data:
            df_exercise = dataframe_manager.generate_strength_df_for_plot(
                all_performances_current_exercise=get_all_performances_by_id(exercise_id, current_user.id)
            )

            graphJSON_1 = plot_function.line_plot(
                df_exercise,
                x='Date',
                y='Charge',
                text=None,
                xaxis_title='Date',
                yaxis_title='Charge (en Kg)',
                color_column='Répétitions',
                title=f"{Exercise.query.filter_by(id=exercise_id).first().exercise_name.title()} - axé Force"
            )

        # Create endurance DF:
        endurance_df = pd.DataFrame(columns=['Date', '10 répétitions', '15 répétitions', '20 répétitions'])

        get_endurance_performance = []

        for perf in ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all():
            if perf.ten_reps != "" or perf.fifteen_reps != "" or perf.twenty_reps != "":
                get_endurance_performance.append({
                    'date': perf.date_performance,
                    'x10': perf.ten_reps if perf.ten_reps != "" else "-",
                    'x15': perf.fifteen_reps if perf.fifteen_reps != "" else "-",
                    'x20': perf.twenty_reps if perf.twenty_reps != "" else "-",
                })

        if len(get_endurance_performance) == 0:
            endurance_data = False
            graphJSON_2 = None
        else:
            endurance_data = True
            for endurance_perf in get_endurance_performance:
                endurance_df = endurance_df.append({'Date': endurance_perf['date'],
                                                  '10 répétitions': endurance_perf['x10'],
                                                  '15 répétitions': endurance_perf['x15'],
                                                  '20 répétitions': endurance_perf['x20']},
                                                 ignore_index=True)

            endurance_df = endurance_df.sort_values(by='Date', ascending=False)

            # Generate DF for plotting endurance data:
            df_exercise = dataframe_manager.generate_endurance_df_for_plot(
                all_performances_current_exercise=get_all_performances_by_id(exercise_id, current_user.id)
            )

            graphJSON_2 = plot_function.line_plot(
                df_exercise,
                x='Date',
                y='Charge',
                text=None,
                yaxis_title='Charge (en Kg)',
                xaxis_title='Date',
                color_column='Répétitions',
                title=f"{Exercise.query.filter_by(id=exercise_id).first().exercise_name.title()} - axé Endurance"
            )

        return render_template('workout_details.html',
                               is_logged=current_user.is_authenticated,
                               exercise_name=get_exercise_name.title(),
                               exercise_id=exercise_id,
                               global_data=global_data,
                               performance_tables=[global_df.to_html(classes='data', index=False)],
                               strength_data=strength_data,
                               strength_tables = [strength_df.to_html(classes='data', index=False)],
                               endurance_data=endurance_data,
                               endurance_tables=[endurance_df.to_html(classes='data', index=False)],
                               graphJSON_1=graphJSON_1,
                               graphJSON_2=graphJSON_2
                               )


@app.route('/edit_workout/<int:user_id>/<int:exercise_id>', methods=['POST', 'GET'])
@login_required
def edit_workout(user_id, exercise_id):
    exercise = Exercise.query.get(exercise_id)
    form = EditWorkout()
    if form.validate_on_submit():

        def is_rpe_null(data):
            """
            Checking if the RPE is null, in this case RPE column would be empty, otherwise RPE will be
            taken into account
            """
            if data == 0:
                data = ""
                return data
            else:
                return data

        new_performance = ExercisePerformance(
            date_performance=form.date_field.data,
            exercise_performance_user=current_user,
            exercise=exercise,
            global_performance=form.global_performance.data,
            three_reps=form.three_reps.data,
            three_rpe=is_rpe_null(form.three_rpe.data),
            two_reps=form.two_reps.data,
            two_rpe=is_rpe_null(form.two_rpe.data),
            one_reps=form.one_reps.data,
            one_rpe=is_rpe_null(form.one_rpe.data),
            ten_reps=form.ten_reps.data,
            fifteen_reps=form.fifteen_reps.data,
            twenty_reps=form.twenty_reps.data,
        )

        #### Get all performances and organized it

        all_perfs = form.all_data.data.split(',')
        print(f'all_perfs: {all_perfs}')
        organized_perfs = {form.date_field.data: {'charge': [], 'sets': [], 'reps': [], 'rpe': []}}

        for n in range(len(all_perfs)):

            if len(all_perfs[n].split('x')) != 3:
                flash('Les données doivent être sous la forme ChargeXNbSériesXNbRépétitions')
                return redirect(url_for('edit_workout', user_id=current_user.id, exercise_id=exercise_id))

            else:
                organized_perfs[form.date_field.data]['charge'].append(int(all_perfs[n].split('x')[0]))
                organized_perfs[form.date_field.data]['sets'].append(int(all_perfs[n].split('x')[1]))
                organized_perfs[form.date_field.data]['reps'].append(int(all_perfs[n].split('x')[-1].split('@')[0]))

                print(f'split rpe :{all_perfs[n].split("@")}')

                if '@' in all_perfs[n].split("@"):
                    organized_perfs[form.date_field.data]['rpe'].append(int(all_perfs[n].split('@')[-1]))
                else:
                    organized_perfs[form.date_field.data]['rpe'].append(0)

        print(organized_perfs)
        # print(organized_perfs[form.date_field.data]['charge'])

        ####



        db.session.add(new_performance)
        db.session.commit()
        flash("Les nouvelles données ont correctement été ajoutées.")
        return redirect(url_for('dashboard'))

    return render_template("edit_workout.html", is_logged=current_user.is_authenticated, exercise=exercise, form=form,
                           title_content=f"{exercise.exercise_name.title()} : Ajout d'une nouvelle performance")


@app.route('/advanced-edit/<int:user_id>/<int:exercise_id>')
@login_required
def advanced_edit(user_id, exercise_id):
    exercise_df = dataframe_manager.create_specific_dataframe(table=Exercise, exercise_id=exercise_id)
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
                           exercise=dataframe_manager.exercise,
                           tables=[exercise_df.to_html(classes='data', index=True)],
                           has_data=has_data,
                           title_content=f"{dataframe_manager.exercise.exercise_name} : Modification d'une performance")


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


@app.route('/profil/<path:username>')
@login_required
def show_user(username):
    get_user_info = User.query.filter_by(username=username).first()
    print('lol')
    get_user_performance = ExercisePerformance.query.filter_by(user_id=get_user_info.id).all()
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


@app.route('/wilks/<int:user_id>')
@login_required
def wilks(user_id):
    last_bw = user_data.get_last_bw(table=PrDetails, user_id=current_user.id)

    # Get all lifts data:
    get_all_squat_data = PrDetails.query.filter_by(user_id=current_user.id).all()
    get_all_bench_data = PrDetails.query.filter_by(user_id=current_user.id).all()
    get_all_deadlift_data = PrDetails.query.filter_by(user_id=current_user.id).all()

    # Create DF for each lifts:
    squat_df = pr_manager.create_rm_df_by_bw(pr_data=get_all_squat_data, lift_id=1).dropna(axis=0)
    bench_df = pr_manager.create_rm_df_by_bw(pr_data=get_all_bench_data, lift_id=2).dropna(axis=0)
    deadlift_df = pr_manager.create_rm_df_by_bw(pr_data=get_all_deadlift_data, lift_id=3).dropna(axis=0)

    # Create DF with only best values for each BW values:
    all_bw_squat = pr_manager.generate_df_with_highest_pr(squat_df['BW'], exercise_name='Squat', lift_list=squat_df)
    all_bw_bench = pr_manager.generate_df_with_highest_pr(bench_df['BW'], exercise_name='Bench', lift_list=bench_df)
    all_bw_deadlift = pr_manager.generate_df_with_highest_pr(deadlift_df['BW'], exercise_name='Deadlift',
                                                             lift_list=deadlift_df)

    # Join DF:
    join_df = all_bw_squat.join(all_bw_bench.set_index('BW'), on='BW')
    join_df = join_df.join(all_bw_deadlift.set_index('BW'), on='BW')

    # Add 'total' column:
    join_df['Total'] = join_df['Squat'] + join_df['Bench'] + join_df['Deadlift']

    # Calculate and add 'WILKS' column:
    wilks_calculator = WilksCalculator()
    join_df['WILKS'] = wilks_calculator.wilks_calculation(sex=current_user.sex, bw=join_df['BW'], total=join_df['Total'])

    # Drop rows with NaN values:
    join_df = join_df.dropna(axis=0, how='any')

    # Create line plot (WILKS/BW):
    join_df_by_BW = join_df.sort_values(by='BW')
    graphJSON1 = plot_function.line_plot(
        df_exercise=join_df_by_BW,
        x='BW',
        y='WILKS',
        text=None,
        xaxis_title='Poids du corps',
        yaxis_title='Coefficient WILKS',
        color_column=None,
        title="Evolution du Coefficient WILKS en fonction du poids de corps"
    )

    # Create Histogram (BW/PR/LIFT):
    graphJSON2 = plot_function.hist_plot(
        function='sum',
        x_axis=join_df['BW'],
        y_axis=[join_df['Squat'], join_df['Bench'], join_df['Deadlift']],
        label_name=['Squat', 'Bench', 'Deadlift'],
        title="Charges maximales par exercice en fonction du poids de corps",
        xaxis_title='Poids de corps (kg)',
        yaxis_title='Charge (kg)',
    )

    if len(join_df) == 0:
        has_data = False
    else:
        has_data = True

    # Checking if there are new Wilks data to add:
    if join_df.shape[0] > len(Wilks.query.filter_by(user_id=current_user.id).all()):

        if len(Wilks.query.filter_by(user_id=current_user.id).all()) == 0:

            for row in range(join_df.shape[0]):

                # Add data into Wilks table:
                new_wilks = Wilks(
                    date=user_data.get_last_date_last_pr(index=0, table=PrDetails, user_id=current_user.id, df=join_df),
                    bodyweight=join_df.loc[row]['BW'],
                    total=join_df.loc[row]['Total'],
                    wilks_coeff=join_df.loc[row]['WILKS'],
                    wilks_data=current_user
                )
                db.session.add(new_wilks)
                db.session.commit()

        elif join_df.shape[0] == len(Wilks.query.filter_by(user_id=current_user.id).all()) + 1:

            # Add data into Wilks table:
            new_wilks = Wilks(
                date=user_data.get_last_date_last_pr(index=-1, table=PrDetails, user_id=current_user.id, df=join_df),
                bodyweight=join_df['BW'].iloc[-1],
                total=join_df['Total'].iloc[-1],
                wilks_coeff=join_df['WILKS'].iloc[-1],
                wilks_data=current_user
            )
            db.session.add(new_wilks)
            db.session.commit()


    print(join_df)
    # Create Wilks/Date DF:
    wilks_by_date_df = pd.DataFrame(columns=['Date', 'Total', 'WILKS'])

    for wilks in Wilks.query.filter_by(user_id=current_user.id).all():
        wilks_by_date_df = wilks_by_date_df.append({'Date': pandas.to_datetime(wilks.date),
                                                    'WILKS': wilks.wilks_coeff,
                                                    'Total': wilks.total},
                                                   ignore_index=True)

    print(wilks_by_date_df)

    # Create line plot (Wilks/Date):
    graphJSON3 = plot_function.line_plot(
        df_exercise=wilks_by_date_df,
        title="Evolution de vos coefficients WILKS en fonction du temps",
        color_column=None,
        x=wilks_by_date_df['Date'],
        y=wilks_by_date_df['WILKS'],
        text=None,
        xaxis_title='Date',
        yaxis_title='WILKS Coefficient',
    )

    return render_template('wilks.html',
                           is_logged=current_user.is_authenticated,
                           title_content="Détails relatifs à vos coefficients WILKS",
                           performance_tables=[join_df.to_html(classes='data', index=False)],
                           performance_title="Coefficients WILKS en fonction de vos totaux associés "
                                             "à votre poids de corps",
                           graphJSON1=graphJSON1,
                           graphJSON2=graphJSON2,
                           graphJSON3=graphJSON3,
                           has_data=has_data)


@app.route('/track_rm/<int:user_id>')
@login_required
def track_rm(user_id):
    # Get all PRs for each exercise(Squat1, Bench2, Deadlift3):
    all_squat_pr = PrDetails.query.filter_by(user_id=current_user.id, lift_id=1).all()
    all_bench_pr = PrDetails.query.filter_by(user_id=current_user.id, lift_id=2).all()
    all_deadlift_pr = PrDetails.query.filter_by(user_id=current_user.id, lift_id=3).all()

    if len(all_squat_pr) + len(all_bench_pr) + len(all_deadlift_pr) == 0:
        return render_template('rm.html',
                               is_logged=current_user.is_authenticated,
                               has_data=False,
                               title_content="Mettre à ses jours ses records personnels", )
    else:
        # Generate DF for each PR exercise:
        squat_df = pr_manager.create_rm_df(all_squat_pr, 1)
        bench_df = pr_manager.create_rm_df(all_bench_pr, 2)
        deadlift_df = pr_manager.create_rm_df(all_deadlift_pr, 3)

        # Sort values by most recents dates:
        squat_df = squat_df.sort_values(by="Date", ascending=False)
        bench_df = bench_df.sort_values(by="Date", ascending=False)
        deadlift_df = deadlift_df.sort_values(by="Date", ascending=False)

        # Add 'Exercise' column for each DF:
        squat_df['Exercice'] = 'Squat'
        bench_df['Exercice'] = 'Bench'
        deadlift_df['Exercice'] = 'Deadlift'

        # Concat all DF together:
        global_pr_df = pd.concat([squat_df, bench_df, deadlift_df])
        print(global_pr_df)

        # Generate line plot:
        graphJSON = plot_function.line_plot(
            df_exercise=global_pr_df,
            x='Date',
            y='Charge',
            text='BW',
            xaxis_title='Date',
            yaxis_title='Charge (en Kg)',
            color_column='Exercice',
            title="SBD - Evolution de vos charges maximales en fonction du temps"
        )

        # Drop 'Exercice' column of DF:
        squat_df.drop(['Exercice'], axis=1, inplace=True)
        bench_df.drop(['Exercice'], axis=1, inplace=True)
        deadlift_df.drop(['Exercice'], axis=1, inplace=True)

        # Drop 'BW' column of DF:
        if len(squat_df) > 0:
            squat_df.drop(['BW'], axis=1, inplace=True)
        if len(bench_df) > 0:
            bench_df.drop(['BW'], axis=1, inplace=True)
        if len(deadlift_df) > 0:
            deadlift_df.drop(['BW'], axis=1, inplace=True)

        return render_template('rm.html',
                               is_logged=current_user.is_authenticated,
                               title_content="Mettre à ses jours ses records personnels",
                               squat_performance_tables=[squat_df.to_html(classes='data', index=False)],
                               squat_performance_title="Vos derniers RM au Squat :",
                               bench_performance_tables=[bench_df.to_html(classes='data', index=False)],
                               bench_performance_title="Vos derniers RM au Benchpress :",
                               deadlift_performance_tables=[deadlift_df.to_html(classes='data', index=False)],
                               deadlift_performance_title="Vos derniers RM au Deadlift :",
                               graphJSON=graphJSON,
                               )


@app.route('/edit_rm/<int:user_id>/<exercise_name>', methods=['POST', 'GET'])
@login_required
def edit_rm(user_id, exercise_name):
    get_bw_data = PrDetails.query.filter_by(user_id=current_user.id).all()
    has_bw_data = False

    for bw in get_bw_data:
        if bw.bodyweight != None:
            has_bw_data = True
            break

    if not has_bw_data:
        flash("Pour ajouter vos records personnels, vous devez d'abord renseigner votre poids du corps dans vos paramètres.")
        return render_template('edit_rm.html',
                               is_logged=current_user.is_authenticated,
                               has_bw_data=False,
                               title_content=f"Ajout d'un nouveau record personnel pour le {exercise_name}")
    else:
        # Add new PR:
        form = AddPersonalRecord()
        if form.validate_on_submit():
            last_bw = user_data.get_last_bw(table=PrDetails, user_id=current_user.id)

            if exercise_name == "Bench Press":
                new_pr = PrDetails(
                    date=form.date_record.data,
                    lift_id=2,
                    max_bench=form.input_record.data,
                    bodyweight=last_bw,
                    prdetails_user=current_user
                )
            elif exercise_name == "Squat":
                new_pr = PrDetails(
                    date=form.date_record.data,
                    lift_id=1,
                    max_squat=form.input_record.data,
                    bodyweight=last_bw,
                    prdetails_user=current_user
                )
            elif exercise_name == "Deadlift":
                new_pr = PrDetails(
                    date=form.date_record.data,
                    lift_id=3,
                    max_deadlift=form.input_record.data,
                    bodyweight=last_bw,
                    prdetails_user=current_user
                )
            db.session.add(new_pr)
            db.session.commit()
            flash("Le nouveau record a été enregistré avec succès.")
            return redirect(url_for('track_rm', user_id=current_user.id))

        # Edit PR:
        current_lift_id = request.args.get('lift_id')
        get_all_pr = PrDetails.query.filter_by(user_id=current_user.id, lift_id=current_lift_id).all()
        pr_df = pr_manager.create_rm_df(get_all_pr, int(current_lift_id)).sort_values(by='Date', ascending=False)
        pr_df['Delete'] = "Supprimer"

        if len(get_all_pr) == 0:
            has_pr_data = False
        else:
            has_pr_data = True

        return render_template('edit_rm.html',
                               is_logged=current_user.is_authenticated,
                               form=form,
                               has_bw_data=True,
                               has_pr_data=has_pr_data,
                               column_names=pr_df.columns.values,
                               row_data=list(pr_df.values.tolist()),
                               link_delete="Delete",
                               zip=zip,
                               tables=[pr_df.to_html(classes='data', index=True)],
                               exercise_name=exercise_name,
                               last_bw=user_data.get_last_bw(table=PrDetails, user_id=current_user.id),
                               lift_id=int(current_lift_id),
                               title_content=f"Ajout d'un nouveau record personnel pour le {exercise_name}")


@app.route('/delete-pr/<int:user_id>/<int:lift_id>', methods=['POST', 'GET'])
@login_required
def delete_pr(user_id, lift_id):
    pr_date = request.args.get('pr_date')

    # Delete PR according to the date
    pr_to_delete = PrDetails.query.filter_by(user_id=current_user.id, lift_id=lift_id, date=pr_date).first()
    db.session.delete(pr_to_delete)
    db.session.commit()

    return redirect(url_for('track_rm', user_id=user_id))


@app.route('/settings/<int:user_id>', methods=['POST', 'GET'])
@login_required
def settings(user_id):
    if user_data.get_last_bw(table=PrDetails, user_id=current_user.id):
        last_bw = user_data.get_last_bw(table=PrDetails, user_id=current_user.id)
    else:
        last_bw = False
    form = EditBodyWeight()
    if form.validate_on_submit():
        new_bw = PrDetails(
            date=form.date_bw.data,
            bodyweight=form.input_bw.data,
            prdetails_user=current_user
        )
        db.session.add(new_bw)
        db.session.commit()
        flash("Votre nouveau poids de corps a été enregistré.")
        return redirect(url_for('settings', user_id=current_user.id))
    return render_template('settings.html',
                           form=form,
                           last_bw=last_bw,
                           is_logged=current_user.is_authenticated,
                           title_content="Modification de vos paramètres")


if __name__ == "__main__":
    app.run(debug=True)
