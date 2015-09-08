makefiles/year_list.pkl: makefiles/make_year_list.py
	python makefiles/make_year_list.py

./data_work/.psql_dts_sentinal: makefiles/year_list.pkl .psql_dts_sentinal
	python data_work/create_postgres_dts.py makefiles/year_list.pkl
	touch ./data_work/.psql_dts_sentinal

./data_work/.merged_psql_sentinal: makefiles/year_list.pkl ./data_work/.psql_dts_sentinal
	python data_work/merge_shapefile_dts.py makefiles/year_list.pkl
	touch ./data_work/.merged_psql_sentinal

./data_work/.cleaned_psql_sentinal: makefiles/year_list.pkl ./data_work/.merged_psql_sentinal
	python data_work/clean_merged_dts.py makefiles/year_list.pkl
	touch ./data_work/.cleaned_psql_sentinal

./data_work/.csvs_jsons_sentinal: makefiles/year_list.pkl .cleaned_psql_sentinal
	python data_work/create_csvs_jsons.py makefiles/year_list.pkl
	aws s3 cp ../data/csvs/ s3://sallamander-forest-fires --recursive
	aws s3 cp ../data/jsons s3://sallamander-forest-fires --recursive
	touch ./data_work/.csvs_jsons_sentinal

setup_data: ./data_work/.psql_dts_sentinal ./data_work/.merged_psql_sentinal \
			./data_work/.cleaned_psql_sentinal ./data_work/.csvs_jsons_sentinal
.PHONY: setup_data


	