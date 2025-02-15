import sys
import csv
import re
import pprint
from collections import defaultdict

season_data = None

class Referee:
    def __init__(self, id, sexe, grades, actives, ddn):
        self.id = id
        self.sexe = sexe
        self.grades = grades
        self.actives = actives
        self.ddn = ddn
    def earliest_season(self): # chronologically earliest
        return max(idx for idx, flag in enumerate(self.actives) if flag)
    def latest_season(self): # chronologically latest
        return min(idx for idx, flag in enumerate(self.actives) if flag)
    def is_active_in_yr(self, yr):
        global season_data
        return self.actives[season_data.yr_to_col[yr]]

class SeasonData:
    def __init__(self, seasons, yr_to_col, col_to_yr):
        self.seasons = seasons
        self.yr_to_col = yr_to_col
        self.col_to_yr = col_to_yr
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
    global ddn_col
    seasons = []
    seasons_yr_to_col = {}
    seasons_col_to_yr = {}
    current_col = 0
    for season in header:
        if season == "année de naissance":
            ddn_col = current_col + 1
        if re.match(r"20\d\d", season):
            seasons.append(season)
            seasons_yr_to_col[season] = current_col
            seasons_col_to_yr[current_col] = season
            current_col = current_col + 1
    return SeasonData(seasons, seasons_yr_to_col, seasons_col_to_yr)

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
    m = len(list(filter(pred_m(), refs_in_yr)))
    f = len(list(filter(pred_f(), refs_in_yr)))
    print("%s: %s M, %s F, %s total, %.0f%% F" %
          (yr,
           m,
           f,
           len(refs_in_yr),
           f/(m+f)*100
          ))

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
            # print ("leaver %i, n is %s, last season is %i" % (leaver_id,n_season,leaver.latest_season()))
            if leaver.latest_season() == n_season:
                leaver_grade = max(leaver.grades)
                left_at[leaver_grade] += 1
                leavers += 1

        for joiner_id in ids_in_yr_npp_but_not_n:
            joiner = get_ref_by_id(refs, joiner_id)
            # is only a joiner if never appears in any season before npp
            # print ("joiner %i, npp is %s, first season is %i" % (joiner_id,npp_season,joiner.earliest_season()))
            if joiner.earliest_season() == npp_season:
                joiner_grade = min(filter(lambda x: x >= 0, joiner.grades))
                joined_at[joiner_grade] += 1
                joiners += 1

        print ("%s(%s) to %s(%s), +%s -%s" % (n, len(active_in_n), npp, len(active_in_npp), len(ids_in_yr_npp_but_not_n), len(ids_in_yr_n_but_not_npp)))

    print ("\nGrades at which referees joined/left the roster:")
    for idx, grade in enumerate(all_grades):
        print("%6s: joined %2s, left %2s" % (grade, joined_at[idx], left_at[idx]))
    print(" Total: joined %s, left %s" % (joiners, leavers))

def print_leaving_age(refs):
    global season_data
    left_at = defaultdict(lambda: 0)
    joined_at = defaultdict(lambda: 0)
    joiners = 0
    leavers = 0

    print ("id,grade,age")
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
            if leaver.latest_season() == n_season and leaver.ddn != 0:
                leaver_grade = max(leaver.grades)
                print ("%i,%s,%d" %
                       (leaver_id,
                        unparse_grade(leaver_grade),
                        int(n) - leaver.ddn))
                
                left_at[leaver_grade] += 1
                leavers += 1


        #print ("%s(%s) to %s(%s), +%s -%s" % (n, len(active_in_n), npp, len(active_in_npp), len(ids_in_yr_npp_but_not_n), len(ids_in_yr_n_but_not_npp)))

    #print ("\nGrades at which referees joined/left the roster:")
    #for idx, grade in enumerate(all_grades):
    #    print("%6s: joined %2s, left %2s" % (grade, joined_at[idx], left_at[idx]))
    #print(" Total: joined %s, left %s" % (joiners, leavers))

