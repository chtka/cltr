from searchers.clinical_trials_searcher import ClinicalTrialsSearcher
from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.isrctn_searcher import ISRCTNSearcher

ctsearcher = ClinicalTrialsSearcher()
anzsearcher = ANZCTRSearcher()
isrsearcher = ISRCTNSearcher()



df = isrsearcher.search_and_load_df('resmed')

print(df.head())



# // look into rss feeds, aws projects that already use them