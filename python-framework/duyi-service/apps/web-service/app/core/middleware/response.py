import json

from fastapi import Request
from fastapi.responses import JSONResponse


async def unified_response(request: Request, call_next):
    """统一包装 API 响应，非 API 路径保持原始响应不变。"""
    # 先交给后续中间件和具体接口处理请求，得到原始响应。
    response = await call_next(request)

    # 页面、静态文件等非 API 响应不参与统一包装，直接返回原响应。
    if not request.url.path.startswith("/api/"):
        return response

    # response.body_iterator 是异步迭代器，只能消费一次；这里将所有响应分片
    # 拼成完整字节串，后面才能解析 JSON 并重新构造响应。
    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    # 复制原响应头，尽量保留下游设置的响应信息。
    headers = dict(response.headers)

    # 原响应的长度对应原始 body；包装后 body 长度已经变化，交给
    # JSONResponse/ASGI 重新计算，避免 Content-Length 与实际内容不一致。
    headers.pop("content-length", None)

    # HTTP 状态码为 400 及以上时，按错误响应处理。
    if response.status_code >= 400:
        # 接口通常会返回 JSON 错误对象；没有响应体时使用空字典兜底。
        err = json.loads(body) if body else {}
        return JSONResponse(
            content={
                # 优先使用业务错误码，没有业务码时退回 HTTP 状态码。
                "code": err.get("code", str(response.status_code)),
                # 错误响应不携带正常业务数据。
                "data": None,
                # 优先使用下游提供的错误消息，没有消息时使用空字符串。
                "message": err.get("message", ""),
            },
            # 保留原始 HTTP 状态码，便于客户端和监控系统正确识别错误。
            status_code=response.status_code,
            # 将复制后的响应头传给新响应。
            headers=headers,
        )

    # 成功响应同样按 JSON 解析；空响应体对应 Python 的 None。
    data = json.loads(body) if body else None

    # 统一返回成功结构：业务码为字符串 "0"，实际结果放在 data 中。
    return JSONResponse(
        content={"code": "0", "data": data, "message": "success"},
        # 成功接口继续保留下游返回的 HTTP 状态码，例如 200 或 201。
        status_code=response.status_code,
        # 保留下游响应头，同时使用重新计算后的响应体长度。
        headers=headers,
    )


# 项目加载中间件时读取这个约定：第一个元素是中间件函数，第二个元素是配置。
MIDDLEWARE = (unified_response, {})
