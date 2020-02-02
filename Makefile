install: create_env
	npm install
	pip install -r requirements.txt

deploy: ensure_env_file
	npx sls deploy --stage dev

deploy_prod: ensure_env_file
	npx sls deploy --stage prod

ensure_env_file:
	if ! test -f ".env"; then \
		cp .env.template .env; \
	fi

create_env: install_pyenv
	if ! pyenv local; then \
		pyenv virtualenv 3.8.1 lambda-ftp-to-gsheet-transform; \
		pyenv local lambda-ftp-to-gsheet-transform; \
	fi

install_pyenv:
	if ! [ -x "$$(command -v pyenv)" ]; then \
  		curl https://pyenv.run | bash; \
	fi
