#!/usr/bin/env python
from statistics import mean
import pandas as pd
import plotly.express as px
from datetime import timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask import render_template
from werkzeug.datastructures import MultiDict
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_session import flask_scoped_session
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
from SleepConvertor import ConvertSleepData
from form import LoginForm, RegisterForm, AddExercise, EditWorkout, EditWorkoutWithSecondaryExercise, SearchUser, AddPersonalRecord, EditBodyWeight, AddCycle, EndingCycle, AddSecondaryExercise, AddList
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

# CREATE DATE TIME OBJECT
time = datetime.now()

# CREATE SLEEP CONVERTOR OBJECT
sleep_convertor = ConvertSleepData()


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

    # Relation with ExerciseDetails table:
    ex_details = relationship("ExerciseDetails", back_populates="exercise_details_user")

    # Relation with CycleDetails table:
    cycle_details = relationship("CycleDetails", back_populates="cycle_details_user")

    # Relation with SecondaryExercises table:
    secondary_exercises_user = relationship("SecondaryExercises", back_populates="secondary_exercises_user")

    # Relation with SecondaryExercisesPerformance table:
    secondary_exercises_performance_user = relationship("SecondaryExercisesPerformance", back_populates="secondary_exercises_performance_user")

    # Relation with SecondaryExercisesList table:
    secondary_exercises_list_user = relationship("SecondaryExercisesList", back_populates="secondary_exercises_list_user")


class Exercise(db.Model):
    __tablename__ = "exercise_info"
    id = db.Column(db.Integer, primary_key=True)

    # ForeignKey User (primary key of User):
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))

    # Exercise table data:
    exercise_name = db.Column(db.String(30), nullable=False)

    author = relationship("User", back_populates="exercises")
    performance = relationship("ExercisePerformance", back_populates="exercise")

    # Relation with ExerciseDetails table:
    ex_details = relationship("ExerciseDetails", back_populates="exercise_global_data")

    # Relation with CycleDetails table:
    ex_details_for_cycle = relationship("CycleDetails", back_populates="exercise_global_data_for_cycle")

    # Relation with SecondaryExercises table:
    secondary_exercises_global = relationship("SecondaryExercises", back_populates="exercise_global_data")

    # Relation with SecondaryExercisesList table:
    secondary_exercise_list_main_ex_data = relationship("SecondaryExercisesList", back_populates="secondary_exercise_list_main_ex_data")


class CycleDetails(db.Model):
    __tablename__ = "cycle_details"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table:
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    cycle_details_user = relationship("User", back_populates="cycle_details")

    # Relation with Exercise table:
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise_info.id"))
    exercise_global_data_for_cycle = relationship("Exercise", back_populates="ex_details_for_cycle")

    # Relation with Exercise Performance table:
    ex_global_cycle = relationship("ExercisePerformance", back_populates="cycle")

    # Cycle Details Data :
    name = db.Column(db.String(40), nullable=False)
    starting_date = db.Column(db.String(20), nullable=False)
    ending_date = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)


class ExercisePerformance(db.Model):
    __tablename__ = "exercise_global_performance"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table :
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    exercise_performance_user = relationship("User", back_populates="performances")

    # Relation with Exercise table :
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise_info.id"))
    exercise = relationship("Exercise", back_populates="performance")

    # Relation with ExerciseDetails table :
    ex_performance_data = relationship("ExerciseDetails", back_populates="exercise_performance_data")

    # Relation with CycleDetails table :
    cycle_id = db.Column(db.Integer, db.ForeignKey("cycle_details.id"))
    cycle = relationship("CycleDetails", back_populates="ex_global_cycle")

    # Relation with SecondaryExercisesPerformance table :
    secondary_exercises_performance = relationship("SecondaryExercisesPerformance", back_populates="exercise_performance_data_nd_exercises")

    # ExercisePerformance table data:
    date_performance = db.Column(db.String(20), nullable=False)
    global_performance = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.String(250), nullable=True)
    sleep_time = db.Column(db.Integer, nullable=True)


