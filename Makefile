.PHONY: clean deploy

deploy:
	docker compose up --build --detach

clean:
	docker compose down --volumes --remove-orphans
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name node_modules -prune -exec rm -rf {} +
	rm -rf frontend/dist
	rm -f db.sqlite3 backend/db.sqlite3
