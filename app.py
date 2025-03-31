# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///genealogie.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Personne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    date_naissance = db.Column(db.String(10), nullable=False)
    est_decede = db.Column(db.Boolean, default=False)
    parent1_id = db.Column(db.Integer, db.ForeignKey('personne.id'), nullable=True)
    parent2_id = db.Column(db.Integer, db.ForeignKey('personne.id'), nullable=True)
    parent1 = relationship('Personne', remote_side=[id], backref='enfants_parent1', foreign_keys=[parent1_id])
    parent2 = relationship('Personne', remote_side=[id], backref='enfants_parent2', foreign_keys=[parent2_id])

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prenom = request.form['prenom']
        nom = request.form['nom']
        date_naissance = request.form['date_naissance']
        existing_person = Personne.query.filter_by(prenom=prenom, nom=nom, date_naissance=date_naissance).first()
        if existing_person:
            return redirect(url_for('index'))
        personne = Personne(prenom=prenom, nom=nom, date_naissance=date_naissance, est_decede=False)
        db.session.add(personne)
        db.session.commit()
        return redirect(url_for('index'))
    personnes = Personne.query.all()
    return render_template('index.html', personnes=personnes)

@app.route('/arbre')
def arbre():
    personnes = Personne.query.all()
    roland = db.session.get(Personne, 2)
    josiane = db.session.get(Personne, 3)
    if not roland or not josiane:
        return "Parents non trouvés", 404
    arbre_data = {
        'name': f"{roland.prenom} {roland.nom} & {josiane.prenom} {josiane.nom}",
        'children': [{'name': f"{p.prenom} {p.nom} ({p.date_naissance})"} for p in personnes if p.parent1_id in [2, 3] or p.parent2_id in [2, 3]]
    }
    return render_template('arbre.html', arbre_data=arbre_data)

if __name__ == '__main__':
    app.run()
