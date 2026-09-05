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
obs-up:
	podman compose -f deploy/observability/docker-compose.observability.yml up -d
obs-down:
	podman compose -f deploy/observability/docker-compose.observability.yml down
obs-clean:
	podman compose -f deploy/observability/docker-compose.observability.yml down -v
obs-logs:
	podman compose -f deploy/observability/docker-compose.observability.yml logs -f
dev-all:
	podman compose -f deploy/observability/docker-compose.observability.yml up -d
	podman compose up --build
restart:
	podman compose down
	podman compose -f deploy/observability/docker-compose.observability.yml down
	podman compose -f deploy/observability/docker-compose.observability.yml up -d
	podman compose up --build