class ExerciseDetails(db.Model):
    __tablename__ = "exercise_details"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table:
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    exercise_details_user = relationship("User", back_populates="ex_details")

    # Relation with Exercise table:
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise_info.id"))
    exercise_global_data = relationship("Exercise", back_populates="ex_details")

    # Relation with ExercisePerformance table:
    performance_id = db.Column(db.Integer, db.ForeignKey("exercise_global_performance.id"))
    exercise_performance_data = relationship("ExercisePerformance", back_populates="ex_performance_data")

    # Exercise Details Data :
    date = db.Column(db.String(20), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    repetitions = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    rpe = db.Column(db.Integer, nullable=True)


class SecondaryExercises(db.Model):
    __tablename__ = "secondary_exercises"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table :
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    secondary_exercises_user = relationship("User", back_populates="secondary_exercises_user")

    # Relation with Exercise table:
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise_info.id"))
    exercise_global_data = relationship("Exercise", back_populates="secondary_exercises_global")

    # Relation with SecondaryExercisesList table:
    list_id = db.Column(db.Integer, db.ForeignKey("secondary_exercises_list.id"))
    secondary_exercises_list_data = relationship("SecondaryExercisesList", back_populates="secondary_exercises_list_data")

    # Relation with SecondaryExercisesPerformance table:
    secondary_exercises_performance_nd_id = relationship("SecondaryExercisesPerformance", back_populates="secondary_exercises_performance_nd_id")

    # Secondary Exercises Data:
    secondary_exercise_name = db.Column(db.String(30), nullable=False)


class SecondaryExercisesPerformance(db.Model):
    __tablename__ = "secondary_exercises_performance"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table:
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    secondary_exercises_performance_user = relationship("User", back_populates="secondary_exercises_performance_user")

    # Relation with ExercisePerformance table:
    performance_id = db.Column(db.Integer, db.ForeignKey("exercise_global_performance.id"))
    exercise_performance_data_nd_exercises = relationship("ExercisePerformance", back_populates="secondary_exercises_performance")

    # Relation with SecondaryExercise table:
    secondary_exercise_id = db.Column(db.Integer, db.ForeignKey("secondary_exercises.id"))
    secondary_exercises_performance_nd_id = relationship("SecondaryExercises", back_populates="secondary_exercises_performance_nd_id")

    # SecondaryExercisesPerformance data:
    global_performance = db.Column(db.String(100), nullable=True)


class SecondaryExercisesList(db.Model):
    __tablename__ = "secondary_exercises_list"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with user table:
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    secondary_exercises_list_user = relationship("User", back_populates="secondary_exercises_list_user")

    # Relation with Exercise table:
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise_info.id"))
    secondary_exercise_list_main_ex_data = relationship("Exercise", back_populates="secondary_exercise_list_main_ex_data")

    # Relation with SecondaryExercises table:
    secondary_exercises_list_data = relationship("SecondaryExercises", back_populates="secondary_exercises_list_data")

    # SecondaryExercisesList data:
    list_name = db.Column(db.String(25), nullable=False)


class PrDetails(db.Model):
    __tablename__ = "pr_details"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # Relation with User table:
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    prdetails_user = relationship("User", back_populates="prs")

    # PR Data:
    date = db.Column(db.String(20), nullable=False)
    lift_id = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Integer, nullable=True)
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
    # Create a global performance DataFrame:
    df_exercise_performance = dataframe_manager.create_dashboard_df(table=ExercisePerformance,
                                                                        user_id=current_user.id)
    df_exercise_performance = df_exercise_performance.sort_values(by="Date", ascending=False)[:15]

    # Generate sleeping dataframe for plotting:
    sleep_df = pd.DataFrame(columns=['Date', 'Sommeil'])

    def conv_time_float(value):
        vals = value.split(':')
        t, hours = divmod(float(vals[0]), 24)
        t, minutes = divmod(float(vals[1]), 60)
        minutes = minutes / 60.0
        return hours + minutes

    all_sleep_data = ExercisePerformance.query.filter_by(user_id=current_user.id).all()
    for sleep in all_sleep_data:
        if sleep.sleep_time is not None:
            formatted_time = str(timedelta(hours=conv_time_float(sleep.sleep_time))).split(':')
            formatted_time = f'{formatted_time[0]}:{formatted_time[1]}'

            sleep_df = sleep_df.append({'Date': sleep.date_performance,
                                        'Sommeil': conv_time_float(sleep.sleep_time),
                                        'Heures': formatted_time},
                                       ignore_index=True)

    if len(sleep_df) != 0:
        sleep_df['Date'] = pd.to_datetime(sleep_df['Date'])
        sleep_df = sleep_df.sort_values(by='Date', ascending=False)

        graphJSON1 = plot_function.area_plot(
            df_exercise=sleep_df,
            x='Date',
            y='Sommeil',
            text='Heures',
            text_color='#ff00e5',
            xaxis_title=None,
            yaxis_title='Heures de sommeil',
            color_column=None,
            line_color='#e600ce',
            y_range=[sleep_df['Sommeil'].min() - 2, sleep_df['Sommeil'].max() + 2],
            line_group=None,
            title="Activité de votre sommeil"
        )
    else:
        graphJSON1 = None

    # Create rate sets per exercises df:
    rate_sets_per_ex_df = pd.DataFrame(columns=['Exercise', 'Number of sets'])

    get_all_exercises_id = [exercise.id for exercise in Exercise.query.filter_by(user_id=current_user.id).all()]

    for id in get_all_exercises_id:
        all_details = ExerciseDetails.query.filter_by(user_id=current_user.id, exercise_id=id).all()

        if len(all_details) != 0:
            get_all_sets_by_ex_id = [perf.sets for perf in all_details if datetime.strptime(perf.date, '%Y-%m-%d').year == time.year and datetime.strptime(perf.date, '%Y-%m-%d').month == time.month]

            rate_sets_per_ex_df = rate_sets_per_ex_df.append({
                'Exercise': all_details[0].exercise_global_data.exercise_name,
                'Number of sets': sum(get_all_sets_by_ex_id)
            }, ignore_index=True)

    if len(rate_sets_per_ex_df) != 0:
        # Plot rate sets per exercises:
        graphJSON2 = plot_function.pie_chart(
            df_data=rate_sets_per_ex_df,
            values='Number of sets',
            names='Exercise',
            color_discrete_sequence=px.colors.sequential.Agsunset,
            title="Taux de séries par exercice durant ce mois",
            legend_pos_y=0.1,
            legend_pos_x=1.75,
            margin_r=300
        )
    else:
        graphJSON2 = None

    # Create average reps per exercise df:
    average_reps_per_ex_df = pd.DataFrame(columns=['Exercise', 'Repetitions'])

    get_all_ex_id = [exercise.id for exercise in Exercise.query.filter_by(user_id=current_user.id).all()]

    for exercise in get_all_ex_id:
        get_all_repetitions = [perf.repetitions for perf in ExerciseDetails.query.filter_by(user_id=current_user.id, exercise_id=exercise).all()]

        if len(get_all_repetitions) != 0:
            average_repetitions = sum(get_all_repetitions)/len(get_all_repetitions)

            average_reps_per_ex_df = average_reps_per_ex_df.append({
                'Exercise': Exercise.query.filter_by(user_id=current_user.id, id=exercise).first().exercise_name,
                'Repetitions': round(average_repetitions, 2)
            }, ignore_index=True)

    if len(average_reps_per_ex_df) != 0:
        # Plot average_reps_per_ex df:
        graphJSON3 = plot_function.separated_hist_chart(
            df=average_reps_per_ex_df,
            title='Nombre moyen de répétitions par exercice',
            color_discrete_sequence=px.colors.sequential.Agsunset,
            legend_title='Exercice'
        )
    else:
        graphJSON3 = None

    # Create total_reps_sets_by_time df:
    total_reps_sets_by_time_df = pd.DataFrame(columns=['Date', 'Exercise', 'Total sets', 'Total repetitions'])

    get_all_exercises_id = [exercise.id for exercise in Exercise.query.filter_by(user_id=current_user.id).all()]

    for id in get_all_exercises_id:
        get_perf_by_dates = [perf.date_performance for perf in ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=id).all()]

        if len(get_perf_by_dates) != 0:

            for perf_by_date in get_perf_by_dates:
                get_detailed_perfs = ExerciseDetails.query.filter_by(user_id=current_user.id, exercise_id=id, date=perf_by_date).all()
                get_total_reps = sum([perf.repetitions for perf in get_detailed_perfs])
                get_total_sets = sum([perf.sets for perf in get_detailed_perfs])

                total_reps_sets_by_time_df = total_reps_sets_by_time_df.append({
                    'Date': perf_by_date,
                    'Exercise': get_detailed_perfs[0].exercise_global_data.exercise_name,
                    'Total sets': float(get_total_sets),
                    'Total repetitions': float(get_total_reps)
                }, ignore_index=True)

    if len(total_reps_sets_by_time_df) != 0:
        # Plot total_reps_sets_by_time_df:
        graphJSON4 = plot_function.bubble_chart(
            data_df=total_reps_sets_by_time_df,
            x='Date',
            y='Total sets',
            size='Total repetitions',
            color='Exercise',
            hover_name='Exercise',
            yaxis_title='Nombre total de séries',
            legend_title='Exercice',
            title='Séries & répétitions en fonction du temps'
        )
    else:
        graphJSON4 = None

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
                           graphJSON1=graphJSON1,
                           graphJSON2=graphJSON2,
                           graphJSON3=graphJSON3,
                           graphJSON4=graphJSON4,
                           title_content=title_content)


@app.route('/add_exercise', methods=['POST', 'GET'])
@login_required
def add_new_exercise():
    form = AddExercise()
    if form.validate_on_submit():
        if Exercise.query.filter_by(user_id=current_user.id, exercise_name=form.exercise_name.data.title()).first():
            flash('Un exercice du même nom existe déjà')
            return redirect(url_for('add_new_exercise'))
        else:
            new_exercise = Exercise(
                exercise_name=form.exercise_name.data.title(),
                author=current_user
            )
            db.session.add(new_exercise)
            db.session.commit()

            flash("L'exercice a été ajouté avec succès")
            return redirect(url_for('show_workout'))

    return render_template("add.html",
                           is_logged=current_user.is_authenticated,
                           form=form,
                           title_content="Commencer à tracker un nouvel exercice")


