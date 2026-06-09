<div align="center">

# 🦞 CodeReview-AI-CLI

**Lightweight Terminal Code Review & Quality Analysis Engine**

**轻量级终端代码审查与质量分析引擎**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen)](requirements.txt)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-lightgrey)](setup.py)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🎉 English

### Introduction

CodeReview-AI-CLI is a **zero-dependency**, lightweight terminal tool for intelligent code review and quality analysis. Inspired by trending projects like `headroom` (context compression) and `liteparse` (document parsing), we built a **pure Python** solution that brings professional code review capabilities directly to your terminal.

**Key Differentiation:** Unlike web-based code review tools, CodeReview-AI-CLI operates entirely in your terminal with zero external dependencies, making it perfect for CI/CD pipelines, pre-commit hooks, and offline development environments.

### ✨ Core Features

- 🔍 **Intelligent Code Analysis** - AST-based deep analysis with cyclomatic complexity calculation
- 🛡️ **Security Scanning** - Detects 11+ security vulnerability patterns (eval, exec, hardcoded secrets, etc.)
- ⚡ **Performance Detection** - Identifies anti-patterns like `range(len())`, string concatenation in loops
- 🎨 **Style Checking** - PEP 8 compliance, naming conventions, import order validation
- 📊 **Quality Scoring** - 0-100 quality score with severity-based weighting
- 🌿 **Git Integration** - Analyze diffs, commits, and branch comparisons
- 🖥️ **TUI Dashboard** - Interactive terminal interface with color-coded output
- 📄 **Multi-format Export** - Text, JSON, Markdown, and HTML reports
- 🚀 **Zero Dependencies** - Pure Python standard library, no pip install required

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- Git (optional, for diff analysis features)

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/CodeReview-AI-CLI.git
cd CodeReview-AI-CLI

# Run directly (no installation needed)
python main.py --help

# Or install as a package
pip install -e .
```

#### Basic Usage

```bash
# Analyze current directory
python main.py analyze

# Analyze a specific file
python main.py analyze src/main.py

# Analyze with JSON output
python main.py analyze src/ --format json --output report.json

# Analyze Git diff
python main.py diff

# Analyze specific commit
python main.py commit HEAD~1

# Compare branches
python main.py compare main develop

# Generate comprehensive report
python main.py report src/ -o report.html --format html

# Interactive TUI mode
python main.py interactive
```

### 📖 Detailed Usage Guide

#### Severity Levels

| Level | Description | Weight |
|-------|-------------|--------|
| CRITICAL | Security vulnerabilities, dangerous operations | -20 pts |
| HIGH | Potential bugs, mutable defaults | -10 pts |
| MEDIUM | Performance issues, high complexity | -5 pts |
| LOW | Style violations, minor issues | -2 pts |
| INFO | Suggestions, TODOs | -1 pt |

#### Configuration

Filter by minimum severity:
```bash
python main.py analyze src/ --severity HIGH
```

#### Output Formats

**Text (default)** - Colorized terminal output with TUI dashboard
**JSON** - Machine-readable for CI/CD integration
**Markdown** - For GitHub PR descriptions
**HTML** - Beautiful reports for sharing

### 💡 Design Philosophy

We believe code quality tools should be:
- **Accessible** - Zero dependencies means it works anywhere
- **Fast** - Pure Python with no overhead
- **Actionable** - Every issue includes a specific suggestion
- **Integrated** - Native Git support for workflow automation

### 📦 Deployment

#### As a Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: codereview-ai
        name: Code Quality Check
        entry: python /path/to/main.py analyze
        language: system
        pass_filenames: true
```

#### CI/CD Integration

```yaml
# .github/workflows/quality.yml
- name: Code Quality Analysis
  run: |
    python main.py analyze src/ --format json --output quality.json
    python -c "import json; d=json.load(open('quality.json')); assert all(r['quality_score'] > 60 for r in d), 'Quality check failed'"
```

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guide
- All tests pass (`python -m unittest discover tests/`)
- New features include tests

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🎉 简体中文

### 项目介绍

