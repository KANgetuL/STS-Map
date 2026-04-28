# STS Map

[![Status](https://img.shields.io/badge/Status-Completed-success.svg)](#)

*An accurate, procedurally generated map generator simulation matching the topological constraints of "Slay the Spire". / 完美模拟《杀戮尖塔》（Slay the Spire）底层地图生成拓扑规则的程序化生成引擎。*

---

## 🇬🇧 English

### Overview
**STS Map** is a complete Python-based procedural generation engine for replicating the map system of *Slay the Spire*. Having achieved all structural milestones, the generator accurately creates node paths across Acts (Floors 0 to 15), applying strict geometric validators, node pruning, path balancing, and deterministic seeds, concluding with a fully converged single boss node.

### Image Preview
<img src="full_sts_map.png" alt="STS Map" width="400">

### Core Features
- **Authentic Topology:** Restricts paths, branch intersections, and respects minimum/maximum node path logic per floor.
- **Single Boss Convergence:** Automatically routes all Floor 14 nodes exactly to the Act Boss at the apex center.
- **Dead-end Pruning:** Actively cleans up isolated start nodes (Floor 0) and guarantees no path-less nodes in between.
- **Deterministic Generation:** Utilizing hash combinations (`md5(seed + act_id)`), providing identical map outputs for shared seeds.
- **Visualization Tooling:** Includes a Matplotlib-based rendering script (`scripts/visualize_full_game.py`) visualizing all 4 concatenated acts in high fidelity.

### Quick Start (Windows PowerShell)

```powershell
# 1. Create and activate Conda environment
conda env create -f environment.yml
conda activate sts-map

# 2. Run the visualizer to generate a map image
python scripts/visualize_full_game.py

# 3. Development / Testing Checks
python -m pytest -q
ruff check .
mypy sts_map
```

### Public API

```python
from sts_map.api import generate_map, generate_map_payload, generate_map_json
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput

input_data = GenerationInput(
    act_id=ActId.ACT1, 
    ascension=10, 
    seed=42, 
    rule_version="0.6.0"
)

# Generate Python object graph
graph = generate_map(input_data)
# Generate structured payload
payload = generate_map_payload(input_data)
# Generate serialized JSON
payload_json = generate_map_json(input_data)
```

---

## 🇨🇳 中文 (Chinese)

### 项目简介
**STS Map** 是一个基于 Python 构建的程序化地图生成引擎，旨在1:1完美还原电子游戏《杀戮尖塔》的路线生成机制。本项目已圆满完成所有既定目标，可以精确生成各幕（第0层至第15层）的节点路径，并包含极其严格的空间验证、死胡同修剪、路径负载均衡，且已完全实现了唯一的Boss节点连线汇聚逻辑与确定性的随机种子控制。

### 图片预览
<img src="full_sts_map.png" alt="STS Map" width="400">

### 核心特性
- **真实的拓扑规则：** 严格限制路径交叉，精确模仿游戏内每层节点的分布规律与生成偏好。
- **单Boss节点汇聚：** 强制将第14层出现的所有路径统一连接至第15层最中心的单一Boss节点，复刻了原作“塔顶”视觉结构。
- **孤立节点剪枝：** 完善的死角检测过滤机制，自动清理无连线的第0层“空悬”起始节点，并保证地图内全路径畅通。
- **确定性随机生成：** 使用 `md5(seed + act_id)` 组合算法计算单幕种子，确保同一个输入参数永远定轨生成固定的拓扑表现。
- **全图可视化工具：** 提供基于 Matplotlib 的脚本（`scripts/visualize_full_game.py`），支持一键渲染预览拼接好的四幕高清视觉地图。

### 快速开始 (Windows PowerShell)

```powershell
# 1. 创建并激活 Conda 环境
conda env create -f environment.yml
conda activate sts-map

# 2. 运行可视化脚本，输出完整的地图图像
python scripts/visualize_full_game.py

# 3. 执行自动化测试与代码静态检查
python -m pytest -q
ruff check .
mypy sts_map
```

### 开放 API参考

```python
from sts_map.api import generate_map, generate_map_payload, generate_map_json
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput

# 设置环境参数与配置（支持指定进阶等级与随机种子）
input_data = GenerationInput(
    act_id=ActId.ACT1, 
    ascension=10, 
    seed=42, 
    rule_version="0.6.0"
)

# 直接生成用于后端的图对象
graph = generate_map(input_data)
# 生成标准数据结构对象
payload = generate_map_payload(input_data)
# 直接导出序列化 JSON 字符串给客户端加载
payload_json = generate_map_json(input_data)
```

---

## Package Layout / 包目录结构

- `sts_map/domain`: enums, core models, runtime state
- `sts_map/config`: config schema
- `sts_map/generator`: topology and room generation pipeline
- `sts_map/rules`: act specific rules
- `sts_map/validators`: map validation
- `sts_map/io`: serialization helpers
- `sts_map/api`: public entrypoint

## Related Documents / 相关文档
- JSON Schema Reference: [doc/JSON_SCHEMA.md](doc/JSON_SCHEMA.md)
- Versioning & Migration: [doc/VERSIONING.md](doc/VERSIONING.md)
