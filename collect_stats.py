import sys
import csv
import re
import pprint

season_data = None

class Referee:
    def __init__(self, id, sexe, grades, actives):
        self.id = id
        self.sexe = sexe
        self.grades = grades
        self.actives = actives

class SeasonData:
    def __init__(self, seasons, yr_to_col):
        self.seasons = seasons
        self.yr_to_col = yr_to_col

def get_season_data(header):
    seasons = []
    seasons_yr_to_col = {}
    current_col = 0
    for season in header:
        if re.match("20\d\d", season):
            seasons.append(season)
            seasons_yr_to_col[season] = current_col
            current_col = current_col + 1
    return SeasonData(seasons, seasons_yr_to_col)

all_grades=[
    'Prov B','Prov A','Nat C','Nat B','Nat A','3-Conf','2-Cont','1-Int'
    ]
def parse_grade(grade):
    try:
        if grade.endswith('-I'):
            grade = grade[:-2]
        return all_grades.index(grade)
    except ValueError:
        return -1

def unparse_grade(grade_id):
    if grade_id == -1:
        return ''
    return all_grades[grade_id]

def parse_active(grade):
    if not grade or grade.endswith('-I'):
        return False
    else:
        return True

def pred_m():
    return lambda ref: ref.sexe == 'M'

def pred_f():
    return lambda ref: ref.sexe == 'F'

def pred_active_in_yr(yr):
    global season_data
    return lambda ref: ref.actives[season_data.yr_to_col[yr]]

def compute_max_grade_stats(refs):
    for ref in refs:
        max_grade = max(ref.grades)

def print_summary_stats(refs, yr):
    refs_in_yr = list(filter(pred_active_in_yr(yr), refs))
    print("%s: %s M, %s F, %s total" %
          (yr,
           len(list(filter(pred_m(), refs_in_yr))),
           len(list(filter(pred_f(), refs_in_yr))),
           len(refs_in_yr)))
        
def main():
    global season_data
    if len(sys.argv) < 2:
        print ("syntax:", sys.argv[0], "infile")
        sys.exit(1)
        
    input_file = sys.argv[1]
    refs = []

    with open(input_file) as csvfile:
        reader = csv.reader(csvfile)

        header = reader.__next__()
        season_data = get_season_data(header)

        for row in reader:
            raw_seasons = row[2:]
            grades = []
            actives = []
            for s in season_data.seasons:
                grades.append(parse_grade(raw_seasons[season_data.yr_to_col[s]]))
                actives.append(parse_active(raw_seasons[season_data.yr_to_col[s]]))
            ref = Referee(int(row[0]), row[1], grades, actives)
            refs.append(ref)

    print_summary_stats(refs, "2011")

    refs_2019 = filter(pred_active_in_yr("2019"), refs)
    compute_max_grade_stats(refs_2019)

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(items[165].grades)
    # pp.pprint(items[165].actives)

if __name__ == "__main__":
    main()
