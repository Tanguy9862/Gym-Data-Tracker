from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField, DateField, RadioField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional
import datetime


class LoginForm(FlaskForm):
    username = StringField("Pseudonyme", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=8, max=15,
                                                                                message="Le mot de passe doit comporter"
                                                                                        " entre 8 et 15 caractères")])
    login_submit = SubmitField("Connexion")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message="Veuillez entrer un email valide.")])
    username = StringField("Pseudonyme", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=8, max=15,
                                                                            message="Le mot de passe doit comporter "
                                                                                    "entre 8 et 15 caractères")])
    sex = RadioField("Genre", validators=[DataRequired()], choices=["Masculin", "Féminin"])
    register_submit = SubmitField("Inscription")


class AddExercise(FlaskForm):
    exercise_name = StringField("Nom de l'exercice", validators=[DataRequired()])
    add_submit = SubmitField("Ajouter")


class EditWorkout(FlaskForm):
    date_field = DateField("Date(JJ-MM-AAAA)", format='%d-%m-%Y', default=datetime.date.today(), validators=[DataRequired()])
    all_data = StringField('Ensemble des performances', validators=[DataRequired()])
    notes = StringField('Notes', validators=[Length(min=0, max=250, message="Les notes ne peuvent pas excéder 250 caractères.")])
    sleep_time = StringField('Sommeil(heures)')

    validate_submit = SubmitField("Valider")


class EditWorkoutWithSecondaryExercise(FlaskForm):
    date_field = DateField("Date(JJ-MM-AAAA)", format='%d-%m-%Y', default=datetime.date.today(), validators=[DataRequired()])
    all_data = StringField('Ensemble des performances', validators=[DataRequired()])
    notes = StringField('Notes', validators=[Length(min=0, max=250, message="Les notes ne peuvent pas excéder 250 caractères.")])
    sleep_time = StringField('Sommeil(heures)')
    secondary_exercise_list = SelectField(u"Liste d'exercices secondaires", coerce=int)
    validate_submit = SubmitField("Valider")


class SearchUser(FlaskForm):
    search_field = StringField("Pseudonyme :", validators=[DataRequired()])
    search_submit = SubmitField("Rechercher")


class AddPersonalRecord(FlaskForm):
    date_record = DateField("Date(JJ-MM-AAAA)", format='%d-%m-%Y', default=datetime.date.today(), validators=[DataRequired()])
    input_record = StringField("Nouveau record(kg)", validators=[DataRequired()])
    save_submit = SubmitField("Enregistrer")


class EditBodyWeight(FlaskForm):
    date_bw = DateField("Date(JJ-MM-AAAA)", format='%d-%m-%Y', default=datetime.date.today(), validators=[DataRequired()])
    input_bw = StringField("Poids de corps (kg)", validators=[DataRequired()])
    save_submit = SubmitField("Enregistrer")


class AddCycle(FlaskForm):
    cycle_name = StringField('Nom du cycle', validators=[
        DataRequired(),
        Length(min=1, max=40, message='Le nom du cycle ne peut pas excéder 40 caractères.')
    ])
    starting_date = DateField("Date de début(JJ-MM-AAAA)", format='%d-%m-%Y', default=datetime.date.today())
    ending_date = DateField("Date de fin(JJ-MM-AAAA)", format='%d-%m-%Y', validators=[Optional()])
    add_submit = SubmitField("Ajouter")


class EndingCycle(FlaskForm):
    finish_button = SubmitField("Mettre fin au cycle")


class AddSecondaryExercise(FlaskForm):
    secondary_exercise_name = StringField("Nom de l'exercice", validators=[
        DataRequired(),
        Length(min=1, max=30, message='Le nom du cycle ne peut pas excéder 30 caractères.')
    ])
    list_data = SelectField(u"Liste d'exercices secondaires", coerce=int)
    add_submit = SubmitField("Ajouter")


class AddList(FlaskForm):
    list_name = StringField("Nom de la liste", validators=[
        DataRequired(),
        Length(min=1, max=25, message="Le nom d'une liste ne peut pas excéder 25 caractères")
    ])
    create_submit = SubmitField("Créer")


