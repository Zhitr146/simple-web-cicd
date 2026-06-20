# simple-web-cicd

一个基于 Flask 的简单 Web 应用，用于软件工程导论课程的 **CI/CD 全流程实践**。

## 项目功能

- `GET /` —— 项目欢迎页，展示版本和可用接口
- `GET /health` —— 健康检查接口（供 Docker、K8s、部署脚本使用）
- `GET /hello?name=...` —— 问候接口
- `GET|POST /api/add?a=...&b=...` —— 加法运算
- `GET|POST /api/multiply?a=...&b=...` —— 乘法运算

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | Flask 3.0 |
| WSGI 服务器 | Gunicorn |
| 语言 | Python 3.11 |
| 单元测试 | pytest + pytest-cov |
| 静态代码检查 | flake8 |
| 容器化 | Docker |
| CI/CD | GitHub Actions |
| 镜像仓库 | GitHub Container Registry (ghcr.io) |

## 本地开发

### 1. 克隆并安装依赖

```bash
git clone https://github.com/<your-username>/simple-web-cicd.git
cd simple-web-cicd
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 本地运行

```bash
python app.py
# 访问 http://localhost:5000
```

### 3. 运行代码检查

```bash
flake8 .
```

### 4. 运行单元测试（含覆盖率）

```bash
pytest tests/ -v --cov=.
```

## Docker 容器化

### 本地构建镜像

```bash
docker build -t simple-web-cicd .
```

### 本地运行容器

```bash
docker run -d --name simple-web-cicd -p 5000:5000 simple-web-cicd
# 或使用 docker-compose
docker-compose up -d --build
```

### 健康检查

```bash
curl http://localhost:5000/health
```

## CI/CD 流水线

GitHub Actions 定义在 `.github/workflows/ci-cd.yml`，包含 4 个阶段：

### 1. Lint（代码风格检查）
- 使用 flake8 对 Python 代码进行静态分析
- 检查语法错误、未使用变量、代码风格一致性

### 2. Test（单元测试 + 覆盖率）
- 使用 pytest 运行所有测试用例（tests/ 目录）
- 生成覆盖率报告（coverage.xml）
- 测试通过后才能进入构建阶段

### 3. Build & Push（构建并推送 Docker 镜像）
- 使用 Docker Buildx 多阶段缓存构建
- 镜像推送到 `ghcr.io/<username>/simple-web-cicd`
- 标签：`latest`、Git 短 SHA、分支名
- **仅在 main/master 分支的 push 事件触发**

### 4. Deploy（部署到云服务器）
- 通过 SSH 连接到云服务器
- 拉取最新镜像，停止并删除旧容器
- 启动新容器并执行健康检查验证
- **仅在 main/master 分支的 push 事件触发**

### 流水线触发条件

| 事件 | Lint | Test | Build | Deploy |
|------|------|------|-------|--------|
| PR 提交 | ✅ | ✅ | ❌ | ❌ |
| Push 到 main/master | ✅ | ✅ | ✅ | ✅ |
| Push 到其他分支 | ✅ | ✅ | ❌ | ❌ |

## 云服务器部署配置

### 前置条件

1. **云服务器**（阿里云/腾讯云/华为云 ECS）：
   - 操作系统：Ubuntu 20.04+ 或 CentOS 7+
   - 已安装 Docker（`docker --version`）
   - 开放安全组入方向的 `5000` 端口和 `22` 端口（SSH）

2. **GitHub 仓库 Secrets** 设置（Settings → Secrets and variables → Actions → New repository secret）：

   | Secret 名称 | 说明 | 示例 |
   |------------|------|------|
   | `DEPLOY_HOST` | 云服务器公网 IP | `123.45.67.89` |
   | `DEPLOY_USER` | SSH 登录用户名 | `root` |
   | `DEPLOY_PORT` | SSH 端口（默认 22）| `22` |
   | `DEPLOY_SSH_KEY` | SSH 私钥内容（-----BEGIN ...-----）| 见下方生成方法 |

### 生成 SSH 密钥对

在云服务器上执行：

```bash
ssh-keygen -t ed25519 -C "github-ci-cd" -f ~/.ssh/github_ci
# 一路回车，不设置密码
cat ~/.ssh/github_ci.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
cat ~/.ssh/github_ci    # 将输出的私钥内容复制到 GitHub Secrets 的 DEPLOY_SSH_KEY
```

### 让云服务器能拉取 ghcr.io 私有镜像

在云服务器上登录 ghcr.io（使用 GitHub Personal Access Token）：

```bash
docker login ghcr.io -u <your-github-username>
# 密码处粘贴你的 GitHub PAT（需包含 read:packages 权限）
```

### 手动部署（备用方案）

如果 GitHub Actions 的 SSH 部署失败，可以直接在云服务器上手动执行：

```bash
# 克隆仓库后
cd ~/simple-web-cicd
chmod +x deploy.sh
./deploy.sh ghcr.io/<your-username>/simple-web-cicd:latest
```

## 项目目录结构

```
simple-web-cicd/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions 流水线
├── tests/
│   ├── __init__.py
│   └── test_app.py            # 单元测试用例
├── app.py                      # Flask 应用主程序
├── requirements.txt            # Python 依赖
├── Dockerfile                  # Docker 镜像构建定义
├── docker-compose.yml          # Docker Compose 配置
├── .dockerignore               # Docker 构建忽略
├── .gitignore                  # Git 忽略
├── .flake8                     # flake8 配置
├── pytest.ini                  # pytest 配置
├── deploy.sh                   # 云服务器部署脚本
└── README.md                   # 项目说明
```

## 课程实践流程参考

1. **编码阶段**：修改 `app.py` 添加新功能，编写对应测试用例到 `tests/`
2. **本地验证**：`pytest` → `flake8` → `docker build`
3. **Git 工作流**：`git add` → `git commit` → `git push origin main`
4. **自动化 CI**：观察 GitHub Actions 的 Lint 和 Test 阶段执行结果
5. **自动化 CD**：Build 阶段自动构建并推送镜像 → Deploy 阶段自动部署到云服务器
6. **验证部署**：访问 `http://<服务器IP>:5000/health` 确认服务正常

## 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| Lint 阶段失败 | 代码风格不符合 PEP 8 | 运行 `flake8 .` 查看错误并修复 |
| Test 阶段失败 | 代码变更破坏了测试 | 本地运行 `pytest` 调试并修复 |
| Build 失败 | Dockerfile 语法错误或依赖缺失 | 本地 `docker build` 调试 |
| Deploy 失败（SSH 连接拒绝）| Secrets 配置错误或 SSH 密钥不对 | 重新配置 DEPLOY_SSH_KEY，确认 authorized_keys |
| Deploy 失败（镜像拉取失败）| 云服务器未登录 ghcr.io | 在云服务器执行 `docker login ghcr.io` |
| 部署后无法访问 | 安全组未开放 5000 端口 | 云控制台安全组添加入方向规则 5000/TCP |

## License

MIT —— 用于课程学习目的
