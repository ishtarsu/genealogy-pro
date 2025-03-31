from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/jungko5631/genealogie/genealogie.db'
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
            print(f"Personne existe déjà : {prenom} {nom} ({date_naissance})")
            return redirect(url_for('index'))
        est_decede = False
        parent1_id = request.form.get('parent1_id') or None
        parent2_id = request.form.get('parent2_id') or None
        personne = Personne(prenom=prenom, nom=nom, date_naissance=date_naissance, 
                           est_decede=est_decede, parent1_id=parent1_id, parent2_id=parent2_id)
        db.session.add(personne)
        db.session.commit()
        print(f"Ajouté : {prenom} {nom} ({date_naissance}), Décédé : {est_decede}")
        return redirect(url_for('index'))
    
    personnes = Personne.query.all()
    print(f"Nombre de personnes récupérées : {len(personnes)}")
    for p in personnes:
        print(f"- {p.id}: {p.prenom} {p.nom} ({p.date_naissance}), Décédé : {p.est_decede}")
    return render_template('index.html', personnes=personnes)

@app.route('/decede/<int:index>')
def marquer_decede(index):
    personne = Personne.query.get_or_404(index)
    personne.est_decede = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    personne = Personne.query.get_or_404(index)
    if request.method == 'POST':
        personne.parent1_id = request.form.get('parent1_id') or None
        personne.parent2_id = request.form.get('parent2_id') or None
        db.session.commit()
        print(f"Parents mis à jour pour {personne.prenom} {personne.nom}")
        return redirect(url_for('index'))
    personnes = Personne.query.all()
    return render_template('edit.html', personne=personne, personnes=personnes)

@app.route('/supprimer/<int:index>')
def supprimer(index):
    personne = Personne.query.get_or_404(index)
    print(f"Suppression : {personne.prenom} {personne.nom} ({personne.date_naissance})")
    db.session.delete(personne)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/arbre')
def arbre():
    personnes = Personne.query.all()
    # Nœud racine pour le couple
    roland = Personne.query.get(2)  # ID 2
    josiane = Personne.query.get(3)  # ID 3
    arbre_data = {
        'name': f"{roland.prenom} {roland.nom} & {josiane.prenom} {josiane.nom}",
        'children': []
    }
    # Ajouter tous les enfants liés à Roland ou Josiane
    enfants_vus = set()
    for parent in [roland, josiane]:
        enfants = parent.enfants_parent1 + parent.enfants_parent2
        for enfant in enfants:
            if enfant.id not in enfants_vus:
                arbre_data['children'].append({
                    'name': f"{enfant.prenom} {enfant.nom} ({enfant.date_naissance})",
                    'children': []  # Préparer pour d'autres niveaux si besoin
                })
                enfants_vus.add(enfant.id)
                print(f"Ajouté enfant à l'arbre : {enfant.prenom} {enfant.nom} ({enfant.date_naissance})")
    return render_template('arbre.html', arbre_data=arbre_data)

if __name__ == '__main__':
    app.run(debug=True)
