from searchers.clinical_trials_searcher import ClinicalTrialsSearcher

ctsearcher = ClinicalTrialsSearcher()

df = ctsearcher.search_and_load_df('resmed')

print(df.head())