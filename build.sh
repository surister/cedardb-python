mkdir ./build
wget https://cedardb.com/download/Dockerfile -O ./build/cedardb.Dockerfile
docker build --tag cedardb -f ./build/cedardb.Dockerfile .