# CUQU找搭子 MCP stdio bridge
# 供 glama.ai 等目录站 introspection 检测与 stdio MCP 客户端使用
FROM python:3.13-slim

WORKDIR /app
COPY scripts/mcp-stdio-bridge.py /app/mcp-stdio-bridge.py

# 无第三方依赖; stdio 模式需 unbuffered 输出
ENV PYTHONUNBUFFERED=1
# 运行时可选: CUQU_API_KEY=cq-sk-xxx (tools/call 转发托管网关用)

CMD ["python", "-u", "mcp-stdio-bridge.py"]
