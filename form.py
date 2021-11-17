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
    global_performance = StringField("Performance globale", validators=[DataRequired()])
    three_reps = StringField("Charge sur 3 répétitions")
    three_rpe = IntegerField("3 Répétitions RPE", default=0, validators=[NumberRange(min=0, max=10,
                                                                          message="Le RPE doit être compris entre 1 et "
                                                                                  "10.")])
    two_reps = StringField("Charge sur 2 répétitions")
    two_rpe = IntegerField("2 Répétitions RPE", default=0, validators=[NumberRange(min=0, max=10,
                                                                          message="Le RPE doit être compris entre 1 et "
                                                                                  "10.")])
    one_reps = StringField("Charge sur 1 répétition")
    one_rpe = IntegerField("1 Répétition RPE", default=0, validators=[NumberRange(min=0, max=10,
                                                                          message="Le RPE doit être compris entre 1 et "
                                                                                  "10.")])
    ten_reps = StringField("Charge sur 10 répétitions")
    fifteen_reps = StringField("Charge sur 15 répétitions")
    twenty_reps = StringField("Charge sur 20 répétitions")

    all_data = StringField('Ensemble des performances')

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

