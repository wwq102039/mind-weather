# 心灵晴雨 Mind Weather

> **班级心理关怀站**：30 秒匿名情绪打卡 + 大数据可视化 + 心理科普知识库。
> 用 Flask 写的轻量 Web 应用，打开即用、无需登录，用图表让每个人看见自己的情绪轨迹。

---

## 项目缘起

班级里做心理关怀，常见的问题是「没人愿意说」。打卡表要填姓名、问卷太长、还怕被看见——最后数据是空的。

这个项目的取舍是：**把记录成本压到 30 秒，把隐私做到不采集身份**。只留四个数值（情绪、压力、睡眠、精力）和一句可选的备注，其余全部匿名。数据攒起来之后，用可视化把「感觉」变成「能看见的趋势」，再配一套可读的科普内容，让关怀从「填表」变成「有反馈」。

## 功能

| 页面 | 路由 | 说明 |
|---|---|---|
| 首页 | `/` | 项目说明与入口 |
| 情绪打卡 | `/record` | 每日打卡：情绪 1–5、压力 1–10、睡眠小时数、精力 1–5、备注（可选） |
| 我的记录 | `/history` | 个人历史打卡列表 |
| 数据中心 | `/dashboard` | 情绪分布、7 天趋势、群体平均 |
| 月度报告 | `/monthly` | 按月汇总与趋势 |
| 知识科普 | `/knowledge` | 文章列表，按分类/标签组织 |
| 文章详情 | `/knowledge/<id>` | Markdown-lite 渲染的正文 |

- **匿名免登录**：首次访问由服务端下发随机 `visitor_id`（`secrets.token_hex(16)`），存于 httpOnly + SameSite=Lax 的 Cookie 中，**不采集姓名、学号、手机号等任何可识别身份的信息**。
- **零配置启动**：首次运行自动建表并写入 7 篇心理科普文章种子数据，不需要手动初始化。
- **离线可用**：ECharts 内置于 `static/js/`，不走 CDN，断网也能出图。

## 技术栈

| 层 | 选型 |
|---|---|
| Web 框架 | Flask 3 |
| ORM | Flask-SQLAlchemy 3.1 |
| 数据库 | SQLite（单文件，无外部依赖） |
| 模板 | Jinja2 服务端渲染（无前端框架） |
| 图表 | ECharts（本地内置） |
| 样式 | 原生 CSS（`static/css/style.css`） |

整个项目**只有两个第三方依赖**（`Flask`、`Flask-SQLAlchemy`），没有构建步骤、没有 npm、没有打包工具。

## 目录结构

```
mind-weather/
├── app/
│   ├── __init__.py          # 应用工厂：配置、蓝图注册、匿名访客钩子、md_lite 过滤器
│   ├── models.py            # 数据模型：MoodRecord / Article
│   ├── main.py              # 首页、数据中心、月度报告
│   ├── records.py           # 情绪打卡、我的记录
│   ├── knowledge.py         # 知识科普列表与详情
│   ├── seed.py              # 7 篇心理科普种子文章
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/echarts.min.js
│   └── templates/           # base / index / record / history / dashboard / monthly / knowledge_*
├── requirements.txt
├── run.py                   # 启动入口
├── run.bat                  # Windows 一键启动
└── reset_data.py            # 清空打卡记录（正式启用前重置用）
```

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活（Windows）
venv\Scripts\activate
# macOS / Linux：source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动
python run.py
```

打开 <http://127.0.0.1:5000>。

首次启动会自动创建 `app/data.db` 并写入 7 篇科普文章，**不需要手动初始化数据库**。
Windows 用户也可以直接双击 `run.bat`。

> 想让同局域网的同学访问，把 `run.py` 里的 `host="127.0.0.1"` 改为 `host="0.0.0.0"`。

## 数据结构

```
mood_record
  id            INTEGER PK
  visitor_id    TEXT(64)   随机访客标识（非身份信息），索引
  date          DATE       打卡日期
  mood          INTEGER    情绪 1–5
  stress        INTEGER    压力 1–10
  sleep         FLOAT      睡眠时长（小时）
  energy        INTEGER    精力 1–5
  note          TEXT       备注（可空）
  created_at    DATETIME
  唯一约束： (visitor_id, date)   # 每人每天一条

article
  id, title, category, summary, content, tags, created_at
```

## 设计取舍

### 1. 匿名优先的身份设计

没有用户表、没有密码、没有登录流程。`before_request` 里读 Cookie，`after_request` 里回写，首次访问生成随机串。代价是「换浏览器就丢记录」，收益是**数据库里没有任何可以指向真人的字段**——这对心理类数据是必要的取舍。

### 2. 自带 Markdown 渲染 + 强制转义

`app/__init__.py` 里的 `md_lite()` 只支持 `##` / `###` 标题、`- ` 列表和空行分段，其余字符一律 `escape()`，最后用 `Markup` 显式声明为安全 HTML。**因为文章内容是管理员录入的富文本，这是本项目唯一的 XSS 面，所以没有引入任何通用 Markdown 库**。

### 3. 零配置的可复现性

`create_app()` 内部完成 `db.create_all()` 与 `seed()`，克隆仓库后直接 `python run.py` 就能跑，不需要额外步骤——这也是本项目**不提交 `data.db`** 的前提（每人本地自动生成干净库）。

### 4. 只用两个依赖

刻意不引入 Flask-Migrate、WTForms、Bootstrap 之类，保持「一个文件能读完」的规模。目的是让班级里有 Python 基础的同学能自己改文案、加字段。

## 部署注意

| 项 | 说明 |
|---|---|
| `SECRET_KEY` | 代码里有开发用默认值，**公网部署必须用环境变量 `SECRET_KEY` 覆盖** |
| `debug=True` | `run.py` 中是开发模式，生产请用 `waitress` / `gunicorn` 启动并关闭 debug |
| 鉴权 | 无登录、无管理后台，定位是**班级内网小站**，不适合多租户或公网开放 |
| 数据库 | SQLite 单机，适合小规模；数据量大时换 PostgreSQL |

## 隐私说明

- 仓库内**不包含任何真实打卡数据**：`app/data.db` 已被 `.gitignore` 排除，克隆后由 `seed()` 生成干净库。
- 应用本身不采集可识别个人身份的信息，访客标识为随机字符串。
- ⚠️ 若你部署此项目收集他人数据：**心理健康相关信息属于敏感个人信息**，需取得单独同意并做加密与访问控制。请勿把真实打卡数据提交到任何仓库。

## 已知限制

- 无鉴权与管理后台，数据按 Cookie 隔离，清除 Cookie 即丢失关联；
- 无数据导出功能（导出 CSV / 个人报告是下一步）；
- 无自动化测试；
- 月度报告为固定字段聚合，暂不支持自定义时间区间；
- `SECRET_KEY` 与 debug 模式均为开发默认值（见上方部署注意）。

## 路线图

- [ ] 打卡数据导出（CSV / 图片报告）
- [ ] 月度报告支持自定义区间
- [ ] 增加 pytest 用例（打卡唯一约束、权限隔离、md_lite 转义）
- [ ] 引入 Alembic 管理表结构变更
- [ ] 生产化：waitress 启动脚本 + 环境变量校验（缺失 SECRET_KEY 直接拒绝启动）

## 内容说明

`app/seed.py` 中的 7 篇心理科普文章（情绪管理 / 压力应对 / 睡眠健康 / 时间管理 / 人际关系）为本项目原创内容，随代码一并开源。

## 许可

个人学习与研究作品，未附加开源许可证。如需引用或用于商业场景，请先联系作者。