CodeReview-AI-CLI 是一款**零依赖**的轻量级终端代码审查与质量分析工具。灵感来源于 `headroom`（上下文压缩）和 `liteparse`（文档解析）等热门项目，我们构建了一个**纯 Python**的解决方案，将专业的代码审查能力直接带到您的终端。

**核心差异化：** 与基于网页的代码审查工具不同，CodeReview-AI-CLI 完全在终端中运行，零外部依赖，非常适合 CI/CD 流水线、预提交钩子和离线开发环境。

### ✨ 核心特性

- 🔍 **智能代码分析** - 基于 AST 的深度分析，支持圈复杂度计算
- 🛡️ **安全漏洞扫描** - 检测 11+ 种安全漏洞模式（eval、exec、硬编码密钥等）
- ⚡ **性能问题检测** - 识别 `range(len())`、循环中字符串拼接等反模式
- 🎨 **代码风格检查** - PEP 8 合规性、命名规范、导入顺序验证
- 📊 **质量评分** - 0-100 质量分数，基于严重级别加权
- 🌿 **Git 集成** - 分析差异、提交和分支对比
- 🖥️ **TUI 仪表盘** - 交互式终端界面，彩色编码输出
- 📄 **多格式导出** - 文本、JSON、Markdown 和 HTML 报告
- 🚀 **零依赖** - 纯 Python 标准库，无需 pip 安装

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- Git（可选，用于差异分析功能）

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/CodeReview-AI-CLI.git
cd CodeReview-AI-CLI

# 直接运行（无需安装）
python main.py --help

# 或作为包安装
pip install -e .
```

#### 基本用法

```bash
# 分析当前目录
python main.py analyze

# 分析特定文件
python main.py analyze src/main.py

# JSON 格式输出
python main.py analyze src/ --format json --output report.json

# 分析 Git 差异
python main.py diff

# 分析特定提交
python main.py commit HEAD~1

# 对比分支
python main.py compare main develop

# 生成综合报告
python main.py report src/ -o report.html --format html

# 交互式 TUI 模式
python main.py interactive
```

### 📖 详细使用指南

#### 严重级别

| 级别 | 描述 | 权重 |
|------|------|------|
| CRITICAL | 安全漏洞、危险操作 | -20 分 |
| HIGH | 潜在 Bug、可变默认值 | -10 分 |
| MEDIUM | 性能问题、高复杂度 | -5 分 |
| LOW | 风格违规、轻微问题 | -2 分 |
| INFO | 建议、TODO | -1 分 |

#### 配置

按最低严重级别过滤：
```bash
python main.py analyze src/ --severity HIGH
```

#### 输出格式

**文本（默认）** - 彩色终端输出，TUI 仪表盘
**JSON** - 机器可读，适合 CI/CD 集成
**Markdown** - 用于 GitHub PR 描述
**HTML** - 美观的报告，便于分享

### 💡 设计理念

我们认为代码质量工具应该：
- **随处可用** - 零依赖意味着在任何地方都能工作
- **极速运行** - 纯 Python，无额外开销
- ** actionable** - 每个问题都包含具体建议
- **深度集成** - 原生 Git 支持，便于工作流自动化

### 📦 部署

#### 作为预提交钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: codereview-ai
        name: 代码质量检查
        entry: python /path/to/main.py analyze
        language: system
        pass_filenames: true
```

#### CI/CD 集成

```yaml
# .github/workflows/quality.yml
- name: 代码质量分析
  run: |
    python main.py analyze src/ --format json --output quality.json
    python -c "import json; d=json.load(open('quality.json')); assert all(r['quality_score'] > 60 for r in d), '质量检查失败'"
```

### 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/ amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加 amazing 功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

请确保：
- 代码遵循 PEP 8 风格指南
- 所有测试通过 (`python -m unittest discover tests/`)
- 新功能包含测试

### 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🎉 繁體中文

### 專案介紹

CodeReview-AI-CLI 是一款**零依賴**的輕量級終端程式碼審查與品質分析工具。靈感來源於 `headroom`（上下文壓縮）和 `liteparse`（文件解析）等熱門專案，我們建構了一個**純 Python**的解決方案，將專業的程式碼審查能力直接帶到您的終端。