def print_probabilities_per_referee_grade(refs, sexe):
    global all_grades, season_data
    print ("Annual probability of continuing/not continuing/being promoted, by referee grade, for sexe '{}'".format(sexe))
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
                    if sexe != "" and ref.sexe != sexe:
                        continue
                    total_events += 1
                    if ref.is_active_in_yr(npp):
                        continue_events += 1
                    if ref.grades[n_col] < ref.grades[npp_col]:
                        promotion_events += 1
        expected_promotion_time_string = "{:.1f}".format(total_events/promotion_events) if promotion_events > 0 else "---"
        expected_lifetime_string = "{:.1f}".format(1/(1-(continue_events/total_events))) if 1-(continue_events/total_events) > 0 else "--"
        print("grade {:7s}: total events {:3}, continue {:.0%}, non-continue {:.0%} (E(1/n): {}), promote {:.0%} (E(1/n): {})".format(grade, total_events, continue_events/total_events, 1-(continue_events/total_events), expected_lifetime_string, promotion_events/total_events, expected_promotion_time_string))

def print_time_to_nat_a(refs, lower, upper):
    count = 0
    sum = 0
    from_prov_B = 0
    for ref in refs:
        if max(ref.grades) >= parse_grade('Nat A'):
            # find first season that this ref was at least nat A, which is last in the list
            first_nat_a = max(idx for idx, grade in enumerate(ref.grades) if grade >= parse_grade('Nat A'))
            earliest_season = ref.earliest_season()
            first_grade = ref.grades[earliest_season]
            first_nat_a_yr = int(season_data.col_to_yr[first_nat_a])
            earliest_season_yr = int(season_data.col_to_yr[earliest_season])

            if first_nat_a_yr < lower or first_nat_a_yr > upper:
                continue

            if first_grade <= parse_grade('Prov A'):
                if first_grade == parse_grade('Prov B'):
                    from_prov_B = from_prov_B + 1
                count = count + 1
                sum = sum + (first_nat_a_yr - earliest_season_yr)
                print ("{} {} {} ({} years) {}".format(ref.id,
                                                       first_nat_a_yr,
                                                       earliest_season_yr,
                                                       first_nat_a_yr - earliest_season_yr,
                                                       unparse_grade(first_grade)))
    print ("Count: {}; from-prov-B: {}; average number of years: {}".format
           (count, from_prov_B, sum/count))

def print_probability_to_nat_a(refs):
    count = 0
    attained_nat_a = 0
    for ref in refs:
        if min(ref.grades) <= parse_grade('Prov A'):
        #if parse_grade('Prov A') in ref.grades:
            count = count + 1
            if max(ref.grades) >= parse_grade('Nat A'):
                attained_nat_a = attained_nat_a + 1
    print ("Count: {}; attained Nat A: {}".format
           (count, attained_nat_a))
    
def print_time_nat_a_to_continental(refs):
    count = 0
    sum = 0
    for ref in refs:
        if max(ref.grades) >= parse_grade('2-Cont'):
            # find first season that this ref was at least nat A, which is last in the list
            first_nat_a = max(idx for idx, grade in enumerate(ref.grades) if grade >= parse_grade('Nat A'))
            first_cont = max(idx for idx, grade in enumerate(ref.grades) if grade >= parse_grade('2-Cont'))
            first_nat_a_yr = int(season_data.col_to_yr[first_nat_a])
            first_cont_yr = int(season_data.col_to_yr[first_cont])
            if first_cont_yr != first_nat_a_yr:
                print ("{} {} {} {}".format(ref.id,
                                                    first_nat_a_yr,
                                                    first_cont_yr,
                                                    first_cont_yr - first_nat_a_yr))
    
## main
        
def main():
    global season_data, ddn_col
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
            ddn = raw_seasons[ddn_col]
            grades = []
            actives = []
            for s in season_data.seasons:
                grades.append(parse_grade(raw_seasons[season_data.yr_to_col[s]]))
                actives.append(parse_active(raw_seasons[season_data.yr_to_col[s]]))
            ref = Referee(int(row[0]), row[1], grades, actives,
                          int(ddn) if ddn != "" else 0)
            refs.append(ref)

    #print_summary_stats_allyears(refs)
    #print_max_grade_stats(refs)
    #print_joining_and_leaving(refs)
    #print_leaving_age(refs)
    #print_probabilities_per_referee_grade(refs, "")
    print_probabilities_per_referee_grade(refs, "F")
    #print_time_to_nat_a(refs, 0, 9999)
    #print_time_nat_a_to_continental(refs)
    #print_time_to_nat_a(refs, 0, 2011)
    #print_time_to_nat_a(refs, 2011, 9999)
    #print_probability_to_nat_a(refs)

    # how to filter on a year
    #refs_2019 = filter(pred_active_in_yr("2019"), refs)
    #compute_max_grade_stats(refs_2019)

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(items[165].grades)
    # pp.pprint(items[165].actives)

if __name__ == "__main__":
    main()
