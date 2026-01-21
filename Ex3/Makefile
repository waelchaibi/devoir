COMPOSE = docker-compose
PROJECT_NAME = ex3

.PHONY: all clean fclean re

all:
	$(COMPOSE) up -d --build

clean:
	$(COMPOSE) down 

fclean: clean
	docker image prune -a -f

re: fclean all