@app.route('/my_exercises')
@login_required
def show_workout():
    get_all_exercises = {exercise.id: exercise.exercise_name.title() for exercise in
                         Exercise.query.filter_by(user_id=current_user.id).all()}

    if len(get_all_exercises) == 0:
        has_data = False
    else:
        has_data = True

        return render_template("show_workout.html",
                               is_logged=current_user.is_authenticated,
                               all_exercises=get_all_exercises,
                               has_data=has_data,
                               title_content="Ajouter une nouvelle performance")


@app.route('/get_workout_details/<int:user_id>/<int:exercise_id>')
@login_required
def get_workout_details(user_id, exercise_id):
    get_exercise_name = Exercise.query.filter_by(user_id=current_user.id, id=exercise_id).first().exercise_name

    # Create global performance DF:
    performances_data = ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
    global_df = dataframe_manager.create_global_df(all_performances=performances_data)

    if len(performances_data) == 0:
        global_data = False
        strength_data = False
        endurance_data = False
        strength_df = pd.DataFrame()
        endurance_df = pd.DataFrame()
        graphJSON_1 = None
        graphJSON_2 = None
        graphJSON_3 = None
        graphJSON_4 = None

    else:
        global_data = True

        def get_reps_range(np_array):
            new_list = list(np_array)
            return sorted(new_list, reverse=True)

        # Create strength DF:
        strength_df = dataframe_manager.create_specific_df(
            highest_reps=6,
            all_performances=ExerciseDetails.query.filter_by(
                user_id=current_user.id,
                exercise_id=exercise_id).all(),
            reps_range=[1, 2, 3, 4, 5, 6])

        if len(strength_df) == 0:
            strength_data = False
            graphJSON_1 = None
        else:
            strength_data = True

            # Generate DF for plotting:
            df_exercise = dataframe_manager.create_df_for_plot(
                data_df=strength_df,
                reps_range=[1, 2, 3, 4, 5, 6]
            )

            # Plot:
            graphJSON_1 = plot_function.area_plot_with_scale(
                df_exercise,
                reps_range=get_reps_range(df_exercise['Répétitions'].unique()),
                legend_order='reversed',
                x='Date',
                y='Charge',
                xaxis_title=None,
                yaxis_title='Charge (en Kg)',
                color_column='Répétitions',
                color_discrete_sequence=px.colors.sequential.Turbo,
                y_range=None,
                title=f"{Exercise.query.filter_by(id=exercise_id).first().exercise_name.title()} - Evolution de votre chage en fonction du nombre de répétitions"
            )

            # Include RPE in the strength df:
            strength_df = dataframe_manager.add_rpe_to_df(df=strength_df,
                                                          all_performances=ExerciseDetails.query.filter_by(
                                                              user_id=current_user.id,
                                                              exercise_id=exercise_id).all(),
                                                          reps_range=[1, 2, 3, 4, 5, 6])

        # Create endurance DF:
        endurance_df = dataframe_manager.create_specific_df(
            highest_reps=25,
            all_performances=ExerciseDetails.query.filter_by(
                user_id=current_user.id,
                exercise_id=exercise_id).all(),
            reps_range=[10, 15, 20, 25])

        if len(endurance_df) == 0:
            endurance_data = False
            graphJSON_2 = None
        else:
            endurance_data = True
            # Generate DF for plotting:
            df_exercise = dataframe_manager.create_df_for_plot(
                data_df=endurance_df,
                reps_range=[10, 15, 20, 25]
            )

            # Plot:
            graphJSON_2 = plot_function.area_plot_with_scale(
                df_exercise,
                reps_range=get_reps_range(df_exercise['Répétitions'].unique()),
                legend_order='reversed',
                x='Date',
                y='Charge',
                xaxis_title=None,
                yaxis_title='Charge (en Kg)',
                color_column='Répétitions',
                y_range=None,
                color_discrete_sequence=px.colors.sequential.Plasma,
                title=f"{Exercise.query.filter_by(id=exercise_id).first().exercise_name.title()} - Evolution de votre chage en fonction du nombre de répétitions"
            )

            # Include RPE in the endurance df:
            endurance_df = dataframe_manager.add_rpe_to_df(df=endurance_df,
                                                           all_performances=ExerciseDetails.query.filter_by(
                                                               user_id=current_user.id,
                                                               exercise_id=exercise_id).all(),
                                                           reps_range=[10, 15, 20, 25])

        # Create total repetitions DF:
        total_reps_df = pd.DataFrame(columns=['Date', 'Total Répétitions'])
        get_all_dates = set([perf.date_performance for perf in ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()])

        for date in get_all_dates:
            current_perf_total_repetitions = 0
            get_all_perfs = ExerciseDetails.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, date=date).all()

            for perf in get_all_perfs:
                current_perf_total_repetitions += perf.repetitions

            total_reps_df = total_reps_df.append({
                'Date': date,
                'Total Répétitions': current_perf_total_repetitions
            }, ignore_index=True)

        # Plot total repetitions DF:
        graphJSON_3 = plot_function.area_plot(
            df_exercise=total_reps_df,
            x='Date',
            y='Total Répétitions',
            text=None,
            text_color=None,
            xaxis_title=None,
            yaxis_title='Nombre total de répétitions',
            color_column=None,
            line_color='#FF6363',
            y_range=None,
            line_group=None,
            title="Nombre total de répétitions par séance sur cet exercice"
        )

        # Create rate_strength_endurance DF:
        get_all_perfs = ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
        current_date = datetime.now()
        strength_set = 0
        endurance_set = 0

        # Get all performances for the current month
        for perf in get_all_perfs:
            str_to_date = datetime.strptime(perf.date_performance, '%Y-%m-%d')

            if str_to_date.year == current_date.year:
                if str_to_date.month == current_date.month:
                    get_detailed_perfs = ExerciseDetails.query.filter_by(user_id=current_user.id,
                                                                         exercise_id=exercise_id,
                                                                         performance_id=perf.id).all()

                    for detailed_perf in get_detailed_perfs:
                        if detailed_perf.repetitions <= 6:
                            strength_set = strength_set + detailed_perf.sets
                        elif detailed_perf.repetitions > 6:
                            endurance_set = endurance_set + detailed_perf.sets

        rate_strength_endurance_df = pd.DataFrame(columns=['Catégorie', 'Répétitions'])
        all_sets = [{'Force': strength_set}, {'Endurance': endurance_set}]

        for set_type in all_sets:
            for category in set_type:
                rate_strength_endurance_df = rate_strength_endurance_df.append({
                    'Catégorie': category,
                    'Répétitions': set_type[category]
                }, ignore_index=True)

        # Plot rate_strength_endurance_df:
        graphJSON_4 = plot_function.pie_chart(
            df_data=rate_strength_endurance_df,
            values='Répétitions',
            names='Catégorie',
            color_discrete_sequence=['#9B3192', '#EA5F89'],
            title="Taux de séries de force Vs. taux de séries d'hypertrophie durant ce mois"
        )

    # Get all cycles data:
    get_all_cycles = CycleDetails.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()

    if len(get_all_cycles) != 0:
        has_cycle_data = True
    else:
        has_cycle_data = False

    return render_template('workout_details.html',
                           is_logged=current_user.is_authenticated,
                           title_content="Résumé de vos exercices",
                           exercise_name=get_exercise_name.title(),
                           exercise_id=exercise_id,
                           global_data=global_data,
                           performance_tables=[global_df.to_html(classes='data', index=False)],
                           strength_data=strength_data,
                           strength_tables=[strength_df.to_html(classes='data', index=False)],
                           endurance_data=endurance_data,
                           endurance_tables=[endurance_df.to_html(classes='data', index=False)],
                           graphJSON_1=graphJSON_1,
                           graphJSON_2=graphJSON_2,
                           graphJSON_3=graphJSON_3,
                           graphJSON_4=graphJSON_4,
                           has_cycle_data=has_cycle_data,
                           all_cycles=get_all_cycles
                           )


