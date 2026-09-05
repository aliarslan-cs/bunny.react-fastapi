dev:
	podman compose up --build
build:
	podman compose build
obs-up:
	podman compose -f deploy/observability/docker-compose.observability.yml up -d
obs-down:
	podman compose -f deploy/observability/docker-compose.observability.yml down
obs-logs:
	podman compose -f deploy/observability/docker-compose.observability.yml logs -f
dev-all-down: obs-down
	podman compose down
dev-all-up: dev obs-up
	@:
restart: dev-all-down dev-all-up
	@:
