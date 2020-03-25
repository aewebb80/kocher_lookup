import os
import sys
import sqlite3

from Bio import SeqIO 
from collections import defaultdict

def createTables (cursor):

	try:

		tables_to_create = ['CREATE TABLE "Genes" ("Gene_ID" TEXT, "Transcript_IDs" TEXT NOT NULL, "Ortholog_ID" TEXT, PRIMARY KEY("Gene_ID"))',
							'CREATE TABLE "Orthologs" ("Ortholog_ID" TEXT,"Transcript_IDs" TEXT NOT NULL, PRIMARY KEY("Ortholog_ID"))',
							'CREATE TABLE "Protein" ("Transcript_ID" TEXT, "Sequence" BLOB NOT NULL, PRIMARY KEY("Transcript_ID") )',
							'CREATE TABLE "mRNA" ("Transcript_ID" TEXT, "Sequence" BLOB NOT NULL, PRIMARY KEY("Transcript_ID") )']

		for table_to_create in tables_to_create:

			# Execute the insert values command
			cursor.execute(table_to_create)

	except sqlite3.Error as error:
		raise Exception(error)

def addSequence (cursor, table, transcript_ID, fasta_sequence):

	try:

		# Create the insert string
		sqlite_insert_values = 'INSERT INTO %s (Transcript_ID, Sequence) VALUES (?, ?)' % table

		# Convert the sequence to binary
		fasta_sequence = sqlite3.Binary(fasta_sequence.encode())

		# Execute the insert values command
		cursor.execute(sqlite_insert_values, (transcript_ID, fasta_sequence))

	except sqlite3.Error as error:
		raise Exception(error)

def addGene (cursor, gene_ID, transcript_IDs):

	try:

		# Create the insert string
		sqlite_insert_values = 'INSERT INTO Genes (Gene_ID, Transcript_IDs) VALUES (?, ?)'

		# Execute the insert values command
		cursor.execute(sqlite_insert_values, (gene_ID, transcript_IDs))

	except sqlite3.Error as error:
		raise Exception(error)

def addGeneOrtho (cursor, gene_ID, transcript_IDs, ortholog_ID):

	try:

		# Create the insert string
		sqlite_insert_values = 'INSERT INTO Genes (Gene_ID, Transcript_IDs, Ortholog_ID) VALUES (?, ?, ?)'

		# Execute the insert values command
		cursor.execute(sqlite_insert_values, (gene_ID, transcript_IDs, ortholog_ID))

	except sqlite3.Error as error:
		raise Exception(error)

def addOrtholog (cursor, ortholog_ID, transcript_IDs):

	try:

		# Create the insert string
		sqlite_insert_values = 'INSERT INTO Orthologs (Ortholog_ID, Transcript_IDs) VALUES (?, ?)'

		# Execute the insert values command
		cursor.execute(sqlite_insert_values, (ortholog_ID, transcript_IDs))

	except sqlite3.Error as error:
		raise Exception(error)

# Connect to the sqlite database
sqlite_connection = sqlite3.connect('SequenceDB.sqlite')

# Create the cursor
cursor = sqlite_connection.cursor()

createTables(cursor)

# Create dict to store the ortholog group for a transcript
transcript_to_ortholog = {}

# Loop the files within the ortholog directory 
for ortholog_file in os.listdir(sys.argv[2]):

	# Assign the ortholog ID, from the filename
	ortholog_ID = os.path.splitext(ortholog_file)[0].replace('og_cds_', 'OG_')

	# Create list to store the orthologs
	orthologous_transcript_list = []

	# Read the ortholog file
	for record in SeqIO.parse(os.path.join(sys.argv[2], ortholog_file), "fasta"):

		# Remove if the other genomes are found
		if '-R' not in record.id:
			continue

		# Append the ID
		orthologous_transcript_list.append(record.id)

		# Assign the ortholog group to the current gene
		transcript_to_ortholog[record.id] = ortholog_ID

	# Save the IDs as a string
	orthologous_transcripts = ', '.join(orthologous_transcript_list)

	# Add the ortholog
	addOrtholog (cursor, ortholog_ID, orthologous_transcripts)

# Walk the Assembly directory
for root, dirs, files in os.walk(sys.argv[1]):

	# Loop the Assembly files
	for name in files:

		if '_trans.fasta' in name:

			# Create an ID dict
			id_dict = defaultdict(list)

			# Loop the sequence
			for record in SeqIO.parse(os.path.join(root, name), "fasta"):

				# Assign the gene ID
				record_gene_id = record.id.split('-')[0]

				# Add the gene ID and transcript ID to the dict
				id_dict[record_gene_id].append(record.id)

			# Open the file as an index
			record_index = SeqIO.index(os.path.join(root, name), "fasta")

			# Loop the dict by gene
			for gene_ID, transcript_IDs in id_dict.items():

				# Loop the transcripts
				for transcript_ID in transcript_IDs:

					# Add the sequence to the database 
					addSequence(cursor, 'mRNA', transcript_ID, record_index[transcript_ID].format("fasta"))

		if '_pep.fasta' in name:

			# Create an ID dict
			id_dict = defaultdict(list)

			# Loop the sequence
			for record in SeqIO.parse(os.path.join(root, name), "fasta"):

				# Assign the gene ID
				record_gene_id = record.id.split('-')[0]

				# Add the gene ID and transcript ID to the dict
				id_dict[record_gene_id].append(record.id)

			# Open the file as an index
			record_index = SeqIO.index(os.path.join(root, name), "fasta")

			# Loop the dict by gene
			for gene_ID, transcript_IDs in id_dict.items():

				# Assign the IDs as a string
				transcript_IDs_str = ', '.join(transcript_IDs)

				# Create a string to store the ortholog
				gene_ortholog = ''

				# Loop the transcripts
				for transcript_ID in transcript_IDs:

					# Add the sequence to the database 
					addSequence(cursor, 'Protein', transcript_ID, record_index[transcript_ID].format("fasta"))

					# Check if the current ID is within the genes to ortholog dict
					if transcript_ID in transcript_to_ortholog:

						# Assign the ortholog 
						gene_ortholog = transcript_to_ortholog[transcript_ID]

				# Check if an ortholog was found
				if gene_ortholog:

					# Add the gene, with an ortholog
					addGeneOrtho(cursor, gene_ID, transcript_IDs_str, gene_ortholog)
				
				else:

					# Add the gene, without an ortholog
					addGene(cursor, gene_ID, transcript_IDs_str)

# Commit any changes
sqlite_connection.commit()

# Close the connection
cursor.close()