@app.route('/edit_workout/<int:user_id>/<int:exercise_id>', methods=['POST', 'GET'])
@login_required
def edit_workout(user_id, exercise_id):
    exercise = Exercise.query.get(exercise_id)
    get_secondary_exercise_data = SecondaryExercises.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()

    if get_secondary_exercise_data:
        form = EditWorkoutWithSecondaryExercise()
        form.secondary_exercise_list.choices = [(g.id, g.list_name) for g in SecondaryExercisesList.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).order_by('list_name')]
    else:
        form = EditWorkout()

    if form.validate_on_submit():

        # Get all performances and organized it
        all_perfs = form.all_data.data.split(',')
        organized_perfs = {form.date_field.data: {'charge': [], 'sets': [], 'reps': [], 'rpe': []}}

        # Checking format of data, rpe and sleep time:
        if not user_data.check_format_of_data(all_perfs=all_perfs):
            flash('Les données doivent être sous la forme ChargeXNbSériesXNbRépétitions')
            return redirect(url_for('edit_workout', user_id=current_user.id, exercise_id=exercise_id))

        if not user_data.check_format_of_rpe(all_perfs=all_perfs):
            flash('Le RPE doit être compris entre 1 et 10')
            return redirect(url_for('edit_workout', user_id=current_user.id, exercise_id=exercise.id))

        if len(form.sleep_time.data) > 0:
            if not user_data.check_format_of_sleep_time(sleep_time_data=form.sleep_time.data):
                flash('Le sommeil doit être sous la forme HH:MM, par exemple 08:30')
                return redirect(url_for('edit_workout', user_id=current_user.id, exercise_id=exercise_id))
            else:
                current_sleep = user_data.check_format_of_sleep_time(sleep_time_data=form.sleep_time.data)
        else:
            current_sleep = None

        for n in range(len(all_perfs)):
            split_perf = all_perfs[n].split('x')
            if len(split_perf) == 2:
                nb_of_sets = 1
                nb_of_repetitions = split_perf[1] if '@' not in split_perf[1] else split_perf[1].split('@')[0]
                rpe_value = None if not '@' in split_perf[1] else split_perf[1].split('@')[1]
            else:
                print(f'split perf is: {split_perf}')
                nb_of_sets = split_perf[1]
                nb_of_repetitions = split_perf[2] if not '@' in split_perf[2] else split_perf[2].split('@')[0]
                rpe_value = None if not '@' in split_perf[2] else split_perf[2].split('@')[1]

            organized_perfs[form.date_field.data]['charge'].append(float(split_perf[0]))
            organized_perfs[form.date_field.data]['sets'].append(int(nb_of_sets))
            organized_perfs[form.date_field.data]['reps'].append(int(nb_of_repetitions))

            if '@' in all_perfs[n]:
                organized_perfs[form.date_field.data]['rpe'].append(float(rpe_value))
            else:
                organized_perfs[form.date_field.data]['rpe'].append(rpe_value)

        # Add performances to database (global performance):

        # Checking if there is an active cycle:
        has_active_cycle = CycleDetails.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, is_active=True).first()
        if has_active_cycle:
            cycle_id = has_active_cycle.id
        else:
            cycle_id = None

        if cycle_id is not None:
            new_global_performance = ExercisePerformance(
                date_performance=form.date_field.data,
                exercise_performance_user=current_user,
                exercise=exercise,
                global_performance=form.all_data.data,
                notes=form.notes.data if len(form.notes.data) > 0 else None,
                sleep_time=current_sleep,
                cycle=CycleDetails.query.get(cycle_id)
            )

            db.session.add(new_global_performance)
            db.session.commit()

        else:
            new_global_performance = ExercisePerformance(
                date_performance=form.date_field.data,
                exercise_performance_user=current_user,
                exercise=exercise,
                global_performance=form.all_data.data,
                notes=form.notes.data if len(form.notes.data) > 0 else None,
                sleep_time=current_sleep
            )

            db.session.add(new_global_performance)
            db.session.commit()

        # Get the last performance object corresponding to the performance_id
        performance = ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).order_by(ExercisePerformance.id.desc()).first()

        # Detailed performance:
        for n in range(len(organized_perfs[form.date_field.data]['charge'])):

            new_performance = ExerciseDetails(
                exercise_details_user=current_user,
                exercise_global_data=Exercise.query.get(exercise_id),
                exercise_performance_data=performance,
                date=form.date_field.data,
                weight=organized_perfs[form.date_field.data]['charge'][n],
                repetitions=organized_perfs[form.date_field.data]['reps'][n],
                sets=organized_perfs[form.date_field.data]['sets'][n],
                rpe=organized_perfs[form.date_field.data]['rpe'][n],
            )

            db.session.add(new_performance)
            db.session.commit()

        # Check if there is secondary exercises data:
        if get_secondary_exercise_data:
            return redirect(url_for('add_secondary_exercises_performance', user_id=current_user.id, exercise_id=exercise_id, performance_id=performance.id, list_id=form.secondary_exercise_list.data))
        else:
            flash("Les nouvelles données ont correctement été ajoutées.")
            return redirect(url_for('get_workout_details', user_id=current_user.id, exercise_id=exercise_id))

    return render_template("edit_workout.html", is_logged=current_user.is_authenticated, exercise=exercise, form=form,
                           title_content=f"{exercise.exercise_name.title()} : Ajout d'une nouvelle performance")


