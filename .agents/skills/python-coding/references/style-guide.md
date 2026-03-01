# Python 风格指南

本文档提供详细的 Python 编码规范和最佳实践，作为 `python-coding` skill 的参考资料。

## 目录

1. [Pythonic 惯用法](#pythonic-惯用法)
2. [类型注解详解](#类型注解详解)
3. [Dataclass 与数据结构](#dataclass-与数据结构)
4. [SOLID 原则](#solid-原则)
5. [设计模式精要](#设计模式精要)
6. [函数式编程](#函数式编程)
7. [测试最佳实践](#测试最佳实践)
8. [现代 Python 特性](#现代-python-特性)
9. [代码异味与反模式](#代码异味与反模式)

---

## Pythonic 惯用法

### 列表推导式

```python
# Good
squares = [x**2 for x in range(10)]
active_users = [u for u in users if u.is_active]

# Bad
squares = []
for x in range(10):
    squares.append(x**2)
```

### enumerate() 替代 range(len())

```python
# Good
for index, item in enumerate(items):
    print(f"{index}: {item}")

# Bad
for i in range(len(items)):
    print(f"{i}: {items[i]}")
```

### Context Manager 管理资源

```python
# Good
with open("file.txt") as f:
    content = f.read()

# Bad
f = open("file.txt")
content = f.read()
f.close()
```

### any() / all() 简化布尔检查

```python
# Good
has_admin = any(user.role == "admin" for user in users)
all_valid = all(is_valid(item) for item in items)

# Bad
has_admin = False
for user in users:
    if user.role == "admin":
        has_admin = True
        break
```

---

## 类型注解详解

### 基础类型

```python
# Python 3.10+ 现代语法
def process(name: str, age: int, scores: list[float]) -> dict[str, float]:
    return {"average": sum(scores) / len(scores)}

# Optional 和 Union
def get_user(id: int) -> User | None:
    return users.get(id)

def format_value(value: int | float | str) -> str:
    return str(value)
```

### TypedDict 结构化字典

```python
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    name: str
    email: str

def create_user(data: UserDict) -> None:
    print(f"Creating: {data['name']}")
```

### Protocol 结构化类型

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

def render(shape: Drawable) -> None:
    shape.draw()  # 接受任何有 draw() 方法的对象
```

### Final 常量

```python
from typing import Final

DATABASE_URL: Final[str] = "postgresql://localhost/mydb"
MAX_RETRIES: Final[int] = 3
```

---

## Dataclass 与数据结构

### 基础用法

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    email: str
    age: int
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.email = self.email.lower()

# 使用
user = User("Alice", "Alice@Example.com", 30)
print(user)  # User(name='Alice', email='alice@example.com', age=30, tags=[])
```

### 不可变对象

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5
```

### Pydantic 数据验证

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    name: str
    email: EmailStr
    age: int

    class Config:
        validate_assignment = True

# 自动验证
user = User(name="Alice", email="invalid", age=30)  # ValidationError
```

---

## SOLID 原则

### S - 单一职责

```python
# Good: 分离职责
class UserRepository:
    def save(self, user: User) -> None: ...

class UserValidator:
    def validate(self, user: User) -> bool: ...

# Bad: 混合职责
class UserManager:
    def save_and_validate(self, user: User) -> None: ...
```

### O - 开闭原则

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount: float) -> None: ...

class CreditCardProcessor(PaymentProcessor):
    def process(self, amount: float) -> None:
        print(f"Processing ${amount} via credit card")

class PayPalProcessor(PaymentProcessor):
    def process(self, amount: float) -> None:
        print(f"Processing ${amount} via PayPal")
```

### D - 依赖倒置

```python
# Good: 依赖抽象
class NotificationService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

# Bad: 依赖具体实现
class NotificationService:
    def __init__(self):
        self.gmail = GmailService()  # 紧耦合
```

---

## 设计模式精要

### 工厂模式

```python
from typing import Protocol

class Exporter(Protocol):
    def export(self, data: str) -> None: ...

class JSONExporter:
    def export(self, data: str) -> None:
        print(f"Exporting to JSON: {data}")

class CSVExporter:
    def export(self, data: str) -> None:
        print(f"Exporting to CSV: {data}")

def create_exporter(format: str) -> Exporter:
    exporters = {"json": JSONExporter, "csv": CSVExporter}
    if format not in exporters:
        raise ValueError(f"Unknown format: {format}")
    return exporters[format]()
```

### 策略模式

```python
from typing import Callable

# 策略作为函数
def export_json(data: dict) -> str:
    import json
    return json.dumps(data)

def export_csv(data: dict) -> str:
    return ",".join(f"{k}={v}" for k, v in data.items())

# 上下文
def process_data(data: dict, strategy: Callable[[dict], str]) -> str:
    return strategy(data)

# 使用
result = process_data({"name": "John"}, export_json)
```

### 依赖注入

```python
class OrderService:
    def __init__(
        self,
        payment: PaymentProcessor,
        inventory: InventoryService,
        notifier: NotificationService
    ):
        self.payment = payment
        self.inventory = inventory
        self.notifier = notifier

    def place_order(self, order: Order) -> None:
        self.inventory.reserve(order.items)
        self.payment.process(order.total)
        self.notifier.notify(order.user, "Order placed")
```

---

## 函数式编程

### 纯函数

```python
# Good: 无副作用
def calculate_tax(price: float, rate: float) -> float:
    return price * rate

# Bad: 修改外部状态
total_tax = 0
def calculate_tax(price: float, rate: float) -> float:
    global total_tax
    tax = price * rate
    total_tax += tax
    return tax
```

### 高阶函数

```python
from typing import Callable

def apply_discount(
    prices: list[float],
    discount_fn: Callable[[float], float]
) -> list[float]:
    return [discount_fn(p) for p in prices]

def ten_percent_off(price: float) -> float:
    return price * 0.9

discounted = apply_discount([100, 200, 300], ten_percent_off)
```

---

## 测试最佳实践

### 可测试代码设计

```python
class UserService:
    def __init__(self, db: Database, validator: Validator):
        self.db = db
        self.validator = validator

    def create_user(self, data: dict) -> User:
        if not self.validator.validate(data):
            raise ValueError("Invalid data")
        return self.db.save(User(**data))
```

### pytest 示例

```python
import pytest

@pytest.fixture
def user_service():
    return UserService(MockDB(), MockValidator())

def test_create_user(user_service):
    user = user_service.create_user({"name": "Alice"})
    assert user.name == "Alice"

@pytest.mark.parametrize("email,valid", [
    ("test@example.com", True),
    ("invalid", False),
])
def test_email_validation(email, valid):
    assert is_valid_email(email) == valid
```

---

## 现代 Python 特性

### 模式匹配 (3.10+)

```python
def process_command(command: dict) -> str:
    match command:
        case {"action": "create", "data": data}:
            return f"Creating: {data}"
        case {"action": "delete", "id": user_id}:
            return f"Deleting {user_id}"
        case _:
            return "Unknown command"
```

### 海象运算符 (3.8+)

```python
# 同时赋值和使用
if (n := len(data)) > 10:
    print(f"Large dataset: {n} items")

# 在推导式中使用
[match.group(0) for line in file if (match := pattern.search(line))]
```

### 字典合并 (3.9+)

```python
defaults = {"timeout": 30, "retries": 3}
config = {"timeout": 60}
final = defaults | config  # {"timeout": 60, "retries": 3}
config |= {"new_key": "value"}
```

---

## 代码异味与反模式

### 常见异味

| 异味 | 解决方案 |
|------|----------|
| 长函数 (>50行) | 提取小函数 |
| 参数过多 (>5个) | 使用 dataclass |
| 深层嵌套 (>3层) | 提前返回/守卫子句 |
| 重复代码 | 提取公共函数 |
| 上帝类 | 拆分职责 |
| 魔法数字 | 命名常量 |
| 布尔标志 | 使用枚举或分离函数 |

### 反模式示例

```python
# God Object
class Application:
    def get_user(self): ...
    def create_order(self): ...
    def send_email(self): ...
    def process_payment(self): ...

# 过早优化
import cython  # 没有测量就添加复杂性

# 硬编码凭证
DB_PASSWORD = "secret123"  # Bad
DB_PASSWORD = os.getenv("DB_PASSWORD")  # Good
```

---

## 自动化工具

推荐使用以下工具自动化检查：

- **ruff**: 快速 linting（替代 flake8, isort）
- **mypy**: 静态类型检查
- **pytest**: 测试框架
- **coverage**: 测试覆盖率
- **pre-commit**: Git hooks 自动检查

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```