import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, DoctorCreateForm, DoctorUpdateForm, PatientCreateForm, PatientUpdateForm, TreatmentplanCreateForm, TreatmentplanUpdateForm, TreatCreateForm, TreatUpdateForm, AppointmentCreateForm, AppointmentUpdateForm
from flaskDemo.models import Appointment, Doctor, Patient, TreatmentPlan, Treats, User
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route("/")
@app.route("/home")
def home():
    #results = Treats.query.all()
    
    #resultsinvoice = Treats.query.join(TreatmentPlan,Treats.TreatmentID == TreatmentPlan.TreatmentID)\
     #           .add_columns(TreatmentPlan.TreatmentCost, Treats.Description, TreatmentPlan.Medicine_name)\
      #          .join(Appointment, Treats.AppointmentID == Appointment.AppointmentID)\
       #         .join(Patient, Appointment.PatientSSN == Patient.PatientSSN)\
        #        .add_columns(Patient.FirstName, Patient.LastName, Appointment.AppointmentID, Appointment.Date, Appointment.Time, Appointment.Reason)
                
      
    res2 = Treats.query.join(TreatmentPlan, Treats.TreatmentID == Treats.TreatmentID)\
          .join(Doctor, Doctor.DoctorID == Treats.DoctorID)\
          .join(Appointment, Appointment.AppointmentID == Treats.AppointmentID)
        
    return render_template('home.html', outString=res2)

@app.route("/invoices")
@login_required
def invoices():  
    resultsinvoice = Treats.query.join(TreatmentPlan,Treats.TreatmentID == TreatmentPlan.TreatmentID)\
                    .add_columns(TreatmentPlan.TreatmentCost, Treats.Description, TreatmentPlan.Medicine_name)\
                    .join(Appointment, Treats.AppointmentID == Appointment.AppointmentID)\
                    .join(Patient, Appointment.PatientSSN == Patient.PatientSSN)\
                    .add_columns(Patient.FirstName, Patient.LastName, Appointment.AppointmentID, Appointment.Date, Appointment.Time, Appointment.Reason)
                
    return render_template('invoices.html', outString1=resultsinvoice)

   # resultsinvoice = Appointment.query.join(Patient,Appointment.PatientSSN == Patient.PatientSSN) \
    #         .add_columns(Appointment.PatientSSN, Patient.FirstName, Patient.LastName, Patient.Address) \
     #        .join(Doctor, Treats.DoctorID == Doctor.DoctorID).add_columns(Treats.DoctorID)\
      #          .join(TreatmentPlan, Treats.TreatmentID == TreatmentPlan.TreatmentID).add_columns(Treats.TreatmentID, Treats.Description,TreatmentPlan.TreatmentCost)\
       #         .join(Appointment, Treats.AppointmentID == Appointment.AppointmentID).add_columns(Treats.AppointmentID)
                
    #return render_template('invoice.html', title='invoice', outString1=resultsinvoice)
                
    #results = Faculty.query.join(Qualified,Faculty.facultyID == Qualified.facultyID) \
     #         .add_columns(Faculty.facultyID, Faculty.facultyName, Qualified.Datequalified, Qualified.courseID)
    #return render_template('join.html', title='Join',joined_1_n=results, joined_m_n=results2)

@app.route("/treat/<TreatmentID>/<AppointmentID>/<DoctorID>")
@login_required
def treat(TreatmentID, AppointmentID, DoctorID):
    treat = Treats.query.get_or_404([TreatmentID, AppointmentID, DoctorID])
    doctor = Doctor.query.get_or_404(DoctorID)
    appointment = Appointment.query.join(Patient, Appointment.PatientSSN == Patient.PatientSSN)\
                    .filter(Appointment.AppointmentID == AppointmentID)\
                    .add_columns(Appointment.AppointmentID, Patient.PatientSSN, Patient.FirstName, Patient.LastName).first()
    treatment = TreatmentPlan.query.get_or_404(TreatmentID)
    return render_template('treat.html', treat=treat, doctor=doctor, appointment=appointment, treatment=treatment)

@app.route("/treat/new", methods=['GET', 'POST'])
@login_required
def new_treat():
    form = TreatCreateForm()
    if form.validate_on_submit():
        treat = Treats(TreatmentID=form.TreatmentID.data,AppointmentID=form.AppointmentID.data, DoctorID=form.DoctorID.data, Description=form.Description.data)
        db.session.add(treat)
        db.session.commit()
        flash('You have added a new treat!', 'success')
        return redirect(url_for('home'))
    return render_template('create_treat.html', title='New Treat', form=form, legend='New Treat')

