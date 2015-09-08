makefiles/year_list.pkl: makefiles/make_year_list.py
	python makefiles/make_year_list.py

.psql_dts_sentinal: 
	touch .psql_dts_sentinal

.merged_psql_sentinal: 
	touch .merged_psql_sentinal

.cleaned_psql_sentinal: 
	touch .cleaned_psql_sentinal

.csvs_jsons_sentinal: 
	touch .csvs_jsons_sentinal

psql_dts: makefiles/year_list.pkl .psql_dts_sentinal
	python data_work/create_postgres_dts.py makefiles/year_list.pkl

merged_psql: makefiles/year_list.pkl .merged_psql_sentinal
	python data_work/merge_shapefile_dts.py makefiles/year_list.pkl

cleaned_psql: makefiles/year_list.pkl .cleaned_psql_sentinal
	python data_work/clean_merged_dts.py makefiles/year_list.pkl

csvs_jsons: makefiles/year_list.pkl .csvs_jsons_sentinal
	python data_work/create_csvs_jsons.py makefiles/year_list.pkl

setup_data: makefiles/year_list.pkl
	python data_work/create_postgres_dts.py makefiles/year_list.pkl
	python data_work/merge_shapefile_dts.py makefiles/year_list.pkl
	python data_work/clean_merged_dts.py makefiles/year_list.pkl
	python data_work/create_csvs_jsons.py makefiles/year_list.pkl
