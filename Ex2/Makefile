COMPOSE = docker-compose
PROJECT_NAME = ex2

.PHONY: all clean fclean re

all:
	$(COMPOSE) -p $(PROJECT_NAME) up -d --build

clean:
	$(COMPOSE) -p $(PROJECT_NAME) down 

fclean: clean
	docker image prune -a -f

re: fclean all

purge: fclean
	docker volume prune -a -f