from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Pandora965@localhost/Fitness_Center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.String(required=True)

    class Meta:
        fields = ('name', 'age', 'id')

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class WorkoutSchema(ma.Schema):
    member_id = fields.String(required=True)
    session_date = fields.String(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("date", "time", "activity", "member_id", "id")

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

class Members(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.String(15))
    #workouts = db.relationship('Workout', backref='member')

class WorkoutSessions(db.Model):
    __tablename__ = 'WorkoutSessions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))

@app.route('/')
def home():
    return 'Welcome to the Fitness Center Database'

#Members functions below#

@app.route('/members', methods=['GET'])
def get_members():
    members = Members.query.all()
    return members_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_member = Members(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'New member added successfully'}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Members.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({'message':'Member details updated successfully'}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Members.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message':'Workout removed successfully'}), 200

#Workout Session functions below#

@app.route('/workoutsessions', methods=['GET'])
def get_workouts():
    workouts = WorkoutSessions.query.all()
    return workouts_schema.jsonify(workouts)

@app.route('/workoutsessions', methods=['POST'])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_workout = WorkoutSessions(member_id=workout_data['member_id'], date=workout_data['date'], time=workout_data['time'], activity=workout_data['activity'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({'message': 'New workout added successfully'}), 201

@app.route('/workoutsessions/<int:id>', methods=['PUT'])
def update_workout(id):
    workout = WorkoutSessions.query.get_or_404(id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    workout.member_id = workout_data['member_id']
    workout.date = workout_data['date']
    workout.time = workout_data['time']
    workout.activity = workout_data['activity']
    db.session.commit()
    return jsonify({'message':'Workout details updated successfully'}), 200

@app.route('/workoutsessions/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = WorkoutSessions.query.get_or_404(id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message':'Workout removed successfully'}), 200

@app.route('/workoutsessions/by-member_id', methods=['GET'])
def get_workout_one_member():
    member_id = request.args.get('member_id')
    workout = WorkoutSessions.query.filter(WorkoutSessions.member_id == member_id).all()
    if workout:
        return workouts_schema.jsonify(workout)
    else:
        return jsonify({"message": "Workout not found"}), 404

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
