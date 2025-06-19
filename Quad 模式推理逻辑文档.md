# Quad 模式推理逻辑文档

> 本文档说明 `mine_sweeper_quad` 类中相较基础模式新增的推理逻辑与方法。
> 基础模式的推理函数请参考《推理函数逻辑详解.md》。

---

## 一、Quad 模式概述

Quad 模式在基础模式的数字提示规则之上，新增了以下约束：

> **规则：任意 2×2 的连续区域中，必须至少包含一个雷。**

这使得原有的推理策略需要结合更大尺度的块状信息进行判断。

---

## 二、新增状态变量

- `legal_quad_map`：
  - 与地图大小相同，标记每个格子所在的 Quad 区域是否合法；
- `legal_quad`：
  - 整张地图是否满足所有 2×2 的 Quad 区域约束；

---

## 三、新增方法说明

### 1. `quad_around(coord)`
```python
def quad_around(self, coord: np.ndarray) -> List[np.ndarray]
```
- 返回包含该格子的所有 2×2 区域中的格子坐标（每个区域以四个格子为一组，打平成一个列表返回）；
- 用于标记需要检查合法性的 Quad 区域集合。


### 2. `is_legal_quad()`
```python
def is_legal_quad(self, quads_to_check=None) -> None
```
- 检查指定的（或所有）2×2 区域是否满足“至少包含一个雷”的规则；
- 不返回值，而是直接更新成员变量 `self.legal_quad`：
  - 若所有已知区域合法且不确定区域仍可能合法，则设为 `POSSIBLE`；
  - 若某个区域已违反约束，则设为 `ILLEGAL`；
  - 若所有区域均满足条件，设为 `LEGAL`；


### 3. `is_legal_quad_recursive()`
```python
def is_legal_quad_recursive(self, remain_coords=None) -> bool
```
- 对所有包含未知格子的 Quad 区域进行递归合法性验证；
- 尝试枚举 HIDDEN 格子作为雷或非雷的可能性，判断是否存在至少一种分布满足所有区域含雷；
- 用于辅助判断 `legal_quad` 是否可以为 `POSSIBLE`，在 update 或 recursion 中提升精度；
- 设计中，这个函数只会在当所有的数字格子的约束都已经被满足了以后才会被调用。


### 4. `first_order_deduct()`（方法扩展）
- 除了执行基础模式的数字格推理外，还额外处理如下 Quad 推理：
  - 若某 2×2 区域中已有 3 个格子为 `NOT_MINE`，则剩余格子必须为 MINE；

若以下 2×2 区域：
```
[-3, -3]
[-3,  M]
```
其中 `M` 为 MINE，其他 3 个格子为 `NOT_MINE`，则该 Quad 区域满足合法性。

但若四个格子都为 `NOT_MINE`，则违反 Quad 规则，状态为 ILLEGAL。

---

## 五、小结

Quad 模式引入了更强的全局约束，使推理变得更加复杂但也更强大。由于区域性信息的引入，该模式尤其适用于“块状”分布明显的地图局面。

未来也可以拓展其他块状约束（如十字形、3×3 区域等）规则，复用当前类结构与策略。