@app.route('/add_secondary_performance/<int:user_id>/<int:list_id>/<int:exercise_id>/<int:performance_id>', methods=['POST', 'GET'])
@login_required
def add_secondary_exercises_performance(user_id, list_id, exercise_id, performance_id):
    get_nd_exercises_data = SecondaryExercises.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, list_id=list_id).all()

    if request.method == 'POST':
        data_correctly_formatted = True

        for nd_exercise in get_nd_exercises_data:
            if " " in nd_exercise.secondary_exercise_name:
                current_exercise = nd_exercise.secondary_exercise_name.replace(" ", "-")
            else:
                current_exercise = nd_exercise.secondary_exercise_name

            if len(request.form[current_exercise]) > 0:
                all_perfs = request.form[current_exercise].split(',')

                for n in range(len(all_perfs)):
                    if len(all_perfs[n].split('x')) != 3:
                        data_correctly_formatted = False
                        break

        if not data_correctly_formatted:
            flash('Les données doivent être sous la forme ChargeXNbSériesXNbRépétitions')
            return redirect(url_for('add_secondary_exercises_performance', user_id=current_user.id, exercise_id=exercise_id, performance_id=performance_id))
        else:
            for nd_exercise in get_nd_exercises_data:
                if " " in nd_exercise.secondary_exercise_name:
                    current_exercise = nd_exercise.secondary_exercise_name.replace(" ", "-")
                else:
                    current_exercise = nd_exercise.secondary_exercise_name

                print(f'performance id is {performance_id}')
                print(f'performance object is {ExercisePerformance.query.get(performance_id)}')

                new_secondary_exercise_perf = SecondaryExercisesPerformance(
                    secondary_exercises_performance_user=User.query.get(current_user.id),
                    exercise_performance_data_nd_exercises=ExercisePerformance.query.get(performance_id),
                    secondary_exercises_performance_nd_id=SecondaryExercises.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, secondary_exercise_name=nd_exercise.secondary_exercise_name).first(),
                    global_performance=request.form[current_exercise] if len(request.form[current_exercise]) > 0 else None,
                )

                db.session.add(new_secondary_exercise_perf)
                db.session.commit()

            flash('Les données ont correctement été ajoutées')
            return redirect(url_for('get_workout_details', user_id=current_user.id, exercise_id=exercise_id))

    return render_template('add_secondary_exercises_performance.html',
                           is_logged=current_user.is_authenticated,
                           secondary_exercises_data=get_nd_exercises_data,
                           performance_id=performance_id,
                           exercise_id=exercise_id,
                           list_id=list_id,
                           title_content='Ajout de données pour vos exercices secondaires')


@app.route('/advanced_edit/<int:user_id>/<int:exercise_id>')
@login_required
def advanced_edit(user_id, exercise_id):
    all_global_performances = ExercisePerformance.query.filter_by(user_id=current_user.id,
                                                                  exercise_id=exercise_id)

    df_exercise = dataframe_manager.create_df_for_edit(all_global_performances=all_global_performances)
    exercise_title = Exercise.query.filter_by(user_id=current_user.id, id=exercise_id).first().exercise_name

    if len(df_exercise) == 0:
        has_data = False
    else:
        has_data = True

    return render_template("advanced_edit.html",
                           is_logged=current_user.is_authenticated,
                           column_names=df_exercise.columns.values,
                           row_data=list(df_exercise.values.tolist()),
                           link_delete="Delete",
                           link_edit="Editer",
                           link_performance_id="Performance_id",
                           zip=zip,
                           tables=[df_exercise.to_html(classes='data', index=True)],
                           has_data=has_data,
                           title_content=f"{exercise_title} : Modification d'une performance")


@app.route('/delete_performance/<int:performance_id>', methods=['POST', 'GET'])
@login_required
def delete_performance(performance_id):
    if request.method == 'POST':
        # Delete detailed performances:
        all_detailed_performances = ExerciseDetails.query.filter_by(performance_id=performance_id).all()
        for detailed_perf in all_detailed_performances:
            db.session.delete(detailed_perf)
        db.session.commit()

        # Delete secondary exercises performances linked to current global performance:
        get_secondary_exercises_performances = SecondaryExercisesPerformance.query.filter_by(user_id=current_user.id, performance_id=performance_id).all()
        if get_secondary_exercises_performances:
            for secondary_perf in get_secondary_exercises_performances:
                db.session.delete(secondary_perf)
            db.session.commit()

        # Delete global performance:
        global_performance_to_delete = ExercisePerformance.query.filter_by(id=performance_id).first()
        get_exercise_id = global_performance_to_delete.exercise.id
        db.session.delete(global_performance_to_delete)
        db.session.commit()
        flash('Les données ont correctement été supprimées.')

        return redirect(url_for('advanced_edit', exercise_id=get_exercise_id, user_id=current_user.id))

    return redirect(url_for('dashboard'))


@app.route('/edit_performance/<int:performance_id>', methods=['POST', 'GET'])
@login_required
def edit_performance(performance_id):
    get_performance_data = ExercisePerformance.query.filter_by(id=performance_id).first()
    form = EditWorkout()

    if request.method == 'GET':
        form = EditWorkout(formdata=MultiDict(
            {
                'all_data': get_performance_data.global_performance,
                'notes': get_performance_data.notes if get_performance_data.notes is not None else '-',
                'sleep_time': get_performance_data.sleep_time if get_performance_data.sleep_time is not None else '-'
            }
        ))
        form.date_field.data = datetime.strptime(get_performance_data.date_performance, '%Y-%m-%d')

    if form.validate_on_submit():

        # Checking format of data, rpe and sleep time:
        all_perfs = form.all_data.data.split(',')

        if not user_data.check_format_of_data(all_perfs=all_perfs):
            flash('Les données doivent être sous la forme ChargeXNbSériesXNbRépétitions')
            return redirect(url_for('edit_performance', performance_id=performance_id))

        if not user_data.check_format_of_rpe(all_perfs=all_perfs):
            flash('Le RPE doit être compris entre 1 et 10')
            return redirect(url_for('edit_performance', performance_id=performance_id))

        if len(form.sleep_time.data) > 0 and '-' not in form.sleep_time.data:
            if not user_data.check_format_of_sleep_time(sleep_time_data=form.sleep_time.data):
                flash('Le sommeil doit être sous la forme HH:MM, par exemple 08:30')
                return redirect(url_for('edit_performance', performance_id=performance_id))
            else:
                new_sleep_time = user_data.check_format_of_sleep_time(sleep_time_data=form.sleep_time.data)
        else:
            new_sleep_time = None

        # Update global performance:
        performance_to_update = ExercisePerformance.query.get(performance_id)
        performance_to_update.date_performance = form.date_field.data
        performance_to_update.global_performance = form.all_data.data
        performance_to_update.notes = form.notes.data if len(form.notes.data) > 1 else None
        performance_to_update.sleep_time = new_sleep_time if new_sleep_time != '-' else None
        db.session.commit()

        # Update detailed performances:
        all_detailed_perf = ExerciseDetails.query.filter_by(user_id=current_user.id,
                                                            performance_id=performance_id).all()
        for perf in all_detailed_perf:
            db.session.delete(perf)
        db.session.commit()

        all_new_perf = ExercisePerformance.query.filter_by(id=performance_id, user_id=current_user.id).first()

        performance = ExercisePerformance.query.filter_by(user_id=current_user.id,
                                                          date_performance=all_new_perf.date_performance,
                                                          global_performance=all_new_perf.global_performance).first()

        for global_perf in all_new_perf.global_performance.split(','):
            split_global_perf = global_perf.split('x')

            if len(split_global_perf) == 2:
                nb_of_sets = 1
                nb_of_repetitions = split_global_perf[1] if '@' not in split_global_perf[1] else split_global_perf[1].split('@')[0]
                rpe_value = None if not '@' in split_global_perf[1] else split_global_perf[1].split('@')[1]
            else:
                nb_of_sets = global_perf.split('x')[1]
                nb_of_repetitions = split_global_perf [2] if not '@' in split_global_perf[2] else split_global_perf[2].split('@')[0]
                rpe_value = None if not '@' in split_global_perf[2] else split_global_perf[2].split('@')[1]

            new_performance = ExerciseDetails(
                exercise_details_user=current_user,
                exercise_global_data=Exercise.query.get(all_new_perf.exercise_id),
                exercise_performance_data=performance,
                date=all_new_perf.date_performance,
                weight=global_perf.split('x')[0],
                repetitions=nb_of_repetitions,
                sets=nb_of_sets,
                rpe=rpe_value,
            )

            db.session.add(new_performance)
            db.session.commit()

        flash('Les données ont correctement été modifiées')
        return redirect(url_for('advanced_edit', user_id=current_user.id, exercise_id=performance.exercise_id))

    return render_template("change_performance.html",
                           is_logged=current_user.is_authenticated,
                           form=form,
                           performance_data=get_performance_data,
                           title_content=f"Performance id{get_performance_data.id} : Modification")


