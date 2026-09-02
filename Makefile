dev:
	 podman compose up --build
build:
	 podman compose build
test:
	 pytest backend/tests
seed:
	 cd backend && python -m scripts.seed
lint:
	 python -m compileall backend/app