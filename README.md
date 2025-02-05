# 华芯自动化代理系统

## 项目简介
这是一个基于Python的自动化系统，主要用于处理邮件和网站数据采集任务。系统包含邮件处理模块和爬虫模块两大核心功能，可以自动化处理邮件附件、录入ERP数据，以及采集多个网站的WIP进度数据。

## 开发状态
当前版本：0.1.2 (开发中)
- 邮件处理模块：70% 完成
  - 基础框架：✅ 已完成
  - 邮件规则引擎：⚡ 开发中
  - 附件处理：⚡ 开发中
  - ERP集成：📅 计划中
- 爬虫模块：30% 完成
  - 基础框架：✅ 已完成
  - WIP数据采集：⚡ 开发中
  - 数据解析：📅 计划中
- 系统基础设施：90% 完成
  - 数据库连接：✅ 已完成
  - 日志系统：✅ 已完成
  - 配置管理：✅ 已完成
  - 错误处理：✅ 已完成

## 主要功能
### 邮件处理模块
- 定时检查未读邮件（每10分钟）
- 自定义规则匹配邮件
- 自动下载和处理Excel附件
- 自动录入ERP系统数据
- 数据存储到SQL Server数据库

### 爬虫模块
- 多网站WIP进度数据采集
- 数据格式化处理
- 定时执行（每天8点）

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

## 项目结构
```
project_root/
├── config/               # 配置管理
│   ├── __init__.py
│   ├── settings.yaml     # 全局配置
│   └── logging.conf      # 日志配置
│
├── core/                 # 核心逻辑
│   └── scheduler.py      # 任务调度中心
│
├── modules/              # 功能模块
│   ├── email_processor/  # 邮件处理
│   │   ├── checker.py    # 邮件检查器
│   │   ├── rules/        # 自定义规则实现
│   │   └── handlers/     # 附件处理器
│   │
│   ├── crawlers/         # 爬虫模块
│   │   ├── base.py       # 爬虫基类
│   │   ├── site1_crawler.py 
│   │   └── site2_crawler.py
│   │
│   └── erp_integration/  # ERP对接
│       ├── adapter.py    # ERP操作适配器
│       └── locators.py   # 界面元素定位配置
│
├── infrastructure/       # 基础设施
│   ├── database.py       # 数据库连接池
│   ├── email_client.py   # 邮件客户端
│   └── file_manager.py   # 文件系统管理
│
├── utils/                # 工具类
│   ├── logger.py         # 日志装饰器
│   ├── retry.py          # 重试机制
│   └── helpers.py        # 通用工具函数
│
├── temp/                 # 临时文件夹
├── logs/                 # 日志存储
├── requirements.txt      # 依赖库
└── main.py              # 入口文件
```

## 环境要求
- Python 3.8+
- SQL Server 数据库
- Windows 操作系统（用于ERP自动化操作）

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
EMAIL_PASSWORD=your_email_password
```

5. 修改配置文件
根据实际情况修改 `config/settings.yaml` 中的配置

## 使用说明
1. 启动系统
```bash
python main.py
```

2. 查看日志
- 运行日志位于 `logs/huaxin_agent.log`
- 日志每天自动轮转，保留30天

## 开发指南
### 添加新的邮件处理规则
1. 在 `modules/email_processor/rules/` 下创建新的规则类
2. 实现 `BaseRule` 接口
3. 在配置文件中注册新规则

### 添加新的爬虫
1. 在 `modules/crawlers/` 下创建新的爬虫类
2. 继承 `BaseCrawler` 类
3. 实现必要的方法
4. 在配置文件中添加相关配置

## 错误处理
系统实现了完善的错误处理机制：
- 自动重试机制
- 异常日志记录
- 邮件通知（待实现）

## 维护说明
- 定期检查日志文件
- 清理临时文件夹（系统会自动清理7天前的文件）
- 更新依赖包版本

## 更新日志
### [0.1.2] - 2024-02-05
- 完善邮件处理模块
  - 添加邮件规则引擎基础框架
  - 实现送货单规则处理
  - 实现进度报告规则处理
  - 实现测试报告规则处理
- 优化项目结构
  - 添加核心业务逻辑层(BLL)
  - 添加数据访问层(DAL)
  - 规范化模块划分
- 增加自动重试机制
- 添加缓存支持
- 完善日志记录

### [0.1.1] - 2024-02-04
- 优化数据库连接配置
- 完善日志系统（支持JSON格式、文件轮转）
- 添加Windows和SQL Server认证支持
- 实现邮件测试功能
- 增加环境变量配置支持

## 待办事项
- [x] 搭建基础项目架构
- [x] 创建基础配置文件
- [x] 配置日志系统
- [x] 实现数据库连接模块
- [x] 开发基础工具类
- [ ] 完善邮件处理模块
  - [x] 基础框架搭建
  - [x] 邮件连接测试
  - [x] 邮件规则引擎基础框架
  - [ ] 完善规则实现
  - [ ] 附件处理器优化
  - [ ] ERP数据录入集成
- [ ] 实现爬虫模块
  - [x] 爬虫基类
  - [ ] WIP数据采集
  - [ ] 数据解析优化
- [ ] 实现ERP自动化模块
- [ ] 添加单元测试
  - [x] 邮件连接测试
  - [x] 数据库操作测试
  - [ ] 规则引擎测试
- [ ] 添加监控告警功能
- [ ] 优化性能和资源使用
- [ ] 添加数据验证机制
- [ ] 实现配置热更新
- [ ] 添加用户界面（可选）

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证
[待定]

## 联系方式
[待补充] 