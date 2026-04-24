## 一、基础全局定义

### 1.1 基础环境

杀戮尖塔 1 代采用 **Java + FlooribGDX** 开发，地图为**纵向分层网格拓扑结构**；
STS Map指在为python版本杀戮尖塔模拟器编写一个地图生成工具，使用python开发

### 1.2 阶段划分

游戏分为**三大常规幕 + 一个隐藏终焉幕**：

1. 第一幕 Act1：森林
2. 第二幕 Act2：都市 / 监狱
3. 第三幕 Act3：深渊 / 核心
4. 第四幕 Act4：终焉（腐化之心，需三钥匙解锁）

### 1.3 核心术语

- **Floor（层级 / 行）**：地图纵向层数，玩家从上至下推进；
- **Room Node（房间节点）**：单层内横向排列的可选择房间；
- **Edge（连通边）**：上下层房间的可行走连接，是路线的核心；
- **原生路径**：算法预生成的完整贯通整幕的固定路线。

### 1.4 标准层数（核心纠正：全网普遍错误）

三大常规幕**每幕固定 16 个地图层级**（Floor 0 ~ Floor 15）：

1. Floor 0：出生起始层

2. Floor 14：全幕强制保底层（休息节点）

3. Floor 15：本幕最终 Boss 层

   

   三幕合计：48层常规地图；

   

   Act4 终焉幕为独立短地图，无随机生成逻辑。

------

## 二、地图拓扑结构生成规则（网格 + 路径）

### 2.1 单层节点数量约束

每一个纵向层级，横向生成**3~5 个房间节点**，随机取值；

同幕内层数越高，单层房间数量小幅收敛，避免后期路线过于分散。

### 2.2 上下层邻接硬性连接规则（不可突破）

任意下层房间，**仅允许与上层三个相邻房间建立连接**：

- 左上节点、正上节点、右上节点

- 禁止跨层连接、禁止隔位连接、禁止反向越级连接

  

  该规则是尖塔地图 “三角递进结构” 的核心。

### 2.3 路径生成规则

1. 每一幕地图生成 **4~6 条贯穿全幕的主路径**，从起始层贯通至 Boss 层；
2. 强制约束：至少保留**2 个不同起始节点**；前两条主路径必须选用不同起点，保证开局路线多样性。
3. 连线交叉约束：**几何意义上的线段交叉严格禁止**；不同路径允许在同一节点发生分支或汇聚（这不视为交叉）。
4. 单节点负载限制：一个上层节点最多向下连接 **2 个下层节点**，一个下层节点最多从上层接收 **2 条入边**，防止路线过度集中或结构畸形。
5. 连通性保障：所有主路径必须全程连通，无断层、无跳跃。

### 2.4 孤立节点剔除

路径生成完成后，执行全局裁剪：

- 无**入边**、无**出边**的孤立房间节点直接删除；
- 保证所有可显示房间都处于有效路线中，无死胡同孤立点。

------

## 三、房间类型基础规则

### 3.1 官方原生房间类型

1.战斗节点

2.精英节点

3.随机节点

4.商店节点

5.休息节点

6.宝藏节点

7.Boss节点

### 3.2 分层禁用黑名单（硬编码）

为控制难度曲线，低层数强制屏蔽高压力 / 高收益房间：

1. Floor 1~3：禁止生成精英节点；
2. Floor 1~5：禁止生成休息节点；
3. Floor 13：禁止生成休息节点；

### 3.3 连续房间禁止规则（防数值失衡）

同一路径的连续可选择节点，**禁止连续出现同类特殊房间**：

- 禁止连续休息、禁止连续精英、禁止连续商店；
- 普通战斗、事件不受连续限制。

### 3.4 全幕强制保底固定房间（核心核心机制）

1. **每幕 Floor14（Boss 前一层）**：**强制固定为休息休息房**，无视随机权重、无视禁用规则；
2. **每幕 Floor15（最终层）**：强制固定为 Boss 战斗房，不可替换、不可跳过；

### 3.5 全局保底补全机制

算法生成结束后强制校验补全，避免极端坏图：

1. 每一幕**至少刷新 1 个商店**；
2. 每一幕**至少刷新 2 个精英房间**；
3. 若随机结果不满足，自动将多余普通战斗强制替换为缺失房型。

------

## 四、节点生成权重，随机节点内容修正与难度修正

尖塔地图并非百分比概率，而是**权重随机抽取**，为原版精准逻辑。

### 4.1 进阶 0（A0 初始难度）基础权重

生成权重战斗节点：55

