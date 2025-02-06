# 华芯自动化代理系统

## 项目简介
这是一个基于Python的自动化系统，主要用于处理邮件和网站数据采集任务。系统包含邮件处理模块和爬虫模块两大核心功能，可以自动化处理邮件附件、录入ERP数据，以及采集多个网站的WIP进度数据。

## 开发状态
当前版本：0.1.3 (开发中)
- 邮件处理模块：85% 完成
  - 基础框架：✅ 已完成
  - 邮件规则引擎：✅ 已完成
  - 附件处理：✅ 已完成
  - ERP集成：⚡ 开发中
- 爬虫模块：80% 完成
  - 基础框架：✅ 已完成
  - WIP数据采集：✅ 已完成
  - 数据解析：✅ 已完成
  - 数据入库：⚡ 开发中
- 系统基础设施：95% 完成
  - 数据库连接：✅ 已完成
  - 日志系统：✅ 已完成
  - 配置管理：✅ 已完成
  - 错误处理：✅ 已完成
  - 缓存机制：✅ 已完成

## 主要功能
### 邮件处理模块
- 定时检查未读邮件（可配置间隔时间）
- 自定义规则匹配邮件
- 自动下载和处理Excel附件
- 智能分类和归档附件
- 自动录入ERP系统数据
- 数据存储到SQL Server数据库

### 爬虫模块
- 多网站WIP进度数据采集
  - 和舰科技爬虫
  - 江苏芯丰爬虫
- 数据格式化处理
- 定时执行（可配置执行时间）
- 并行处理支持
- 自动重试机制
- 数据入库和缓存

## 技术架构
- 编程语言：Python 3.8+
- 数据库：SQL Server
- 主要框架/库：
  - APScheduler (任务调度)
  - SQLAlchemy (数据库ORM)
  - pandas & openpyxl (数据处理)
  - requests & BeautifulSoup (网页爬虫)
  - pyautogui & opencv (自动化操作)
  - imap-tools (邮件处理)
  - python-dotenv (环境变量管理)

## 项目结构
```
project_root/
├── config/               # 配置管理
│   ├── settings.yaml     # 全局配置
│   ├── crawler_config.yaml # 爬虫配置
│   └── email_rules.yaml  # 邮件规则配置
│
├── core/                 # 核心逻辑
│   ├── scheduler.py      # 任务调度中心
│   ├── email_processor.py # 邮件处理器
│   └── crawler_processor.py # 爬虫处理器
│
├── modules/              # 功能模块
│   ├── email_processor/  # 邮件处理
│   │   ├── rules/       # 自定义规则实现
│   │   └── handlers/    # 附件处理器
│   │
│   ├── crawlers/        # 爬虫模块
│   │   ├── base.py      # 爬虫基类
│   │   ├── hjtc_crawler.py # 和舰科技爬虫
│   │   └── xinf_crawler.py # 江苏芯丰爬虫
│   │
│   └── file_processor/  # 文件处理
│       ├── delivery_handler.py # 送货单处理
│       └── supplier/    # 供应商数据处理
│
├── infrastructure/       # 基础设施
│   ├── database.py      # 数据库连接池
│   ├── email_client.py  # 邮件客户端
│   └── file_manager.py  # 文件系统管理
│
├── utils/               # 工具类
│   ├── logger.py        # 日志工具
│   ├── helpers.py       # 通用工具函数
│   ├── emailHelper.py   # 邮件处理工具
│   └── cache.py        # 缓存工具
│
├── models/              # 数据模型
│   ├── base.py         # 基础模型
│   └── wip_fab.py      # WIP数据模型
│
├── bll/                 # 业务逻辑层
│   ├── base.py         # 基础业务逻辑
│   └── wip_fab.py      # WIP业务逻辑
│
├── dal/                 # 数据访问层
│   ├── base.py         # 基础数据访问
│   └── wip_fab.py      # WIP数据访问
│
├── attachments/         # 附件存储
├── logs/               # 日志存储
├── tests/              # 测试用例
├── .env               # 环境变量
├── requirements.txt    # 依赖库
└── main.py            # 入口文件
```

## 环境要求
- Python 3.8+
- SQL Server 数据库
- Windows 操作系统（用于ERP自动化操作）
- ODBC Driver 18 for SQL Server