@app.route('/delete_workout/<int:user_id>/<int:exercise_id>')
@login_required
def delete_workout(user_id, exercise_id):
    # Delete all performances for the exercise:
    performance_to_delete = ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
    for performance in performance_to_delete:
        db.session.delete(performance)
        db.session.commit()

    # Delete detailed performances for the exercise:
    detailed_performances_to_delete = ExerciseDetails.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
    for performance in detailed_performances_to_delete:
        db.session.delete(performance)
        db.session.commit()

    get_secondary_exercises_id = [nd_exercise.id for nd_exercise in SecondaryExercises.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()]

    # Delete secondary exercises attached:
    secondary_exercises_to_delete = SecondaryExercises.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
    for secondary_exercise in secondary_exercises_to_delete:
        db.session.delete(secondary_exercise)
        db.session.commit()

    # Delete secondary exercises list:
    secondary_exercises_list_to_delete = SecondaryExercisesList.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
    for secondary_exercise_list in secondary_exercises_list_to_delete:
        db.session.delete(secondary_exercise_list)
        db.session.commit()

    # Delete secondary exercises performances:
    for id in get_secondary_exercises_id:
        get_secondary_exercises_perf_by_id = SecondaryExercisesPerformance.query.filter_by(user_id=current_user.id, secondary_exercise_id=id).all()
        for secondary_ex_perf in get_secondary_exercises_perf_by_id:
            db.session.delete(secondary_ex_perf)
            db.session.commit()

    # Delete cycles of exercise:
    get_cycles_details_of_exercise = CycleDetails.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
    for cycle in get_cycles_details_of_exercise:
        db.session.delete(cycle)
        db.session.commit()

    # Finally, delete the exercise:
    exercise_to_delete = Exercise.query.filter_by(user_id=current_user.id, id=exercise_id).first()
    db.session.delete(exercise_to_delete)
    db.session.commit()

    flash("L'exercice a correctement été supprimé.")
    return redirect(url_for('dashboard'))


@app.route('/add_cycle/<int:user_id>/<int:exercise_id>', methods=['POST', 'GET'])
@login_required
def add_cycle(user_id, exercise_id):
    get_exercise_name = Exercise.query.filter_by(user_id=current_user.id, id=exercise_id).first().exercise_name
    form = AddCycle()

    if form.validate_on_submit():

        if not CycleDetails.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, is_active=True).all():

            new_cycle = CycleDetails(
                cycle_details_user=current_user,
                exercise_global_data_for_cycle=Exercise.query.get(exercise_id),
                name=form.cycle_name.data,
                starting_date=form.starting_date.data,
                ending_date=form.ending_date.data if form.ending_date.data is not None else 'Undetermined',
                is_active=True
            )

            db.session.add(new_cycle)
            db.session.commit()

            flash('Le nouveau cycle a été ajouté avec succès')

            return redirect(url_for('get_workout_details', user_id=current_user.id, exercise_id=exercise_id))
        else:
            flash('Veuillez terminer le cycle actif pour en ajouter un nouveau')
            return redirect(url_for('add_cycle', user_id=current_user.id, exercise_id=exercise_id))

    return render_template('add_cycle.html',
                           form=form,
                           title_content=f"{get_exercise_name} : Ajout d'un nouveau cycle",
                           exercise_id=exercise_id,
                           is_logged=current_user.is_authenticated)


@app.route('/get_cycle_details/<int:user_id>/<int:cycle_id>', methods=['POST', 'GET'])
@login_required
def get_cycle_details(user_id, cycle_id):
    get_cycle_details = CycleDetails.query.filter_by(user_id=current_user.id, id=cycle_id).first()
    get_global_performance_data = ExercisePerformance.query.filter_by(user_id=current_user.id,
                                                                      exercise_id=get_cycle_details.exercise_id,
                                                                      cycle_id=cycle_id).all()

    print(get_global_performance_data)
    if len(get_global_performance_data) > 0:
        # Average sleep during the cycle:
        sleep_data = []
        for perf in get_global_performance_data:
            if perf.sleep_time is not None:
                sleep_data.append(sleep_convertor.conv_time_float(value=perf.sleep_time))

        if len(sleep_data) > 0:
            average_sleep = mean(sleep_data)
            formatted_average_sleep = sleep_convertor.float_to_time(
                hours=int(str(average_sleep).split('.')[0]),
                decimal=int(str(average_sleep).split('.')[1])
            ).split('.')[0]
        else:
            formatted_average_sleep = '-'

        # Average RPE & working weight during the cycle:
        get_all_perf_id_of_cycle = [perf.id for perf in ExercisePerformance.query.filter_by(user_id=current_user.id, exercise_id=get_cycle_details.exercise_id, cycle_id=cycle_id).all()]
        all_rpe = []
        all_weight = []

        for performance_id in get_all_perf_id_of_cycle:
            get_rpe = [perf_details.rpe for perf_details in ExerciseDetails.query.filter_by(user_id=current_user.id, exercise_id=get_cycle_details.exercise_id, performance_id=performance_id).all() if perf_details.rpe is not None]
            get_weight = [perf_details.weight if perf_details.sets == 1 else perf_details.weight * perf_details.sets for perf_details in ExerciseDetails.query.filter_by(user_id=current_user.id, exercise_id=get_cycle_details.exercise_id, performance_id=performance_id).all()]

            if len(get_rpe) > 0:
                for rpe in get_rpe:
                    all_rpe.append(rpe)

            if len(get_weight) > 0:
                for weight in get_weight:
                    all_weight.append(weight)

        if len(all_rpe) > 0:
            average_rpe = mean(all_rpe)
        else:
            average_rpe = '-'
        if len(all_weight) > 0:
            average_weight = round(mean(all_weight), 1)
        else:
            average_weight = '-'

    else:
        formatted_average_sleep = '-'
        average_rpe = '-'
        average_weight = '-'

    # Enable ending cycle if it's active:
    if get_cycle_details.is_active is True:
        form = EndingCycle()
        if form.validate_on_submit():
            get_cycle_details.is_active = False
            get_cycle_details.ending_date = time.now().strftime('%Y-%m-%d')
            db.session.commit()
            flash('Vous avez mis fin à votre cycle')
            return redirect(url_for('get_workout_details', user_id=current_user.id,
                                    exercise_id=get_cycle_details.exercise_id))
    else:
        form = None

    return render_template('get_cycle_details.html',
                           title_content=f"Résumé de votre cycle : {get_cycle_details.name}",
                           is_logged=current_user.is_authenticated,
                           cycle=get_cycle_details,
                           has_active_cycle=get_cycle_details.is_active,
                           form=form,
                           average_sleep=formatted_average_sleep,
                           average_rpe=average_rpe,
                           average_weight=average_weight)


