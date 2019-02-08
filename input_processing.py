import requests
from Bio import SeqIO
import os


def obtain_sequence_from_uniprot(uniprot_id):

    r = requests.get('https://www.uniprot.org/uniprot/'+uniprot_id+'.fasta')

    if(r.status_code == 200):

        fp = open(uniprot_id+'.fasta', 'w')
        fp.write(r.text)
        fp.close()

        seq = SeqIO.read(uniprot_id+'.fasta', "fasta")
        os.remove(uniprot_id+'.fasta')
        return seq.seq

    else:

        return 'error'


def parse_fasta(fasta_in):

    cnt = 0

    while True:

        if(not os.path.exists(str(cnt)+'.fasta')):
            break

        cnt += 1

    fp = open(str(cnt)+'.fasta', 'w')
    fp.write(fasta_in)
    fp.close()

    seq = SeqIO.read(str(cnt)+'.fasta', "fasta")
    os.remove(str(cnt)+'.fasta')
    print(seq)
    return seq.seq


def parse_file(filey):

    try:
        seq = SeqIO.read(filey, "fasta")
        os.remove(filey)
        return seq.seq

    except Exception as e:
        print(e)
        os.remove(filey)
        return 'error'


if __name__ == '__main__':

    parse_fasta('>tr\nMFL')
