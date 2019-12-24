import pandas as pd
import untangle

def get_data_labels(url):
    obj = untangle.parse(url)
    data = obj.codeBook.dataDscr.var
    labels = {
        x['ID']: {
            int(el.catValu.cdata): el.labl.cdata
            for el in x.catgry
        }
        for x in data
        if getattr(x, 'catgry', None)
    }
    return labels

def get_working_population_data():
    url = "gameplan/growth/raw_data/data_labels.xml"
    data_labels = get_data_labels(url)
    ipums = pd.read_csv("gameplan/growth/raw_data/asec_data.csv")

    for k, v in data_labels.items():
        ipums[k.lower()] = ipums[k].replace(v)

    ipums['inctot'] = ipums['INCTOT'].clip(lower=0)

    working_pop = ipums.query("AGE.between(22, 65) & WKSWORK1 >= 40 & fullpart == 'Full-time'")

    return working_pop

def get_cohort_data(age, metro_area='', age_window=2):
    working_pop = get_working_population_data()
    cohort = working_pop[
        working_pop['AGE'].between(age - age_window, age + age_window)
        & working_pop['metarea'].str.contains(metro_area)
    ]
    return cohort