@app.route('/secondary_exercises/<int:user_id>/<int:exercise_id>', methods=['POST', 'GET'])
@login_required
def secondary_exercises(user_id, exercise_id):
    get_main_exercise = Exercise.query.get(exercise_id)

    if SecondaryExercisesList.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).first():
        has_list_data = True
        user = User.query.get(current_user.id)
        form = AddSecondaryExercise(obj=user)
        form.list_data.choices = [(g.id, g.list_name) for g in SecondaryExercisesList.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).order_by('list_name')]

        if form.validate_on_submit():

            if SecondaryExercises.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, list_id=form.list_data.data, secondary_exercise_name=form.secondary_exercise_name.data.title()).first():
                flash("Vous avez déjà ajouté un exercice du même nom")
                return redirect(url_for('secondary_exercises', user_id=current_user.id, exercise_id=exercise_id))
            else:
                new_secondary_exercise = SecondaryExercises(
                    secondary_exercises_user=current_user,
                    exercise_global_data=get_main_exercise,
                    secondary_exercises_list_data=SecondaryExercisesList.query.get(form.list_data.data),
                    secondary_exercise_name=form.secondary_exercise_name.data.title(),
                )

                db.session.add(new_secondary_exercise)
                db.session.commit()
                flash("L'exercice secondaire a été ajouté avec succès")
            return redirect(url_for('secondary_exercises', user_id=current_user.id, exercise_id=exercise_id))

        # Resume performance of secondary exercise:
        get_secondary_exercises_list_data = SecondaryExercisesList.query.filter_by(user_id=current_user.id, exercise_id=exercise_id).all()
    else:
        has_list_data = False
        form = None
        get_secondary_exercises_list_data = None

    return render_template('secondary_exercises_details.html',
                           title_content=f"{get_main_exercise.exercise_name} : Exercices secondaires ",
                           is_logged=current_user.is_authenticated,
                           form=form,
                           has_list_data=has_list_data,
                           all_secondary_exercises_list=get_secondary_exercises_list_data,
                           exercise_id=exercise_id)


@app.route('/add_list/<int:user_id>/<int:exercise_id>', methods=['POST', 'GET'])
@login_required
def add_list_for_secondary_exercises(user_id, exercise_id):
    get_main_exercise = Exercise.query.filter_by(user_id=current_user.id, id=exercise_id).first()
    form = AddList()

    if form.validate_on_submit():

        if not SecondaryExercisesList.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, list_name=form.list_name.data).first():
            new_list = SecondaryExercisesList(
                secondary_exercises_list_user=User.query.get(current_user.id),
                secondary_exercise_list_main_ex_data=Exercise.query.get(exercise_id),
                list_name=str(form.list_name.data),

            )
            db.session.add(new_list)
            db.session.commit()

            flash('La nouvelle liste a correctement été ajoutée')
            return redirect(url_for('secondary_exercises', user_id=current_user.id, exercise_id=get_main_exercise.id))
        else:
            flash('Vous avez déjà ajouté une liste du même nom')
            return redirect(url_for('add_list_for_secondary_exercises', user_id=current_user.id, exercise_id=get_main_exercise.id))

    return render_template('add_list.html',
                           title_content=f"{get_main_exercise.exercise_name} : Création d'une liste pour exercices secondaires ",
                           is_logged=current_user.is_authenticated,
                           form=form)


@app.route('/secondary_exercises_resume/<int:user_id>/<int:list_id>')
@login_required
def secondary_exercises_list_resume(user_id, list_id):
    get_current_list_data = SecondaryExercisesList.query.filter_by(user_id=current_user.id, id=list_id).first()

    list_df = pd.DataFrame(columns=['Performance_id', 'Date'])

    current_secondary_exercises_data = SecondaryExercises.query.filter_by(user_id=current_user.id, list_id=list_id, exercise_id=get_current_list_data.exercise_id).all()

    get_nd_exercises_name = [exercise.secondary_exercise_name for exercise in current_secondary_exercises_data]
    get_nd_exercises_id = [exercise.id for exercise in current_secondary_exercises_data]

    if len(get_nd_exercises_id) != 0:
        for exercise_name in get_nd_exercises_name:
            list_df[exercise_name] = ''

        get_perf_id = set([exercise.performance_id for exercise in
                           SecondaryExercisesPerformance.query.filter_by(user_id=current_user.id).all() if
                           exercise.secondary_exercise_id in get_nd_exercises_id])

        if len(get_perf_id) != 0:

            for perf_id in get_perf_id:

                get_date_of_current_perf = SecondaryExercisesPerformance.query.filter_by(user_id=current_user.id, performance_id=perf_id).first().exercise_performance_data_nd_exercises.date_performance

                if get_date_of_current_perf not in list_df.values:

                    list_df = list_df.append({
                        'Performance_id': perf_id,
                        'Date': get_date_of_current_perf
                    }, ignore_index=True)

                    for nd_exercise_id in get_nd_exercises_id:

                        get_current_perf_data = SecondaryExercisesPerformance.query.filter_by(user_id=current_user.id,
                                                                                              secondary_exercise_id=nd_exercise_id,
                                                                                              performance_id=perf_id).first()

                        if get_current_perf_data is not None:
                            list_df.loc[list_df['Date'] == get_date_of_current_perf, get_current_perf_data.secondary_exercises_performance_nd_id.secondary_exercise_name] = get_current_perf_data.global_performance if get_current_perf_data.global_performance is not None else "-"
                        else:
                            list_df.loc[list_df['Date'] == get_date_of_current_perf, SecondaryExercises.query.filter_by(user_id=current_user.id, id=nd_exercise_id).first().secondary_exercise_name] = "-"

    if len(list_df) == 0:
        has_secondary_exercises_performances_data = False
    else:
        has_secondary_exercises_performances_data = True
        list_df['Delete'] = "Supprimer"

    return render_template('secondary_exercises_list_resume.html',
                           is_logged=current_user.is_authenticated,
                           title_content=f"Vos exercices secondaires associés à la liste : {get_current_list_data.list_name}",
                           column_names=list_df.columns.values,
                           row_data=list(list_df.values.tolist()),
                           link_performance_id="Performance_id",
                           link_delete="Delete",
                           zip=zip,
                           list_data=get_current_list_data,
                           has_data=has_secondary_exercises_performances_data,
                           secondary_exercises_table=[list_df.to_html(classes='data', index=False)])