生成权重精英节点：8

生成权重随机节点：22

生成权重商店节点：10

生成权重宝藏节点：7

### 4.2 进阶难度全局修正（A1~A20）

随着进阶等级提升，难度线性平衡调整：

1. 普通战斗权重逐步降低，A20 最终降至 **45**；每升一级难度降低0.5权重
2. 精英战斗权重逐步提升，A20 最终提升至 **18**；每升一级难度提高0.5权重
3. 事件、商店、休息权重**全程保持不变**。

### 4.3 随机节点特殊动态修正

随机节点存在**空事件惩罚累加机制**：

随机节点中实际可出现战斗节点，精英节点，商店节点，宝藏节点和事件节点（随机节点独有事件节点）。但随机节点统一展示为随机节点图标

战斗初始概率10%，宝藏初始概率2%，商店初始概率3%，事件初始概率85%

1. 若进入随机节点后未触发战斗、商店、宝藏、精英等特殊内容；
2. 下一个随机节点的特殊内容触发权重**增加基础值**；例如访问随机节点为事件节点，则下一次访问随机节点时战斗出现概率+10%，宝藏+2%，商店+3%，事件-15%
3. 一旦触发特殊内容（战斗，宝藏，商店），所有累加权重立即归零重置。

------

## 五、部分生成专属规则

### 5.1 Act1~Act2 特殊精英节点

在Act1固定替换一个已经生成的精英节点变为特殊精英节点，如果玩家在Act1没有访问该节点，则在Act2重复该行为直到玩家访问特殊精英节点

### 5.2Act4 终焉・腐化之心（无随机生成）

完全放弃随机地图算法，为**纯固定线性地图**，无任何随机节点：

1. 第一层：休息节点

2. 第二层：商店节点

3. 第三层：精英节点

4. 第四层：Boss节点

   额外限制：Act4 默认完全禁止随机节点

------

## 六、生成流程完整时序（标准化流程）

### 6.1 统一输入

输入参数：`act_id`、`ascension`、`seed`、`rule_version`。

所有随机行为必须仅由 `seed` 派生的统一 RNG 驱动，保证可重放。

### 6.2 阶段 A：拓扑生成（仅做结构，不分配房型）

1. 生成每层节点数（3~5，按层高收敛）；
2. 生成 4~6 条主路径并确保至少 2 个不同起点；
3. 连接时执行邻接约束（仅左上/正上/右上）；
4. 执行几何交叉检测，禁止线段交叉；
5. 应用节点负载限制（入边/出边上限均为 2）；
6. 删除孤立节点并复检全局连通性。

阶段 A 输出：合法有向分层图（不含房型）。

### 6.3 阶段 B：房型分配（仅做房型，不改拓扑）

1. 按权重初分配房型；
2. 应用分层黑名单；
3. 应用连续房型禁用；
4. 强制覆盖 Floor14=休息、Floor15=Boss；
5. 执行幕内保底补全（商店>=1，精英>=2）。

阶段 B 输出：拓扑不变、房型合法的地图。

### 6.4 阶段 C：随机节点内容解析（运行期/访问时）

1. 随机节点外显统一为“随机”；
2. 访问时再根据动态权重解析为事件/战斗/商店/宝藏/精英；
3. 若命中事件则累计惩罚，若命中特殊内容则清零累计。

阶段 C 输出：访问结果与更新后的随机节点状态。

### 6.5 阶段 D：Act 特殊规则

1. Act1 特殊精英替换；
2. 若未访问则 Act2 继续投放直到访问；
3. Act4 使用固定线性模板，跳过 A/B/C 随机流程。

### 6.6 阶段 E：统一校验与导出

1. 结构校验：邻接合法、无几何交叉、主路径数量合法、连通合法；
2. 规则校验：黑名单、强制层、保底数量全部满足；
3. 统计校验：多 seed 抽样分布在阈值内；
4. 导出：序列化为 JSON 供模拟器消费。

------

## 七、风险修正与工程化规范（新增）

### 7.1 交叉语义消歧规范

为避免“边不允许交叉”与“路径可合理交叉”冲突，统一采用以下定义：

1. **交叉（禁止）**：两条边在非端点位置发生几何相交，记为非法；
2. **汇聚/分支（允许）**：两条及以上路径共享同一节点或在同一节点分叉，记为合法；
3. **判定优先级**：先判定是否共享端点；若非共享端点再做线段相交判定。

工程落地要求：拓扑构建器内置 `edge_intersection_check`，在每次加边时实时校验。

### 7.2 职责解耦规范

