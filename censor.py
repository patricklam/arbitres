import sys
import csv
import pprint

if len(sys.argv) < 3:
    print ("syntax:", sys.argv[0], "infile outfile key")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]
key_file = sys.argv[3]

referee_id = 0
id2name = {}
with open(input_file) as csvfile:
    with open(output_file, 'w', newline='') as censored_csvfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(censored_csvfile)

        header = reader.__next__()
        header[0] = 'id'
        writer.writerow(header)
        
        for row in reader:
            if row[0] == "END":
                break
            id2name[referee_id] = row[0]
            row[0] = referee_id
            referee_id = referee_id + 1
            writer.writerow(row)

with open(key_file, 'w', newline='') as keyf:
    pp = pprint.PrettyPrinter(stream = keyf)
    pp.pprint(id2name)
            
