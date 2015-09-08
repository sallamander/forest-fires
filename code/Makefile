makefiles/year_list.pkl: makefiles/make_year_list.py
	python makefiles/make_year_list.py

psql_dts: makefiles/year_list.pkl 
	python data_work/create_postgres_dts.py makefiles/year_list.pkl

merged_psql_sentinal: makefiles/year_list.pkl
	python data_work/merged_shapfiles_dts.py makefiles/year_list.pkl

cleaned_psql_sentinal: makefiles/year_list.pkl 
	python data_work/clean_merged_dts.py makefiles/year_list.pkl

csvs_jsons_sentinal: makefiles/year_list.pkl 
	python data_work/create_csvs_jsons.py makefiles/create_csvs_jsons.py

new_year_data: makefiles/year_list.pkl
	python data_work/create_postgres_dts.py makefiles/year_list.pkl
	python data_work/merged_shapfiles_dts.py makefiles/year_list.pkl
	python data_work/clean_merged_dts.py makefiles/year_list.pkl
	python data_work/create_csvs_jsons.py makefiles/create_csvs_jsons.py
