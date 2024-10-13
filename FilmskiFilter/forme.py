from flask_wtf import FlaskForm
from wtforms import IntegerField,StringField,SubmitField, TextAreaField, URLField, PasswordField
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo


class MovieForm(FlaskForm):
    title = StringField("Titl", validators=[InputRequired("Unesite titl!")])
    director = StringField("Redatelj", validators=[InputRequired("Unesite redatelja!")])
    
    year = IntegerField(
        "Godina izlaska",
          validators=[
            InputRequired("Unesite godinu!"),
            NumberRange(min=1878, max=2024, message="Molim stavite godinu u formatu YYYY.")
            ])

    submit = SubmitField("Dodaj Film") 

class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]: 
            self.data =  [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []


class ExtendedMovieForm(MovieForm):
    cast = StringListField("Glumačka postava")
    series = StringListField("Serijal")
    tags = StringListField("Žanr")
    description = TextAreaField("Opis")
    video_link = URLField()

    submit = SubmitField("Primjeni") 



class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired("Unesite email!"), Email(message="Netočan unos email adrese!")])
    password = PasswordField(
        "Lozinka",
        validators=[
            InputRequired("Unesite lozinku!"),
            Length(min=4, max=20, 
            message="Lozinka mora biti između 4 i 20 karaktera")])
    confirm_password = PasswordField(
        "Potvrda Lozinke",
        validators=[
            InputRequired("Unesite lozinku!"),
            EqualTo(
            "password",
            message="Lozinke se ne podudaraju!")])
    submit = SubmitField("Registracija")
 

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired("Unesite email!")])
    password = PasswordField("Lozinka", validators=[InputRequired("Unesite lozinku!")])
    submit = SubmitField("Prijava")


class SearchForm(FlaskForm):
    searched = StringField("Pretraženo", validators=[InputRequired()])
    submit = SubmitField("Pretraži")