## 安装步骤
1. 克隆项目到本地
```bash
git clone [项目地址]
cd huaxinAgent
```

2. 创建并激活虚拟环境
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. 安装依赖包
```bash
pip install -r requirements.txt
```

4. 配置环境变量
创建 `.env` 文件并配置以下环境变量：
```
EMAIL_ADDRESS=your_email_address
EMAIL_PASSWORD=your_email_password
EMAIL_IMAP_SERVER=your_imap_server
EMAIL_IMAP_PORT=993
EMAIL_USE_SSL=True

DB_USER=your_db_user
DB_PASSWORD=your_db_password

HJTC_USERNAME=your_hjtc_username
HJTC_PASSWORD=your_hjtc_password

XINF_USERNAME=your_xinf_username
XINF_PASSWORD=your_xinf_password
```

5. 修改配置文件
根据实际情况修改以下配置文件：
- `config/settings.yaml`：全局配置
- `config/crawler_config.yaml`：爬虫配置
- `config/email_rules.yaml`：邮件规则配置

## 使用说明
1. 启动系统
```bash
python main.py
```

2. 查看日志
- 运行日志位于 `logs/huaxinAgent_YYYYMMDD.log`
- 日志每天自动轮转，支持多级备份

## 开发指南
### 添加新的邮件处理规则
1. 在 `modules/email_processor/rules/` 下创建新的规则类
2. 实现 `BaseRule` 接口
3. 在 `config/email_rules.yaml` 中注册新规则

### 添加新的爬虫
1. 在 `modules/crawlers/` 下创建新的爬虫类
2. 继承 `BaseCrawler` 类并实现必要的方法：
   - `login()`：实现登录逻辑
   - `run()`：实现爬虫主逻辑
3. 在 `config/crawler_config.yaml` 中添加爬虫配置

## 错误处理
系统实现了完善的错误处理机制：
- 自动重试机制
- 异常日志记录
- 错误状态追踪
- 邮件通知（开发中）

## 维护说明
- 定期检查日志文件
- 清理临时文件夹（系统会自动清理7天前的文件）
- 更新依赖包版本
- 监控数据库连接状态
- 检查爬虫配置有效性

## 更新日志
### [0.1.3] - 2024-02-06
- 优化爬虫模块
  - 完善爬虫配置管理
  - 添加爬虫状态监控
  - 实现并行处理
  - 优化错误处理
- 改进邮件处理
  - 优化附件保存逻辑
  - 完善文件命名规则
  - 添加文件重复检查
- 增强系统稳定性
  - 添加数据缓存机制
  - 优化数据库连接池
  - 完善日志记录

### [0.1.2] - 2024-02-05
- 完善邮件处理模块
  - 添加邮件规则引擎
  - 实现送货单规则处理
  - 实现进度报告规则处理
- 优化项目结构
  - 添加核心业务逻辑层
  - 添加数据访问层
  - 规范化模块划分

### [0.1.1] - 2024-02-04
- 优化数据库连接配置
- 完善日志系统
- 添加Windows认证支持
- 实现邮件测试功能

## 待办事项
- [x] 搭建基础项目架构
- [x] 创建基础配置文件
- [x] 配置日志系统
- [x] 实现数据库连接模块
- [x] 开发基础工具类
- [x] 完善邮件处理模块
  - [x] 基础框架搭建
  - [x] 邮件连接测试
  - [x] 邮件规则引擎
  - [x] 附件处理器
  - [ ] ERP数据录入集成
- [x] 实现爬虫模块
  - [x] 爬虫基类
  - [x] WIP数据采集
  - [x] 数据解析优化
  - [ ] 数据入库完善
- [ ] 实现ERP自动化模块
- [ ] 添加单元测试
  - [x] 邮件连接测试
  - [x] 数据库操作测试
  - [x] 规则引擎测试
  - [ ] 爬虫模块测试
- [ ] 添加监控告警功能
- [ ] 优化性能和资源使用
- [ ] 添加数据验证机制
- [ ] 实现配置热更新
- [ ] 添加Web管理界面

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证
MIT License

## 联系方式
- 作者：[您的名字]
- 邮箱：[您的邮箱]
- 项目地址：[项目仓库地址] 
