from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, TimeField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import Appointment, Doctor, Patient, TreatmentPlan, Treats, User
from wtforms.fields.html5 import DateField


did = Treats.query.with_entities(Treats.DoctorID)
dChoices2 = [(row[0],row[0]) for row in did]  # change
results=list()
for row in did:
    rowDict=row._asdict()
    results.append(rowDict)
dChoices = [(row['DoctorID'],row['DoctorID']) for row in results]
regex1='^((((19|20)(([02468][048])|([13579][26]))-02-29))|((20[0-9][0-9])|(19[0-9][0-9]))-((((0[1-9])'
regex2='|(1[0-2]))-((0[1-9])|(1\d)|(2[0-8])))|((((0[13578])|(1[02]))-31)|(((0[1,3-9])|(1[0-2]))-(29|30)))))$'
regex=regex1 + regex2


tid = Treats.query.with_entities(Treats.TreatmentID)
tChoices2 = [(row[0],row[0]) for row in tid]  # change
results=list()
for row in tid:
    rowDict=row._asdict()
    results.append(rowDict)
tChoices = [(row['TreatmentID'],row['TreatmentID']) for row in results]
regex1='^((((19|20)(([02468][048])|([13579][26]))-02-29))|((20[0-9][0-9])|(19[0-9][0-9]))-((((0[1-9])'
regex2='|(1[0-2]))-((0[1-9])|(1\d)|(2[0-8])))|((((0[13578])|(1[02]))-31)|(((0[1,3-9])|(1[0-2]))-(29|30)))))$'
regex=regex1 + regex2

aid = Treats.query.with_entities(Treats.AppointmentID)
aChoices2 = [(row[0],row[0]) for row in aid]  # change
results=list()
for row in aid:
    rowDict=row._asdict()
    results.append(rowDict)
aChoices = [(row['AppointmentID'],row['AppointmentID']) for row in results]
regex1='^((((19|20)(([02468][048])|([13579][26]))-02-29))|((20[0-9][0-9])|(19[0-9][0-9]))-((((0[1-9])'
regex2='|(1[0-2]))-((0[1-9])|(1\d)|(2[0-8])))|((((0[13578])|(1[02]))-31)|(((0[1,3-9])|(1[0-2]))-(29|30)))))$'
regex=regex1 + regex2



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
    DoctorID = IntegerField('Doctor ID', validators=[DataRequired()])
    FirstName = StringField('First Name:', validators=[DataRequired()])
    LastName = StringField('Last Name:', validators=[DataRequired()])
    Speciality = StringField('Speciality:', validators=[DataRequired()])
    submit = SubmitField('Create')

class DoctorUpdateForm(DoctorCreateForm):
    DoctorID = IntegerField('Doctor ID:', validators=[DataRequired()])
    FirstName = StringField('First Name:', validators=[DataRequired()] )
    LastName = StringField('last Name:', validators=[DataRequired()] )
    Speciality = StringField('Speciality:', validators=[DataRequired()] )
    submit = SubmitField('Update')



#class DeptForm(DeptUpdateForm):

#    dnumber=IntegerField('Department Number', validators=[DataRequired()])
#    submit = SubmitField('Add this department')

#    def validate_dnumber(self, dnumber):    #because dnumber is primary key and should be unique
#        dept = Department.query.filter_by(dnumber=dnumber.data).first()
#        if dept:
#            raise ValidationError('That department number is taken. Please choose a different one.')

class PatientCreateForm(FlaskForm):
    patientssn = IntegerField('Patient SSN', validators=[DataRequired()])
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    gender = StringField('Gender:', validators=[DataRequired(), Length(max=1)])
    address = StringField('Address:', validators=[DataRequired()])
    contact_number = StringField('Contact No:', validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Create')

class PatientUpdateForm(PatientCreateForm):
    patientssn = IntegerField('Patient SSN', validators=[DataRequired()])
    #, render_kw={'readonly': True}
    submit = SubmitField('Update')
    
class AppointmentCreateForm(FlaskForm):
    patients = Patient.query.with_entities(Patient.PatientSSN, Patient.FirstName, Patient.LastName).distinct()
    #appointments=Appointment.query.with_entities(Appointment.AppointmentID)
    choices = [(row[0],row[0]) for row in patients]

    appointmentid = IntegerField('Appointment ID', validators=[DataRequired()])
    patient = SelectField('Patient', choices=choices, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    is_emergency = BooleanField('Is Emergency')
    reason = TextAreaField('Reason')
    submit = SubmitField('Create')

class AppointmentUpdateForm(AppointmentCreateForm):
    
    patients = Patient.query.with_entities(Patient.PatientSSN, Patient.FirstName, Patient.LastName).distinct()
    #appointments=Appointment.query.with_entities(Appointment.AppointmentID)
    choices = [(row[0],row[0]) for row in patients]
    
    appointmentid = IntegerField('Appointment ID', validators=[DataRequired()])
    patient = IntegerField('Patient', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    
                                 #,  choices=choices, render_kw={'readonly': True})
    submit = SubmitField('Update')
    
    
class TreatmentplanCreateForm(FlaskForm):
    TreatmentID = IntegerField('TreatmentID', validators=[DataRequired()])
    TreatmentCost = StringField('TreatmentCost:')
    Is_Trauma = IntegerField('Is trauma:')
    Measures_taken = StringField('Measures taken:')
    Is_Medication = IntegerField('Is medication:')
    Medicine_name = StringField('Medicine name:')
    Dosage = StringField('Dosage')
    Is_councelling = IntegerField('Is Councelling:')
    Councelling_Feedback = StringField('Councelling Feedback:')
    Is_therapy = IntegerField('Is therapy:')
    Therapy_Outcome = StringField('therapy outcome:')
    
    submit = SubmitField('Create')

class TreatmentplanUpdateForm(TreatmentplanCreateForm):
    TreatmentID = IntegerField('TreatmentID', validators=[DataRequired()])
    TreatmentCost = StringField('TreatmentCost:')
    Is_Trauma = IntegerField('Is trauma:')
    Measures_taken = StringField('Measures taken:')
    Is_Medication = IntegerField('Is medication:')
    Medicine_name = StringField('Medicine name:')
    Dosage = StringField('Dosage:')
    Is_councelling = IntegerField('Is Councelling:')
    Councelling_Feedback = StringField('Councelling Feedback:')
    Is_therapy = IntegerField('Is therapy:')
    Therapy_Outcome = StringField('therapy outcome:')
    
    submit = SubmitField('Update')
    
class TreatCreateForm(FlaskForm):
    TreatmentID = IntegerField('TreatmentID', validators=[DataRequired()])
    AppointmentID = IntegerField('AppointmentID:', validators=[DataRequired()])
    DoctorID = IntegerField('DoctorID:', validators=[DataRequired()])
    Description = StringField('Description:', validators=[DataRequired()])

    submit = SubmitField('Create')

class TreatUpdateForm(TreatCreateForm):
    TreatmentID = IntegerField('TreatmentID', validators=[DataRequired()])
    AppointmentID = IntegerField('AppointmentID:', validators=[DataRequired()])
    DoctorID = IntegerField('DoctorID:', validators=[DataRequired()])
    Description = StringField('Description:', validators=[DataRequired()])
    
    submit = SubmitField('Update')