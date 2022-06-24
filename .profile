wget https://localtonet.com/download/localtonet-linux-x64.zip
unzip linux-x64.zip
chmod 777 localtonet
./localtonet authtoken ${token}
localtonet udptcp 6567