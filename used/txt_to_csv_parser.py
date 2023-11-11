import csv

# same script is used for the CPUs.
with open("gpus.txt", "r+") as f:
    dict_item_to_score = []

    for line in f.readlines():
        line = line.split('\t')
        dict_item_to_score.append({'Part': line[0], 'Score': int(line[1].strip())})

    with open("gpus.csv", "w+", newline='') as csv_file:
        field_names = ['Part', 'Score']
        csv_writer = csv.DictWriter(csv_file,fieldnames=field_names , delimiter=',')

        for k in dict_item_to_score:
            print(k)
            csv_writer.writerow(k)