@app.route("/treat/<TreatmentID>/<AppointmentID>/<DoctorID>/update", methods=['GET', 'POST'])
@login_required
def update_treat(TreatmentID, AppointmentID, DoctorID):
    treat = Treats.query.get_or_404([TreatmentID, AppointmentID, DoctorID])

    form = TreatUpdateForm()
    if form.validate_on_submit():
        treat.TreatmentID = form.TreatmentID.data
        treat.AppointmentID = form.AppointmentID.data
        treat.DoctorID = form.DoctorID.data
        treat.Description = form.Description.data
      
        db.session.commit()
        flash('The treat has been updated!', 'success')
        return redirect(url_for('treat', TreatmentID=treat.TreatmentID, AppointmentID=treat.AppointmentID, DoctorID=treat.DoctorID))
    elif request.method == 'GET':
        form.TreatmentID.data = treat.TreatmentID
        form.AppointmentID.data = treat.AppointmentID
        form.DoctorID.data = treat.DoctorID
        form.Description.data = treat.Description
    
    return render_template('create_treat.html', title='Update Treat', form=form, legend='Update Treat')

@app.route("/treat/<TreatmentID>/<AppointmentID>/<DoctorID>/delete", methods=['POST'])
@login_required
def delete_treat(TreatmentID, AppointmentID, DoctorID):
    treat = Treats.query.get_or_404([TreatmentID,AppointmentID,DoctorID])
    db.session.delete(treat)
    db.session.commit()
    flash('The treat has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/doctors")
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', title="Doctors", outString=doctors)

@app.route("/doctors/<DoctorID>")
@login_required
def doctor(DoctorID):
    doctor = Doctor.query.get_or_404(DoctorID)
    return render_template('doctor.html', title="doctor.DoctorID", doctor=doctor)

@app.route("/doctors/new", methods=['GET', 'POST'])
@login_required
def new_doctor():
    form = DoctorCreateForm()
    if form.validate_on_submit():
        doctor = Doctor(DoctorID=form.DoctorID.data, FirstName=form.FirstName.data, LastName=form.LastName.data, Speciality=form.Speciality.data)
        db.session.add(doctor)
        db.session.commit()
        flash('You have added a new doctor!', 'success')
        return redirect(url_for('doctors'))
    return render_template('create_doctor.html', title='New Doctor', form=form, legend='New Doctor')

@app.route("/doctors/<DoctorID>/update", methods=['GET', 'POST'])
@login_required
def update_doctor(DoctorID):
    doctor = Doctor.query.get_or_404(DoctorID)

    form = DoctorUpdateForm()
    if form.validate_on_submit():
        doctor.DoctorID = form.DoctorID.data
        doctor.FirstName = form.FirstName.data
        doctor.LastName = form.LastName.data
        doctor.Speciality = form.Speciality.data
        
        db.session.commit()
        flash('The doctor has been updated!', 'success')
        return redirect(url_for('doctor', DoctorID=DoctorID))
    elif request.method == 'GET':
        form.DoctorID.data = doctor.DoctorID
        form.FirstName.data = doctor.FirstName
        form.LastName.data = doctor.LastName
        form.Speciality.data = doctor.Speciality
        
    return render_template('create_doctor.html', title='Update Doctor', form=form, legend='Update Doctor')

@app.route("/doctors/<DoctorID>/delete", methods=['POST'])
@login_required
def delete_doctor(DoctorID):
    doctor = Doctor.query.get_or_404(DoctorID)
    db.session.delete(doctor)
    db.session.commit()
    flash('The doctor has been deleted!', 'success')
    return redirect(url_for('doctors'))


@app.route("/patients")
def patients():
    patients = Patient.query.all()
    return render_template('patients.html', title="Patients", outString=patients)

@app.route("/patients/<patientssn>")
@login_required
def patient(patientssn):
    patient = Patient.query.get_or_404(patientssn)
    return render_template('patient.html', title="patient", patient=patient)

@app.route("/patients/new", methods=['GET', 'POST'])
@login_required
def new_patient():
    form = PatientCreateForm()
    if form.validate_on_submit():
        patient = Patient(PatientSSN=form.patientssn.data, FirstName=form.first_name.data, LastName=form.last_name.data, Gender=form.gender.data,
                            Address=form.address.data, ContactNumber=form.contact_number.data)
        db.session.add(patient)
        db.session.commit()
        flash('You have added a new patient!', 'success')
        return redirect(url_for('patients'))
    return render_template('create_patient.html', title='New Patient', form=form, legend='New Patient')

@app.route("/patients/<patientssn>/update", methods=['GET', 'POST'])
@login_required
def update_patient(patientssn):
    patient = Patient.query.get_or_404(patientssn)

    form = PatientUpdateForm()
    if form.validate_on_submit():
        patient.PatientSSN = form.patientssn.data
        patient.FirstName = form.first_name.data
        patient.LastName = form.last_name.data
        patient.Gender = form.gender.data
        patient.Address = form.address.data
        patient.ContactNumber = form.contact_number.data
        db.session.commit()
        flash('The patient has been updated!', 'success')
        return redirect(url_for('patient', patientssn=patientssn))
    elif request.method == 'GET':
        form.patientssn.data = patient.PatientSSN
        form.first_name.data = patient.FirstName
        form.last_name.data = patient.LastName
        form.gender.data = patient.Gender
        form.address.data = patient.Address
        form.contact_number.data = patient.ContactNumber
    return render_template('create_patient.html', title='Update Patient', form=form, legend='Update Patient')

@app.route("/patients/<patientssn>/delete", methods=['POST'])
@login_required
def delete_patient(patientssn):
    patient = Patient.query.get_or_404(patientssn)
    db.session.delete(patient)
    db.session.commit()
    flash('The patient has been deleted!', 'success')
    return redirect(url_for('patients'))

@app.route("/appointments")
def appointments(): 
    appointments = Appointment.query.join(Patient, Appointment.PatientSSN == Patient.PatientSSN)\
                    .add_columns(Appointment.AppointmentID, Patient.FirstName, Patient.LastName, Appointment.Date, Appointment.Time, Appointment.Is_Emergency)
    return render_template('appointments.html', title="Appointments", outString=appointments)

@app.route("/appointments/<AppointmentID>")
@login_required
def appointment(AppointmentID):
    appointment = Appointment.query.join(Patient, Appointment.PatientSSN == Patient.PatientSSN)\
                    .filter(Appointment.AppointmentID == AppointmentID) \
                    .add_columns(Appointment.AppointmentID, Patient.PatientSSN, Patient.FirstName, Patient.LastName, Appointment.Date, Appointment.Time, Appointment.Is_Emergency, Appointment.Reason).first()
    return render_template('appointment.html', title="Appointment", appointment=appointment)

@app.route("/appointments/new", methods=['GET', 'POST'])
@login_required
def new_appointment():
    form = AppointmentCreateForm()
    if form.validate_on_submit():
        appointment = Appointment(AppointmentID=form.appointmentid.data, PatientSSN=form.patient.data, Date=form.date.data, Time=form.time.data, Is_Emergency=form.is_emergency.data, Reason=form.reason.data)
        db.session.add(appointment)
        db.session.commit()
        flash('You have added a new Appointment!', 'success')
        return redirect(url_for('appointments'))
    return render_template('create_appointment.html', title='New Appointment', form=form, legend='New Appointment')

@app.route("/appointments/<AppointmentID>/update", methods=['GET', 'POST'])
@login_required
def update_appointment(AppointmentID):
    appointment = Appointment.query.get_or_404(AppointmentID)

    form = AppointmentUpdateForm()
    if form.validate_on_submit():
        appointment.AppointmentID = form.appointmentid.data
        appointment.PatientSSN = form.patient.data
        appointment.Date = form.date.data
        appointment.Time = form.time.data
        appointment.Is_Emergency = form.is_emergency.data
        appointment.Reason = form.reason.data
        db.session.commit()
        flash('The Appointment has been updated!', 'success')
        return redirect(url_for('appointment', AppointmentID=appointment.AppointmentID))
    elif request.method == 'GET':
        form.appointmentid.data = appointment.AppointmentID
        form.patient.data = appointment.PatientSSN
        form.date.data = appointment.Date
        form.time.data = appointment.Time
        form.is_emergency.data = appointment.Is_Emergency
        form.reason.data = appointment.Reason
    return render_template('create_appointment.html', title='Update Appointment', form=form, legend='Update Appointment')

@app.route("/appointments/<AppointmentID>/delete", methods=['POST'])
@login_required
def delete_appointment(AppointmentID):
    appointment = Appointment.query.get_or_404(AppointmentID)
    db.session.delete(appointment)
    db.session.commit()
    flash('The Appointment has been deleted!', 'success')
    return redirect(url_for('appointments'))



@app.route("/treatmentplans")
def treatmentplans():
    treatmentplans = TreatmentPlan.query.all()
    return render_template('treatmentplans.html', title="Treatmentplan", outString=treatmentplans)

@app.route("/treatmentplans/<TreatmentID>")
@login_required
def treatmentplan(TreatmentID):
    treatmentplan = TreatmentPlan.query.get_or_404(TreatmentID)
    return render_template('treatmentplan.html', title="treatmentplan.TreatmentID", treatmentplan=treatmentplan)

@app.route("/treatmentplans/new", methods=['GET', 'POST'])
@login_required
def new_treatmentplan():
    form = TreatmentplanCreateForm()
    if form.validate_on_submit():
        treatmentplan = TreatmentPlan(TreatmentID=form.TreatmentID.data,TreatmentCost=form.TreatmentCost.data,\
                        Is_Medication=form.Is_Medication.data,\
                        Medicine_name=form.Medicine_name.data, Dosage=form.Dosage.data, \
                        Is_Trauma=form.Is_Trauma.data, Measures_taken=form.Measures_taken.data,\
                        Is_councelling=form.Is_councelling.data, \
                        Councelling_Feedback=form.Councelling_Feedback.data, \
                        Is_therapy=form.Is_therapy.data, Therapy_Outcome=form.Therapy_Outcome.data)
        db.session.add(treatmentplan)
        db.session.commit()
        flash('You have added a new treatmentplan!', 'success')
        return redirect(url_for('treatmentplans'))
    return render_template('create_treatmentplan.html', title='New Treatmentplan', form=form, legend='New Treatmentplan')

@app.route("/treatmentplans/<TreatmentID>/update", methods=['GET', 'POST'])
@login_required
def update_treatmentplan(TreatmentID):
    treatmentplan = TreatmentPlan.query.get_or_404(TreatmentID)

    form = TreatmentplanUpdateForm()
    if form.validate_on_submit():
        treatmentplan.TreatmentID = form.TreatmentID.data
        treatmentplan.TreatmentCost = form.TreatmentCost.data
        treatmentplan.Is_Trauma = form.Is_Trauma.data
        treatmentplan.Measures_taken = form.Measures_taken.data
        treatmentplan.Is_Medication = form.Is_Medication.data
        treatmentplan.Medicine_name = form.Medicine_name.data
        treatmentplan.Dosage = form.Dosage.data
        treatmentplan.Is_councelling = form.Is_councelling.data
        treatmentplan.Councelling_Feedback = form.Councelling_Feedback.data
        treatmentplan.Is_therapy = form.Is_therapy.data
        treatmentplan.Therapy_Outcome = form.Therapy_Outcome.data
        
        db.session.commit()
        flash('The treatmentplan has been updated!', 'success')
        return redirect(url_for('treatmentplan', TreatmentID=TreatmentID))
    elif request.method == 'GET':
        form.TreatmentID.data =treatmentplan.TreatmentID
        form.TreatmentCost.data =treatmentplan.TreatmentCost
        form.Is_Trauma.data= treatmentplan.Is_Trauma
        form.Measures_taken.data = treatmentplan.Measures_taken
        form.Is_Medication.data=treatmentplan.Is_Medication
        form.Medicine_name.data=treatmentplan.Medicine_name
        form.Dosage.data=treatmentplan.Dosage
        form.Is_councelling.data=treatmentplan.Is_councelling
        form.Councelling_Feedback.data=treatmentplan.Councelling_Feedback
        form.Is_therapy.data=treatmentplan.Is_therapy
        form.Therapy_Outcome.data=treatmentplan.Therapy_Outcome
              
    return render_template('create_treatmentplan.html', title='Update Treatmentplan', form=form, legend='Update Treatmentplan')

@app.route("/treatmentplans/<TreatmentID>/delete", methods=['POST'])
@login_required
def delete_treatmentplan(TreatmentID):
    treatmentplan = TreatmentPlan.query.get_or_404(TreatmentID)
    db.session.delete(treatmentplan)
    db.session.commit()
    flash('The treatmentplan has been deleted!', 'success')
    return redirect(url_for('treatmentplans'))




