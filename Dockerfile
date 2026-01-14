FROM python:3.12

WORKDIR /workspace
COPY . .
RUN pip install .
ENTRYPOINT ["netmind-web3-mcp"]