禁止将“拓扑生成 + 房型分配 + 随机节点解析”写入单一流程函数。统一拆分为独立模块：

1. `topology_builder`：只负责图结构；
2. `room_allocator`：只负责静态房型；
3. `random_room_resolver`：只负责随机节点访问解析；
4. `rule_engine`：按 Act/难度装配规则；
5. `map_validator`：统一验证入口。

模块边界要求：

1. 上游模块不得直接修改下游运行态状态；
2. 允许通过不可变数据对象传递结果；
3. 任何“修复”行为必须记录修复原因与前后差异。

### 7.3 可验证性规范

建立三层验证体系：

1. **单次生成硬约束验证**
   - Floor14 必为休息、Floor15 必为 Boss；
   - 禁用层不出现被禁房型；
   - 邻接/交叉/负载约束全部满足。

2. **统计分布验证（回归）**
   - 在固定参数下抽样 N>=500 张图；
   - 核对房型占比区间、精英/商店出现率、随机节点解析曲线；
   - 偏差超阈值即判定失败。

3. **可重放验证**
   - 相同 seed + 相同规则版本，生成结果必须字节级一致；
   - 规则版本变化后允许结果变化，但必须可追踪版本号。

建议阈值（初版）：

1. 关键房型占比偏差不超过目标值的 ±5%；
2. 保底规则命中率必须为 100%；
3. 非法图（断路/交叉/越级）比例必须为 0%。

### 7.4 规则版本化规范

新增 `rule_version` 字段，任何规则修改都必须升级版本并记录变更说明。推荐格式：

`MAJOR.MINOR.PATCH`

1. MAJOR：结构性规则变化（如邻接规则变动）；
2. MINOR：权重、阈值、补全策略调整；
3. PATCH：文字修订、无行为影响。

------

## 八、Python 接口与类设计清单（函数签名级别）

### 8.1 推荐包结构（与职责解耦规范一致）

```text
sts_map/
  domain/
   enums.py
   models.py
   state.py
  config/
   schema.py
  generator/
   topology_builder.py
   room_allocator.py
   random_room_resolver.py
   pipeline.py
  rules/
   rule_engine.py
  validators/
   map_validator.py
  io/
   serializer.py
```

### 8.2 枚举与基础类型

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence


class ActId(str, Enum):
   ACT1 = "act1"
   ACT2 = "act2"
   ACT3 = "act3"
   ACT4 = "act4"


class RoomType(str, Enum):
   MONSTER = "monster"
   ELITE = "elite"
   EVENT = "event"           # 随机节点展开后的事件
   QUESTION = "question"     # 地图显示用随机节点
   SHOP = "shop"
   REST = "rest"
   TREASURE = "treasure"
   BOSS = "boss"
   SPECIAL_ELITE = "special_elite"
```

### 8.3 核心数据模型

```python
@dataclass(frozen=True, slots=True)
class NodeId:
   floor: int
   x: int


@dataclass(frozen=True, slots=True)
class Edge:
   src: NodeId
   dst: NodeId


@dataclass(slots=True)
class RoomNode:
   id: NodeId
   room_type: RoomType | None = None
   display_type: RoomType = RoomType.QUESTION


@dataclass(slots=True)
class MapGraph:
   act_id: ActId
   nodes_by_floor: dict[int, list[RoomNode]]
   edges: list[Edge]


@dataclass(frozen=True, slots=True)
class GenerationInput:
   act_id: ActId
   ascension: int
   seed: int
   rule_version: str


@dataclass(slots=True)
class GenerationContext:
   rng_seed: int
   input: GenerationInput
   metadata: dict[str, str] = field(default_factory=dict)
```

### 8.4 规则配置对象

```python
@dataclass(frozen=True, slots=True)
class RoomWeightConfig:
   monster: float
   elite: float
   question: float
   shop: float
   treasure: float


@dataclass(frozen=True, slots=True)
class RandomRoomDynamicWeight:
   fight_base: float = 10.0
   treasure_base: float = 2.0
   shop_base: float = 3.0
   event_base: float = 85.0


@dataclass(frozen=True, slots=True)
class ActRuleConfig:
   floor_count: int
   min_paths: int
   max_paths: int
   min_nodes_per_floor: int
   max_nodes_per_floor: int
   force_floor14_rest: bool
   force_floor15_boss: bool
   min_shop_count: int
   min_elite_count: int
