from flask import Flask, Response, abort, redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

# Create the Flask application
app = Flask(__name__)

# Config the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SequenceDB.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Start the database
db = SQLAlchemy(app)

# Get metadata for the table
db.Model.metadata.reflect(db.engine)

# Create the link table model
class Sequence ():
	def __init__ (self, transcript_id, sequence):
		self.Transcript_ID = transcript_id
		self.Sequence = sequence

	def __str__(self):
		return str(self.Sequence)

# Create the link table model
class Genes (db.Model):
	__tablename__ = 'Genes'
	__table_args__ = { 'extend_existing': True }
	Gene_ID = db.Column(db.Text, primary_key=True)

# Create the mRNA table model
class mRNA (db.Model):
	__tablename__ = 'mRNA'
	__table_args__ = { 'extend_existing': True }
	Transcript_ID = db.Column(db.Text, primary_key=True)

# Create the protein table model
class Protein (db.Model):
	__tablename__ = 'Protein'
	__table_args__ = { 'extend_existing': True }
	Transcript_ID = db.Column(db.Text, primary_key=True)

# Create the protein table model
class Orthologs (db.Model):
	__tablename__ = 'Orthologs'
	__table_args__ = { 'extend_existing': True }
	Ortholog_ID = db.Column(db.Text, primary_key=True)

@app.route("/")
def index ():

	# Render the index
	return render_template("index.html")

@app.route('/gene/<gene_id>')
def gene (gene_id):

	# Render the webpage
	return render_template("gene.html", Gene_ID = gene_id)

@app.route('/mrna-lookup/<gene_id>')
def mrnaLookup(gene_id):

	# Get the gene data from the database
	gene_data = Genes.query.filter_by(Gene_ID=gene_id).first()

	# Convert the transcript_ids into a list
	transcript_IDs = gene_data.Transcript_IDs.split(', ')

	# Check if anything was returned
	if not gene_data:
		return redirect(url_for('mrnaMissing', gene_id = gene_id))

	# Create a list to store the transcript information
	transcript_mRNAs = []

	# Loop the transcripts
	for transcript_ID in transcript_IDs:

		# Get the transcript data from the database
		mRNA_data = mRNA.query.filter_by(Transcript_ID=transcript_ID).first()

		# Assign the new sequence object
		transcript_mRNA = Sequence(mRNA_data.Transcript_ID, mRNA_data.Sequence.decode())

		# Add the mRNA data to the list
		transcript_mRNAs.append(transcript_mRNA)

	# Check if anything was returned
	if not transcript_mRNAs:
		return redirect(url_for('mrnaMissing', Gene_ID = gene_id))

	# Render the webpage
	return render_template("mrna-lookup.html", Gene_ID = gene_id, mRNA_data_list = transcript_mRNAs)

@app.route("/gene-mRNAFasta/<gene_id>")
def geneMRNAFasta(gene_id):

	# Get the gene data from the database
	gene_data = Genes.query.filter_by(Gene_ID=gene_id).first()

	# Convert the transcript_ids into a list
	transcript_IDs = gene_data.Transcript_IDs.split(', ')

	# Create a string to store the sequences
	sequence = ''

	# Loop the transcripts
	for transcript_ID in transcript_IDs:

		# Get the transcript data from the database
		mRNA_data = mRNA.query.filter_by(Transcript_ID=transcript_ID).first()

		# Assign the new sequence object 
		transcript_mRNA = Sequence(mRNA_data.Transcript_ID, mRNA_data.Sequence.decode())

		# Add the sequence to the string
		sequence += str(transcript_mRNA)

	# Return the mRNA as a fasta file
	return Response(sequence, mimetype="text/plain", headers={"Content-disposition":"attachment; filename=%s.fasta" % gene_id})

@app.route("/trans-mRNAFasta/<transcript_id>")
def transMRNAFasta(transcript_id):

	# Get the mRNA from the database
	mRNA_data = mRNA.query.filter_by(Transcript_ID=transcript_id).first()

	# Return the mRNA as a fasta file
	return Response(mRNA_data.Sequence, mimetype="text/plain", headers={"Content-disposition":"attachment; filename=%s.fasta" % transcript_id})

@app.route("/mrna-missing/<gene_id>")
def mrnaMissing (gene_id):
	return render_template('not-found.html', Gene_ID = gene_id, data_type = 'mRNA')

@app.route('/protein-lookup/<gene_id>')
def proteinLookup(gene_id):

	# Get the gene data from the database
	gene_data = Genes.query.filter_by(Gene_ID=gene_id).first()

	# Convert the transcript_ids into a list
	transcript_IDs = gene_data.Transcript_IDs.split(', ')

	# Check if anything was returned
	if not gene_data:
		return redirect(url_for('proteinMissing', gene_id = gene_id))

	# Create a list to store the transcript information
	transcript_AAs = []

	# Loop the transcripts
	for transcript_ID in transcript_IDs:

		# Get the protein from the database
		protein_data = Protein.query.filter_by(Transcript_ID=transcript_ID).first()

		# Assign the new sequence object
		transcript_AA = Sequence(protein_data.Transcript_ID, protein_data.Sequence.decode())

		# Add the mRNA data to the list
		transcript_AAs.append(transcript_AA)

	# Check if anything was returned
	if not transcript_AAs:
		return redirect(url_for('proteinMissing', Gene_ID = gene_id))

	# Render the webpage
	return render_template("protein-lookup.html", Gene_ID = gene_id, protein_data_list = transcript_AAs)