@app.route('/delete_secondary_performance/<int:user_id>/<int:performance_id>', methods=['POST'])
@login_required
def delete_secondary_performance(user_id, performance_id):
    if request.method == 'POST':
        # Delete secondary exercises performances linked to current global performance:
        get_secondary_exercises_performances = SecondaryExercisesPerformance.query.filter_by(user_id=current_user.id,
                                                                                             performance_id=performance_id).all()
        if get_secondary_exercises_performances:
            get_current_list_id = SecondaryExercisesPerformance.query.filter_by(user_id=current_user.id, performance_id=performance_id).first().secondary_exercises_performance_nd_id.list_id

            for secondary_perf in get_secondary_exercises_performances:
                db.session.delete(secondary_perf)
            db.session.commit()

            flash('Les données ont correctement été supprimées')
            return redirect(url_for('secondary_exercises_list_resume', user_id=current_user.id, list_id=get_current_list_id))

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


@app.route('/profile/<path:username>')
@login_required
def show_user(username):
    get_user_info = User.query.filter_by(username=username).first()
    get_user_performance = ExercisePerformance.query.filter_by(user_id=get_user_info.id).all()
    df_exercise_performance = dataframe_manager.create_dashboard_df(table=ExercisePerformance,
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
    get_all_squat_data = PrDetails.query.filter_by(user_id=current_user.id, lift_id=1).all()
    get_all_bench_data = PrDetails.query.filter_by(user_id=current_user.id, lift_id=2).all()
    get_all_deadlift_data = PrDetails.query.filter_by(user_id=current_user.id, lift_id=3).all()

    if len(get_all_squat_data) != 0 and len(get_all_bench_data) != 0 and len(get_all_deadlift_data) != 0:

        has_data = True

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
        graphJSON1 = plot_function.area_plot(
            df_exercise=join_df_by_BW,
            x='BW',
            y='WILKS',
            text=None,
            text_color=None,
            xaxis_title='Poids du corps',
            yaxis_title='Coefficient WILKS',
            color_column=None,
            line_color='#00ffd9',
            y_range=[join_df_by_BW['WILKS'].min() - 100, join_df_by_BW['WILKS'].max() + 100],
            line_group=None,
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
    else:
        has_data = False
        join_df = pd.DataFrame()
        graphJSON1 = None
        graphJSON2 = None

    # Create Wilks/Date DF:
    wilks_by_date_df = pd.DataFrame(columns=['Date', 'Total', 'WILKS'])

    if has_data:

        for wilks in Wilks.query.filter_by(user_id=current_user.id).all():
            wilks_by_date_df = wilks_by_date_df.append({'Date': pd.to_datetime(wilks.date),
                                                        'WILKS': wilks.wilks_coeff,
                                                        'Total': wilks.total},
                                                       ignore_index=True)

        print(f'wilks by date df :\n{wilks_by_date_df}')
        print(wilks_by_date_df['WILKS'].min())

        # Create line plot (Wilks/Date):
        graphJSON3 = plot_function.area_plot(
            df_exercise=wilks_by_date_df,
            title="Evolution de vos coefficients WILKS en fonction du temps",
            color_column=None,
            x=wilks_by_date_df['Date'],
            y=wilks_by_date_df['WILKS'],
            text=None,
            text_color=None,
            xaxis_title=None,
            line_color='#00e5ff',
            y_range=[wilks_by_date_df['WILKS'].min() - 100, wilks_by_date_df['WILKS'].max() + 100],
            yaxis_title='WILKS Coefficient',
            line_group=None
        )
    else:
        graphJSON3 = None

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
        # print(global_pr_df)

        graphJSON = plot_function.area_plot(
            df_exercise=global_pr_df,
            x='Date',
            y='Charge',
            text='BW',
            text_color='#ff00a5',
            xaxis_title=None,
            yaxis_title='Charge (en Kg)',
            color_column='Exercice',
            line_color='#ff00a5',
            y_range=None,
            line_group=None,
            title="SBD - Evolution de vos charges maximales en fonction du temps"
        )

        # Generate line plot:
        # graphJSON = plot_function.area_plot_with_scale(
        #     df_exercise=global_pr_df,
        #     reps_range=['Squat', 'Benchpress', 'Deadlift'],
        #     legend_order='normal',
        #     color_discrete_sequence=['#00f9ff', '#ff00db', '#bd00ff'],
        #     x='Date',
        #     y='Charge',
        #     text=['BW'],
        #     xaxis_title=None,
        #     yaxis_title='Charge (en Kg)',
        #     color_column='Exercice',
        #     y_range=None,
        #     title="SBD - Evolution de vos charges maximales en fonction du temps"
        # )



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
    lift_id = request.args.get('lift_id')
    # print(lift_id)

    for bw in get_bw_data:
        if bw.bodyweight is not None:
            has_bw_data = True
            break

    if not has_bw_data:
        flash("Pour ajouter vos records personnels, vous devez d'abord renseigner "
              "votre poids du corps dans vos paramètres.")
        return render_template('edit_rm.html',
                               is_logged=current_user.is_authenticated,
                               has_bw_data=False,
                               exercise_name=exercise_name,
                               title_content=f"Ajout d'un nouveau record personnel pour le {exercise_name}")
    else:
        # Add new PR:
        form = AddPersonalRecord()
        if form.validate_on_submit():
            last_bw = user_data.get_last_bw(table=PrDetails, user_id=current_user.id)

            new_pr = PrDetails(
                date=form.date_record.data,
                lift_id=int(request.args.get('lift_id')),
                weight=form.input_record.data,
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

    all_lift_id = [1, 2, 3]
    all_lift_id.remove(lift_id)

    # Get bw of current PR:
    bw_of_pr = PrDetails.query.filter_by(user_id=current_user.id, lift_id=lift_id, date=pr_date).first().bodyweight
    others_pr = []

    # Get bests PRs of other lift according to the current BW
    for lift in all_lift_id:
        current_pr = [lift.weight for lift in PrDetails.query.filter_by(user_id=current_user.id,lift_id=lift, bodyweight=bw_of_pr,).all()]
        if len(current_pr) != 0:
            current_pr = max(current_pr)
            others_pr.append(current_pr)

    others_pr.append(PrDetails.query.filter_by(user_id=current_user.id, lift_id=lift_id, date=pr_date).first().weight)

    # Checking & delete if there is a WILKS coefficient based on the current PR:
    if len(others_pr) == 3:
        wilks_calculator = WilksCalculator()
        current_wilks = wilks_calculator.wilks_calculation(sex=current_user.sex, bw=bw_of_pr, total=sum(others_pr))

        if Wilks.query.filter_by(user_id=current_user.id, wilks_coeff=current_wilks, total=sum(others_pr), bodyweight=bw_of_pr).first():
            db.session.delete(Wilks.query.filter_by(user_id=current_user.id, wilks_coeff=current_wilks, total=sum(others_pr), bodyweight=bw_of_pr).first())
            db.session.commit()

    # Delete PR according to the date
    pr_to_delete = PrDetails.query.filter_by(user_id=current_user.id, lift_id=lift_id, date=pr_date).first()
    db.session.delete(pr_to_delete)
    db.session.commit()

    return redirect(url_for('track_rm', user_id=current_user.id))


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