```

### 8.5 拓扑生成接口

```python
class TopologyBuilder:
   def build(self, ctx: GenerationContext, cfg: ActRuleConfig) -> MapGraph:
      ...

   def sample_floor_node_count(self, floor: int, cfg: ActRuleConfig) -> int:
      ...

   def generate_main_paths(self, graph: MapGraph, min_paths: int, max_paths: int) -> list[list[NodeId]]:
      ...

   def can_connect(self, src: NodeId, dst: NodeId) -> bool:
      ...

   def would_intersect(self, existing_edges: Sequence[Edge], candidate: Edge) -> bool:
      ...

   def enforce_node_load_limits(self, graph: MapGraph, max_in: int = 2, max_out: int = 2) -> None:
      ...

   def prune_isolated_nodes(self, graph: MapGraph) -> None:
      ...
```

### 8.6 房型分配接口

```python
class RoomAllocator:
   def allocate(self, graph: MapGraph, ctx: GenerationContext, cfg: ActRuleConfig, weights: RoomWeightConfig) -> None:
      ...

   def assign_by_weight(self, graph: MapGraph, weights: RoomWeightConfig, ascension: int) -> None:
      ...

   def apply_floor_blacklist(self, graph: MapGraph) -> None:
      ...

   def apply_consecutive_constraints(self, graph: MapGraph) -> None:
      ...

   def force_key_floors(self, graph: MapGraph) -> None:
      ...

   def repair_minimum_requirements(self, graph: MapGraph, min_shop: int, min_elite: int) -> None:
      ...
```

### 8.7 随机节点解析接口（运行期）

```python
@dataclass(slots=True)
class RandomRoomState:
   pity_fight: float = 0.0
   pity_treasure: float = 0.0
   pity_shop: float = 0.0
   pity_event: float = 0.0


@dataclass(frozen=True, slots=True)
class RandomResolveResult:
   resolved_type: RoomType
   next_state: RandomRoomState


class RandomRoomResolver:
   def resolve(self, state: RandomRoomState, dyn: RandomRoomDynamicWeight, rng_seed: int) -> RandomResolveResult:
      ...

   def compute_current_weights(self, state: RandomRoomState, dyn: RandomRoomDynamicWeight) -> Mapping[RoomType, float]:
      ...

   def on_event_hit(self, state: RandomRoomState, dyn: RandomRoomDynamicWeight) -> RandomRoomState:
      ...

   def on_special_hit(self, state: RandomRoomState) -> RandomRoomState:
      ...
```

### 8.8 规则引擎接口（Act 特化与扩展）

```python
class RuleEngine:
   def apply_act_specific_rules(self, graph: MapGraph, ctx: GenerationContext) -> None:
      ...

   def apply_act1_special_elite(self, graph: MapGraph, visited_special_elite: bool) -> None:
      ...

   def build_fixed_act4_map(self, ctx: GenerationContext) -> MapGraph:
      ...
```

### 8.9 校验与验收接口

```python
@dataclass(frozen=True, slots=True)
class ValidationIssue:
   code: str
   message: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
   ok: bool
   issues: tuple[ValidationIssue, ...]


class MapValidator:
   def validate_all(self, graph: MapGraph, ctx: GenerationContext, cfg: ActRuleConfig) -> ValidationReport:
      ...

   def validate_structure(self, graph: MapGraph) -> list[ValidationIssue]:
      ...

   def validate_room_rules(self, graph: MapGraph, cfg: ActRuleConfig) -> list[ValidationIssue]:
      ...

   def validate_distribution(self, samples: Sequence[MapGraph]) -> list[ValidationIssue]:
      ...

   def validate_reproducibility(self, input_data: GenerationInput) -> list[ValidationIssue]:
      ...
```

### 8.10 对外入口接口

```python
class MapGenerationService:
   def generate(self, input_data: GenerationInput) -> MapGraph:
      ...

   def generate_many(self, input_list: Iterable[GenerationInput]) -> list[MapGraph]:
      ...
```

```python
def generate_map(input_data: GenerationInput) -> MapGraph:
   """对外单函数入口，内部串联 TopologyBuilder -> RoomAllocator -> RuleEngine -> MapValidator。"""
   ...
```

### 8.11 最小实现顺序（按可运行优先）

1. `domain`：先落 `NodeId/Edge/MapGraph/GenerationInput`；
2. `generator.topology_builder`：先保证合法图生成；
3. `generator.room_allocator`：补房型规则与保底修复；
4. `validators.map_validator`：先做硬约束校验；
5. `generator.pipeline` + `api`：打通单入口；
6. `random_room_resolver` 与 `rule_engine`：最后接入动态与 Act 特化。