@app.route("/gene-proteinFasta/<gene_id>")
def geneProteinFasta(gene_id):

	# Get the gene data from the database
	gene_data = Genes.query.filter_by(Gene_ID=gene_id).first()

	# Convert the transcript_ids into a list
	transcript_IDs = gene_data.Transcript_IDs.split(', ')

	# Create a string to store the sequences
	sequence = ''

	# Loop the transcripts
	for transcript_ID in transcript_IDs:

		# Get the protein from the database
		protein_data = Protein.query.filter_by(Transcript_ID=transcript_ID).first()

		# Assign the new sequence object
		transcript_AA = Sequence(protein_data.Transcript_ID, protein_data.Sequence.decode())

		# Add the sequence to the string
		sequence += str(transcript_AA)

	# Return the protein as a fasta file
	return Response(sequence, mimetype="text/plain", headers={"Content-disposition":"attachment; filename=%s.fasta" % gene_id})

@app.route("/trans-proteinFasta/<transcript_id>")
def transProteinFasta(transcript_id):

	# Get the protein from the database
	protein_data = Protein.query.filter_by(Transcript_ID=transcript_id).first()

	# Return the protein as a fasta file
	return Response(protein_data.Sequence, mimetype="text/plain", headers={"Content-disposition":"attachment; filename=%s.fasta" % transcript_id})

@app.route("/protein-missing/<gene_id>")
def proteinMissing (gene_id):
	return render_template('not-found.html', Gene_ID = gene_id, data_type = 'Protein')

@app.route("/orthologs-lookup/<gene_id>")
def orthologLookup (gene_id):

	# Get the gene data from the database
	gene_data = Genes.query.filter_by(Gene_ID=gene_id).first()

	# Check if anything was returned
	if not gene_data or not gene_data.Ortholog_ID:
		return redirect(url_for('orthoMissing', gene_id = gene_id))

	# Get the ortholog data from the database
	ortholog_data = Orthologs.query.filter_by(Ortholog_ID=gene_data.Ortholog_ID).first()

	# Create a list to store the ortholog IDs
	ortholog_gene_IDs = []

	# Loop the transcript IDs using a split function
	for ortholog_ID in ortholog_data.Transcript_IDs.split(', '):

		# Assign the gene ID using the the transcript ID
		ortholog_transcript_data = Genes.query.filter(Genes.Transcript_IDs.contains(ortholog_ID)).first()

		# Assign the Gene ID
		ortholog_gene_ID = ortholog_transcript_data.Gene_ID

		# Check that ortholog isnt the query gene ID
		if ortholog_gene_ID == gene_id:
			continue

		# Append the ID	
		ortholog_gene_IDs.append(ortholog_gene_ID)

	# Sort the list
	ortholog_gene_IDs.sort()

	# Render the webpage
	return render_template("orthologs-lookup.html", Gene_ID = gene_id, ortholog_id_list = ortholog_gene_IDs)

@app.route("/ortho-mRNAFasta/<gene_id>")
def orthoMRNAFasta (gene_id):

	# Get the gene data from the database
	gene_data = Genes.query.filter_by(Gene_ID=gene_id).first()

	# Get the ortholog data from the database
	ortholog_data = Orthologs.query.filter_by(Ortholog_ID=gene_data.Ortholog_ID).first()

	# Conver the orthologs into a multi-line string
	transcript_IDs = ortholog_data.Transcript_IDs.split(', ')

	# Create a string to store the sequences
	sequence = ''

	# Loop the transcripts
	for transcript_ID in transcript_IDs:

		# Get the transcript data from the database
		mRNA_data = mRNA.query.filter_by(Transcript_ID=transcript_ID).first()

		# Assign the new sequence object 
		transcript_mRNA = Sequence(mRNA_data.Transcript_ID, mRNA_data.Sequence.decode())

		# Add the sequence to the string
		sequence += str(transcript_mRNA)

	# Return the protein as a fasta file
	return Response(sequence, mimetype="text/plain", headers={"Content-disposition":"attachment; filename=%s.fasta" % gene_id})

@app.route("/ortho-proteinFasta/<gene_id>")
def orthoProteinFasta (gene_id):

	# Get the gene data from the database
	gene_data = Genes.query.filter_by(Gene_ID=gene_id).first()

	# Get the ortholog data from the database
	ortholog_data = Orthologs.query.filter_by(Ortholog_ID=gene_data.Ortholog_ID).first()

	# Conver the orthologs into a multi-line string
	transcript_IDs = ortholog_data.Transcript_IDs.split(', ')

	# Create a string to store the sequences
	sequence = ''

	# Loop the transcripts
	for transcript_ID in transcript_IDs:

		# Get the protein from the database
		protein_data = Protein.query.filter_by(Transcript_ID=transcript_ID).first()

		# Assign the new sequence object
		transcript_AA = Sequence(protein_data.Transcript_ID, protein_data.Sequence.decode())

		# Add the sequence to the string
		sequence += str(transcript_AA)

	# Return the protein as a fasta file
	return Response(sequence, mimetype="text/plain", headers={"Content-disposition":"attachment; filename=%s.fasta" % gene_id})

@app.route("/ortho-missing/<gene_id>")
def orthoMissing (gene_id):
	return render_template('not-found.html', Gene_ID = gene_id, data_type = 'Orthologs')

if __name__ == '__main__':
    app.run(debug=True)