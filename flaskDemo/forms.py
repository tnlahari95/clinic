from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, TimeField, SelectField, HiddenField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import Appointment, Doctor, Patient, TreatmentPlan, Treats, User
from wtforms.fields.html5 import DateField

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class DoctorCreateForm(FlaskForm):
    DoctorID = IntegerField('Doctor ID:', validators=[DataRequired()])
    FirstName = StringField('First Name:', validators=[DataRequired()])
    LastName = StringField('Last Name:', validators=[DataRequired()])
    Speciality = StringField('Speciality:', validators=[DataRequired()])
    submit = SubmitField('Create')

class DoctorUpdateForm(DoctorCreateForm):
    submit = SubmitField('Update')

class PatientCreateForm(FlaskForm):
    patientssn = IntegerField('Patient SSN', validators=[DataRequired()])
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    gender = StringField('Gender:', validators=[DataRequired(), Length(max=1)])
    address = StringField('Address:', validators=[DataRequired()])
    contact_number = StringField('Contact No:', validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Create')

class PatientUpdateForm(PatientCreateForm):
    submit = SubmitField('Update')


class AppointmentCreateForm(FlaskForm):
    appointmentid = IntegerField('Appointment ID', validators=[DataRequired()])
    patient = SelectField('Patient', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    is_emergency = BooleanField('Is Emergency')
    reason = TextAreaField('Reason')
    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super(AppointmentCreateForm, self).__init__(*args, **kwargs)
        self.patient.choices = [
            (a.PatientSSN, a.FirstName + " " + a.LastName)
            for a in Patient.query.with_entities(Patient.PatientSSN, Patient.FirstName, Patient.LastName).distinct().order_by(Patient.FirstName)
        ]

class AppointmentUpdateForm(AppointmentCreateForm):
    submit = SubmitField('Update')
    
    
class TreatmentplanCreateForm(FlaskForm):
    TreatmentID = IntegerField('TreatmentID', validators=[DataRequired()])
    TreatmentCost = DecimalField('TreatmentCost:')
    Is_Trauma = BooleanField('Is trauma:')
    Measures_taken = StringField('Measures taken:')
    Is_Medication = BooleanField('Is medication:')
    Medicine_name = StringField('Medicine name:')
    Dosage = StringField('Dosage')
    Is_councelling = BooleanField('Is Councelling:')
    Councelling_Feedback = StringField('Councelling Feedback:')
    Is_therapy = BooleanField('Is therapy:')
    Therapy_Outcome = StringField('Therapy Outcome:')
    
    submit = SubmitField('Create')

class TreatmentplanUpdateForm(TreatmentplanCreateForm):
    submit = SubmitField('Update')
    
class TreatCreateForm(FlaskForm):
    doctors = Patient.query.with_entities(Doctor.DoctorID, Doctor.FirstName, Doctor.LastName).distinct()
    doctorchoices = [(row[0],row[1] + " " + row[2]) for row in doctors]

    TreatmentID = SelectField('Treatment', coerce=int, validators=[DataRequired()])
    AppointmentID = SelectField('Appointment', coerce=int, validators=[DataRequired()])
    DoctorID = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    Description = StringField('Description:', validators=[DataRequired()])
    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super(TreatCreateForm, self).__init__(*args, **kwargs)
        self.TreatmentID.choices = [
            (a.TreatmentID, a.TreatmentID)
            for a in TreatmentPlan.query.with_entities(TreatmentPlan.TreatmentID).distinct()
        ]
        self.AppointmentID.choices = [
            (a.AppointmentID, str(a.AppointmentID) + " - " + a.FirstName + " " + a.LastName)
            for a in Appointment.query.join(Patient, Appointment.PatientSSN == Patient.PatientSSN)\
                            .with_entities(Appointment.AppointmentID, Patient.FirstName, Patient.LastName).order_by(Appointment.AppointmentID)
        ]
        self.DoctorID.choices = [
            (a.DoctorID, a.FirstName + " " + a.LastName)
            for a in Doctor.query.with_entities(Doctor.DoctorID, Doctor.FirstName, Doctor.LastName).distinct()
        ]

class TreatUpdateForm(TreatCreateForm):
    submit = SubmitField('Update')