# Add Path

On a Mac you need to add the path to waiver_coach git repo to your path so that you can import it in python.

	export PYTHONPATH="${PYTHONPATH}:mypathto/waiver_coach/"

For me it's

	export PYTHONPATH="${PYTHONPATH}:/Users/rossboberg/Documents/MIDS/capstone/waiver_coach/"

# Folders
`data\` saves pickled pipelines and data for quick loading

`feature_extraction\` has files for feature extraction

`nfldb_helpers\` has helper functions for getting data & info from nfldb postgres

`prediction\` has functions for acctually making predictions (tying to gether data, feature extraction, etc)

`results\` houses results of predictions