**核心差異化：** 與基於網頁的程式碼審查工具不同，CodeReview-AI-CLI 完全在終端中執行，零外部依賴，非常適合 CI/CD 流水線、預提交鉤子和離線開發環境。

### ✨ 核心特性

- 🔍 **智慧程式碼分析** - 基於 AST 的深度分析，支援圈複雜度計算
- 🛡️ **安全漏洞掃描** - 檢測 11+ 種安全漏洞模式（eval、exec、硬編碼金鑰等）
- ⚡ **效能問題檢測** - 識別 `range(len())`、迴圈中字串拼接等反模式
- 🎨 **程式碼風格檢查** - PEP 8 合規性、命名規範、匯入順序驗證
- 📊 **品質評分** - 0-100 品質分數，基於嚴重級別加權
- 🌿 **Git 整合** - 分析差異、提交和分支對比
- 🖥️ **TUI 儀表板** - 互動式終端介面，彩色編碼輸出
- 📄 **多格式匯出** - 文字、JSON、Markdown 和 HTML 報告
- 🚀 **零依賴** - 純 Python 標準庫，無需 pip 安裝

### 🚀 快速開始

#### 環境要求
- Python 3.8 或更高版本
- Git（可選，用於差異分析功能）

#### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/CodeReview-AI-CLI.git
cd CodeReview-AI-CLI

# 直接執行（無需安裝）
python main.py --help

# 或作為套件安裝
pip install -e .
```

#### 基本用法

```bash
# 分析當前目錄
python main.py analyze

# 分析特定檔案
python main.py analyze src/main.py

# JSON 格式輸出
python main.py analyze src/ --format json --output report.json

# 分析 Git 差異
python main.py diff

# 分析特定提交
python main.py commit HEAD~1

# 對比分支
python main.py compare main develop

# 生成綜合報告
python main.py report src/ -o report.html --format html

# 互動式 TUI 模式
python main.py interactive
```

### 📖 詳細使用指南

#### 嚴重級別

| 級別 | 描述 | 權重 |
|------|------|------|
| CRITICAL | 安全漏洞、危險操作 | -20 分 |
| HIGH | 潛在 Bug、可變預設值 | -10 分 |
| MEDIUM | 效能問題、高複雜度 | -5 分 |
| LOW | 風格違規、輕微問題 | -2 分 |
| INFO | 建議、TODO | -1 分 |

#### 配置

按最低嚴重級別過濾：
```bash
python main.py analyze src/ --severity HIGH
```

#### 輸出格式

**文字（預設）** - 彩色終端輸出，TUI 儀表板
**JSON** - 機器可讀，適合 CI/CD 整合
**Markdown** - 用於 GitHub PR 描述
**HTML** - 美觀的報告，便於分享

### 💡 設計理念

我們認為程式碼品質工具應該：
- **隨處可用** - 零依賴意味著在任何地方都能工作
- **極速執行** - 純 Python，無額外開銷
- ** actionable** - 每個問題都包含具體建議
- **深度整合** - 原生 Git 支援，便於工作流自動化

### 📦 部署

#### 作為預提交鉤子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: codereview-ai
        name: 程式碼品質檢查
        entry: python /path/to/main.py analyze
        language: system
        pass_filenames: true
```

#### CI/CD 整合

```yaml
# .github/workflows/quality.yml
- name: 程式碼品質分析
  run: |
    python main.py analyze src/ --format json --output quality.json
    python -c "import json; d=json.load(open('quality.json')); assert all(r['quality_score'] > 60 for r in d), '品質檢查失敗'"
```

### 🤝 貢獻指南

1. Fork 本倉庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 新增 amazing 功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

請確保：
- 程式碼遵循 PEP 8 風格指南
- 所有測試通過 (`python -m unittest discover tests/`)
- 新功能包含測試

### 📄 開源協議

本專案採用 MIT 協議開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**Made with 🦞 by gitstq**

[⭐ Star this repo](https://github.com/gitstq/CodeReview-AI-CLI) | [🐛 Report Issue](https://github.com/gitstq/CodeReview-AI-CLI/issues) | [🤝 Contribute](https://github.com/gitstq/CodeReview-AI-CLI/pulls)

</div>
