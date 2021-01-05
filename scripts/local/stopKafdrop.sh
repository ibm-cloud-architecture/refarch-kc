docker stop $(docker ps | grep kafdrop | awk '{print $1}')
