# CUQU找搭子 MCP Server (open-source implementation)
# stdio JSON-RPC server: read tools hit CUQU public live API,
# write tools forward to the hosted gateway with CUQU_API_KEY.
FROM python:3.13-slim

WORKDIR /app
COPY server.py /app/server.py

ENV PYTHONUNBUFFERED=1
# Optional at runtime: CUQU_API_KEY=cq-sk-xxx (enables write tools)

CMD ["python", "-u", "server.py"]
