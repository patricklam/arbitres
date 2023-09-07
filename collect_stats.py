import sys
import csv
import re
import pprint
from collections import defaultdict

season_data = None

class Referee:
    def __init__(self, id, sexe, grades, actives):
        self.id = id
        self.sexe = sexe
        self.grades = grades
        self.actives = actives
    def first_season(self): # chronologically earliest
        return max(idx for idx, flag in enumerate(self.actives) if flag)
    def last_season(self): # chronologically latest
        return min(idx for idx, flag in enumerate(self.actives) if flag)
    def is_active_in_yr(self, yr):
        global season_data
        return self.actives[season_data.yr_to_col[yr]]

class SeasonData:
    def __init__(self, seasons, yr_to_col):
        self.seasons = seasons
        self.yr_to_col = yr_to_col
        self.adjacent_year_pairs = self.compute_adjacent_year_pairs()
    def compute_adjacent_year_pairs(self):
        pairs = []
        prev_season = -1
        for season in self.seasons:
            s = int(season)
            if prev_season - 1 == s:
                pairs.append((str(s), str(prev_season)))
            prev_season = s
        return pairs        
            
## utilities
def get_ref_by_id(refs, id):
    for ref in refs:
        if id == ref.id:
            return ref
    return None

def initialize_season_data(header):
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

## computations
        
def print_summary_stats(refs, yr):
    refs_in_yr = list(filter(pred_active_in_yr(yr), refs))
    print("%s: %s M, %s F, %s total" %
          (yr,
           len(list(filter(pred_m(), refs_in_yr))),
           len(list(filter(pred_f(), refs_in_yr))),
           len(refs_in_yr)))

def print_summary_stats_multiyear(refs):
    years = ['2001', '2011', '2021', '2023']
    for year in years:
        print_summary_stats(refs, year)

def print_summary_stats_allyears(refs):
    global season_data
    for year in season_data.seasons:
        print_summary_stats(refs, year)

def print_max_grade_stats(refs):
    global all_grades
    grades = defaultdict(lambda: 0)
    for ref in refs:
        max_grade = max(ref.grades)
        grades[max_grade] += 1

    total = 0
    for idx, grade in enumerate(all_grades):
        total += grades[idx]

    for idx, grade in enumerate(all_grades):
        print("%6s: %2s (%d%%)" % (grade, grades[idx], float(100*grades[idx])/total))
    print(" Total: %s" % total)
        
def print_joining_and_leaving(refs):
    global season_data
    left_at = defaultdict(lambda: 0)
    joined_at = defaultdict(lambda: 0)
    joiners = 0
    leavers = 0

    print ("Number of referees joining/leaving the roster between each season:")
    for (n,npp) in season_data.adjacent_year_pairs:
        n_season = season_data.yr_to_col[n]
        npp_season = season_data.yr_to_col[npp]
        active_in_n = list(filter(pred_active_in_yr(n), refs))
        active_in_npp = list(filter(pred_active_in_yr(npp), refs))
        ids_in_yr_n = set(map(lambda x: x.id, filter(pred_active_in_yr(n), refs)))
        ids_in_yr_npp = set(map(lambda x: x.id, filter(pred_active_in_yr(npp), refs)))
        ids_in_yr_n_but_not_npp = sorted(list(ids_in_yr_n - ids_in_yr_npp)) # left in N+1
        ids_in_yr_npp_but_not_n = sorted(list(ids_in_yr_npp - ids_in_yr_n)) # joined in N+1

        for leaver_id in ids_in_yr_n_but_not_npp:
            leaver = get_ref_by_id(refs, leaver_id)
            # is only a leaver if never appears in any season after n
            # print ("leaver %i, n is %s, last season is %i" % (leaver_id,n_season,leaver.last_season()))
            if leaver.last_season() == n_season:
                leaver_grade = max(leaver.grades)
                left_at[leaver_grade] += 1
                leavers += 1

        for joiner_id in ids_in_yr_npp_but_not_n:
            joiner = get_ref_by_id(refs, joiner_id)
            # is only a joiner if never appears in any season before npp
            # print ("joiner %i, npp is %s, first season is %i" % (joiner_id,npp_season,joiner.first_season()))
            if joiner.first_season() == npp_season:
                joiner_grade = min(filter(lambda x: x >= 0, joiner.grades))
                joined_at[joiner_grade] += 1
                joiners += 1

        print ("%s(%s) to %s(%s), +%s -%s" % (n, len(active_in_n), npp, len(active_in_npp), len(ids_in_yr_npp_but_not_n), len(ids_in_yr_n_but_not_npp)))

    print ("\nGrades at which referees joined/left the roster:")
    for idx, grade in enumerate(all_grades):
        print("%6s: joined %2s, left %2s" % (grade, joined_at[idx], left_at[idx]))
    print(" Total: joined %s, left %s" % (joiners, leavers))

def print_probabilities_per_referee_grade(refs):
    global all_grades, season_data
    print ("Annual probability of continuing/not continuing/being promoted, by referee grade")
    for grade_idx, grade in enumerate(all_grades):
        total_events = 0
        continue_events = 0
        promotion_events = 0
        for (n,npp) in season_data.adjacent_year_pairs:
            n_col = season_data.yr_to_col[n]
            npp_col = season_data.yr_to_col[npp]
            for ref in refs:
                # if a referee is active at grade g at season n,
                # 1) are they active the next season?
                # 2) are they still at the same grade?
                if ref.is_active_in_yr(n) and ref.grades[n_col] == grade_idx:
                    total_events += 1
                    if ref.is_active_in_yr(npp):
                        continue_events += 1
                    if ref.grades[n_col] < ref.grades[npp_col]:
                        promotion_events += 1
        expected_promotion_time = "{:.1f}".format(total_events/promotion_events) if promotion_events > 0 else "---"
        print("grade {:7s}: total events {:3}, continue {:.0%}, non-continue {:.0%} (E(1/n): {:.1f}), promote {:.0%} (E(1/n): {})".format(grade, total_events, continue_events/total_events, 1-(continue_events/total_events), 1/(1-(continue_events/total_events)), promotion_events/total_events, expected_promotion_time))

def levels_joining_and_leaving(refs):
    pass
    # for every adjacent year pair, record the level of new refs/departed refs

        # next question: what level do refs join and leave at?
        # maybe collect this across all years: "x Prov B refs join, y Nat A refs leave"
        
## main
        
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
        season_data = initialize_season_data(header)

        for row in reader:
            raw_seasons = row[2:]
            grades = []
            actives = []
            for s in season_data.seasons:
                grades.append(parse_grade(raw_seasons[season_data.yr_to_col[s]]))
                actives.append(parse_active(raw_seasons[season_data.yr_to_col[s]]))
            ref = Referee(int(row[0]), row[1], grades, actives)
            refs.append(ref)

    #print_summary_stats_allyears(refs)
    #print_max_grade_stats(refs)
    #print_joining_and_leaving(refs)
    print_probabilities_per_referee_grade(refs)            

    #refs_2019 = filter(pred_active_in_yr("2019"), refs)
    #compute_max_grade_stats(refs_2019)

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(items[165].grades)
    # pp.pprint(items[165].actives)

if __name__ == "__main__":
    main()
