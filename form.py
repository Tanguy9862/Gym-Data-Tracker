from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, DateField, RadioField
from wtforms.validators import DataRequired, Length, Email, NumberRange
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

