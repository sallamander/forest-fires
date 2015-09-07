makefiles/year_list.pkl: makefiles/make_year_list.py
	python makefiles/make_year_list.py

./../data/.db_sentinal: makefiles/year_list.pkl
	python code/data_work/create_postgres_dts.py makefiles/year_list.pkl
	touch ./../data/.db_sentinal

all: ./../data/.db_sentinal