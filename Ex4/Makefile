COMPOSE = docker-compose
PROJECT_NAME = ex4

.PHONY: all clean fclean re purge-bdd purge-all

all:
	$(COMPOSE) up -d --build

clean:
	$(COMPOSE) down 

fclean: clean
	docker image prune -a -f

re: fclean all

purge: fclean
	docker volume prune -a -f	

purge-bdd:
	$(COMPOSE) down -v
	docker volume rm $(PROJECT_NAME)_postgres_data $(PROJECT_NAME)_pgadmin_data 2>/dev/null || true

purge-all: clean
	$(COMPOSE) down -v --remove-orphans
	docker system prune -a -f --volumes
	$(COMPOSE) up -d --build