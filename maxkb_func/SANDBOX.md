# MaxKB tool / workflow Python Sandbox (SANDBOX=1, LD_PRELOAD=sandbox.so)

企业版默认开启进程级沙箱。工具代码与工作流 `tool-node` 均在此环境执行。

## 默认禁止（除非运维改配置）

| 能力 | 配置项 | 默认 | 影响 |
|------|--------|------|------|
| **子进程** | `SANDBOX_PYTHON_ALLOW_SUBPROCESS` | `0` | `subprocess` / `os.system` / `os.popen` / `multiprocessing` / `Popen` → `Permission denied to create subprocess` |
| **原始 syscall** | `SANDBOX_PYTHON_ALLOW_SYSCALL` | `0` | `ctypes` 绕过类调用受限 |
| **任意 dlopen** | `SANDBOX_PYTHON_ALLOW_DL_OPEN` / `ALLOW_DL_PATHS` | 白名单路径 | 仅允许沙箱包路径下的原生扩展 |

结果：**凡依赖 fork/exec/shell 的库在工具里都不可用**。

## 明确不要用在工具里的包/写法

| 类型 | 例子 | 原因 |
|------|------|------|
| 调 shell / 外部 CLI | `markitdown`（多数路径会起进程）、`pdf2image`+poppler、`ffmpeg-python`、调用 `pandoc`/`wkhtmltopdf` | 需要 subprocess |
| 进程封装 | `subprocess`、`os.system`、`multiprocessing`、`concurrent.futures.ProcessPoolExecutor` | 沙箱拦截创建子进程 |
| 未安装依赖 | 任意不在 sandbox site-packages 的包 | `No module named '...'`；需运维装到 `/opt/maxkb-app/sandbox/python-packages` 等 |
| 访问黑名单主机 | 配置了 `SANDBOX_PYTHON_BANNED_HOSTS` 的域名/IP | `Permission denied to access ...` |
| Unix socket / 部分敏感 syscall | — | 沙箱拦截 |

实测（MaxKB EE v2.10.x 常见表现）：

```text
subprocess.getoutput(...)  → Permission denied to create subprocess.
import markitdown          → No module named 'markitdown'（即使安装，转换也常走 shell）
```

## 可用的替代思路

1. **纯 Python 计算 / HTTP(S) 请求**（未进黑名单的域名）：`requests`、`json`、`re`、`datetime` 等（以实例已安装包为准）。
2. **文档解析**：优先用工作流内置「文档内容提取 / 分段」节点，或知识库上传链路，不要在工具里 shell 出 markitdown。
3. 确实需要 CLI：由**平台管理员**设置 `SANDBOX_PYTHON_ALLOW_SUBPROCESS=1` 并安装依赖（有安全风险，需审批）。

## 资源限制（常见默认）

- 内存约 `SANDBOX_PYTHON_PROCESS_LIMIT_MEM_MB=256`
- 超时约 `SANDBOX_PYTHON_PROCESS_LIMIT_TIMEOUT_SECONDS=3600`
- CPU 亲和核数可配

## tool-lib 参数绑定注意

工具库节点执行时会用**工具定义里的 `source`** 覆盖节点上的 `source`。  
因此 `tool-lib-node` 引用上游结果请用 **自定义字符串模板**：

```json
{ "name": "text", "type": "string", "source": "custom", "value": "{{内嵌工具.result}}", "is_required": true }
```

不要对 `tool-lib-node` 使用 `value: ["node-id","result"]` 引用数组（会被当成 custom 字符串列表导致类型错误）。  
`tool-node`（工作流内嵌代码）则可用 `source: reference` + 数组地址。
