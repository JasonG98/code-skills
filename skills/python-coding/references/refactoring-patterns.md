# 常见重构模式

本指南展示了常见的代码异味以及如何按照 Python 最佳实践进行重构。

## 1. 提取函数

**适用场景**：函数过长或承担多个职责

**重构前：**
```python
def process_order(order_data):
    # 验证订单
    if not order_data.get("items"):
        raise ValueError("订单中没有商品")
    if order_data["total"] <= 0:
        raise ValueError("订单金额无效")

    # 计算税费
    subtotal = sum(item["price"] * item["qty"] for item in order_data["items"])
    tax_rate = 0.08 if order_data["state"] == "CA" else 0.05
    tax = subtotal * tax_rate

    # 处理支付
    payment_method = order_data["payment_method"]
    if payment_method == "credit_card":
        # 处理信用卡支付
        pass
    elif payment_method == "paypal":
        # 处理 PayPal 支付
        pass

    # 发送确认邮件
    email = order_data["customer_email"]
    subject = "订单确认"
    body = f"您的订单总计 ${subtotal + tax} 已确认"
    # 发送邮件代码
```

**重构后：**
```python
def process_order(order_data: dict) -> None:
    validate_order(order_data)
    tax = calculate_tax(order_data)
    process_payment(order_data)
    send_confirmation(order_data, tax)

def validate_order(order_data: dict) -> None:
    if not order_data.get("items"):
        raise ValueError("订单中没有商品")
    if order_data["total"] <= 0:
        raise ValueError("订单金额无效")

def calculate_tax(order_data: dict) -> float:
    subtotal = sum(item["price"] * item["qty"] for item in order_data["items"])
    tax_rate = 0.08 if order_data["state"] == "CA" else 0.05
    return subtotal * tax_rate

def process_payment(order_data: dict) -> None:
    processor = get_payment_processor(order_data["payment_method"])
    processor.process(order_data)

def send_confirmation(order_data: dict, tax: float) -> None:
    subtotal = sum(item["price"] * item["qty"] for item in order_data["items"])
    send_email(
        to=order_data["customer_email"],
        subject="订单确认",
        body=f"您的订单总计 ${subtotal + tax} 已确认"
    )
```

## 2. 用数据类替代字典

**适用场景**：使用字典表示结构化数据时

**重构前：**
```python
def create_user(name: str, email: str, age: int) -> dict:
    return {
        "name": name,
        "email": email,
        "age": age,
        "created_at": datetime.now(),
        "is_active": True
    }

def get_user_display_name(user: dict) -> str:
    return f"{user['name']} ({user['email']})"

# 使用时没有类型安全，容易出错
user = create_user("Alice", "alice@example.com", 30)
print(user["nama"])  # 拼写错误，运行时才报错
```

**重构后：**
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    name: str
    email: str
    age: int
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def display_name(self) -> str:
        return f"{self.name} ({self.email})"

# 使用时有类型安全，IDE 可自动补全
user = User("Alice", "alice@example.com", 30)
print(user.display_name())
# user.nama  # IDE 立即发现拼写错误
```

## 3. 用常量替代魔法数字

**适用场景**：代码中出现没有上下文的数字时

**重构前：**
```python
def calculate_shipping(weight: float) -> float:
    if weight < 5:
        return 5.99
    elif weight < 20:
        return 12.99
    else:
        return 19.99

def is_heavy_package(weight: float) -> bool:
    return weight > 20
```

**重构后：**
```python
# 常量模块或文件顶部
LIGHT_PACKAGE_MAX_WEIGHT = 5
MEDIUM_PACKAGE_MAX_WEIGHT = 20
LIGHT_SHIPPING_COST = 5.99
MEDIUM_SHIPPING_COST = 12.99
HEAVY_SHIPPING_COST = 19.99

def calculate_shipping(weight: float) -> float:
    if weight < LIGHT_PACKAGE_MAX_WEIGHT:
        return LIGHT_SHIPPING_COST
    elif weight < MEDIUM_PACKAGE_MAX_WEIGHT:
        return MEDIUM_SHIPPING_COST
    else:
        return HEAVY_SHIPPING_COST

def is_heavy_package(weight: float) -> bool:
    return weight > MEDIUM_PACKAGE_MAX_WEIGHT
```

## 4. 用多态替代条件判断

**适用场景**：基于类型的长 if/elif 链

**重构前：**
```python
def process_payment(payment_type: str, amount: float) -> str:
    if payment_type == "credit_card":
        # 信用卡处理逻辑
        fee = amount * 0.029
        return f"通过信用卡处理 ${amount}（手续费：${fee}）"
    elif payment_type == "paypal":
        # PayPal 处理逻辑
        fee = amount * 0.034
        return f"通过 PayPal 处理 ${amount}（手续费：${fee}）"
    elif payment_type == "bank_transfer":
        # 银行转账逻辑
        fee = 2.50
        return f"通过银行转账处理 ${amount}（手续费：${fee}）"
    else:
        raise ValueError(f"未知的支付类型：{payment_type}")
```

**重构后：**
```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def calculate_fee(self, amount: float) -> float:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    def process(self, amount: float) -> str:
        fee = self.calculate_fee(amount)
        return f"通过{self.get_name()}处理 ${amount}（手续费：${fee}）"

class CreditCardProcessor(PaymentProcessor):
    def calculate_fee(self, amount: float) -> float:
        return amount * 0.029

    def get_name(self) -> str:
        return "信用卡"

class PayPalProcessor(PaymentProcessor):
    def calculate_fee(self, amount: float) -> float:
        return amount * 0.034

    def get_name(self) -> str:
        return "PayPal"

class BankTransferProcessor(PaymentProcessor):
    def calculate_fee(self, amount: float) -> float:
        return 2.50

    def get_name(self) -> str:
        return "银行转账"

# 工厂
def get_payment_processor(payment_type: str) -> PaymentProcessor:
    processors = {
        "credit_card": CreditCardProcessor,
        "paypal": PayPalProcessor,
        "bank_transfer": BankTransferProcessor,
    }
    if payment_type not in processors:
        raise ValueError(f"未知的支付类型：{payment_type}")
    return processors[payment_type]()

# 使用示例
processor = get_payment_processor("paypal")
result = processor.process(100.0)
```

## 5. 用推导式替代循环

**适用场景**：通过简单转换构建列表/字典时

**重构前：**
```python
# 构建列表
result = []
for item in items:
    if item.is_active:
        result.append(item.name.upper())

# 构建字典
user_map = {}
for user in users:
    user_map[user.id] = user.name

# 过滤
active_users = []
for user in users:
    if user.is_active and user.age >= 18:
        active_users.append(user)
```

**重构后：**
```python
# 列表推导式
result = [item.name.upper() for item in items if item.is_active]

# 字典推导式
user_map = {user.id: user.name for user in users}

# 使用推导式过滤
active_users = [user for user in users if user.is_active and user.age >= 18]

# 复杂条件可使用 filter()
def is_eligible(user):
    return user.is_active and user.age >= 18

active_users = list(filter(is_eligible, users))
```

## 6. 用对象替代参数列表

**适用场景**：函数参数过多（>5个）时

**重构前：**
```python
def send_email(
    to: str,
    subject: str,
    body: str,
    cc: list = None,
    bcc: list = None,
    attachments: list = None,
    priority: int = 1,
    html: bool = False,
    reply_to: str = None
) -> None:
    # 发送邮件逻辑
    pass

# 调用冗长且容易出错
send_email(
    "user@example.com",
    "你好",
    "邮件正文",
    None,
    None,
    None,
    1,
    True,
    "noreply@example.com"
)
```

**重构后：**
```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class EmailConfig:
    to: str
    subject: str
    body: str
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    priority: int = 1
    html: bool = False
    reply_to: Optional[str] = None

def send_email(config: EmailConfig) -> None:
    # 发送邮件逻辑
    pass

# 清晰、自文档化
config = EmailConfig(
    to="user@example.com",
    subject="你好",
    body="邮件正文",
    html=True,
    reply_to="noreply@example.com"
)
send_email(config)
```

## 7. 用枚举替代字符串类型码

**适用场景**：使用字符串表示固定值集合时

**重构前：**
```python
def get_user_permissions(role: str) -> list:
    if role == "admin":
        return ["read", "write", "delete", "manage_users"]
    elif role == "moderator":
        return ["read", "write", "delete"]
    elif role == "user":
        return ["read", "write"]
    else:
        return ["read"]

# 容易拼写错误
permissions = get_user_permissions("admim")  # 拼写错误，返回只读权限
```

**重构后：**
```python
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

def get_user_permissions(role: UserRole) -> list[str]:
    permissions_map = {
        UserRole.ADMIN: ["read", "write", "delete", "manage_users"],
        UserRole.MODERATOR: ["read", "write", "delete"],
        UserRole.USER: ["read", "write"],
        UserRole.GUEST: ["read"],
    }
    return permissions_map[role]

# 类型安全，IDE 可自动补全
permissions = get_user_permissions(UserRole.ADMIN)
# permissions = get_user_permissions("admim")  # IDE/mypy 捕获类型错误
```

## 8. 用卫语句替代嵌套条件

**适用场景**：深层嵌套使代码难以阅读时

**重构前：**
```python
def process_payment(user, amount):
    if user is not None:
        if user.is_active:
            if user.has_valid_payment_method():
                if amount > 0:
                    if amount <= user.balance:
                        # 实际处理支付
                        user.balance -= amount
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False
```

**重构后：**
```python
def process_payment(user: User, amount: float) -> bool:
    # 卫语句 - 提前返回
    if user is None:
        return False

    if not user.is_active:
        return False

    if not user.has_valid_payment_method():
        return False

    if amount <= 0:
        return False

    if amount > user.balance:
        return False

    # 主逻辑在最小嵌套层级
    user.balance -= amount
    return True
```

## 9. 用依赖注入替代全局变量

**适用场景**：使用全局变量存储配置或服务时

**重构前：**
```python
# 全局状态
DATABASE_URL = "postgresql://localhost/mydb"
EMAIL_API_KEY = "secret_key"

class UserService:
    def create_user(self, data: dict) -> User:
        # 使用全局变量
        db = connect(DATABASE_URL)
        user = db.save(User(**data))

        # 发送欢迎邮件
        email_client = EmailClient(EMAIL_API_KEY)
        email_client.send(user.email, "欢迎")

        return user
```

**重构后：**
```python
from dataclasses import dataclass

@dataclass
class Config:
    database_url: str
    email_api_key: str

class Database:
    def __init__(self, url: str):
        self.url = url

    def save(self, entity): ...

class EmailClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, to: str, subject: str): ...

class UserService:
    def __init__(self, db: Database, email_client: EmailClient):
        self.db = db
        self.email_client = email_client

    def create_user(self, data: dict) -> User:
        user = self.db.save(User(**data))
        self.email_client.send(user.email, "欢迎")
        return user

# 应用启动时进行依赖注入
config = Config(
    database_url="postgresql://localhost/mydb",
    email_api_key="secret_key"
)
db = Database(config.database_url)
email_client = EmailClient(config.email_api_key)
user_service = UserService(db, email_client)
```

## 10. 用管道替代方法链

**适用场景**：长链式转换时

**重构前：**
```python
# 难以阅读、调试和测试
result = (
    data_source
    .filter(lambda x: x.is_active)
    .map(lambda x: x.normalize())
    .filter(lambda x: x.is_valid())
    .map(lambda x: x.transform())
    .reduce(lambda acc, x: acc + x.value, 0)
)
```

**重构后：**
```python
from typing import Callable, TypeVar, Iterable

T = TypeVar('T')
U = TypeVar('U')

def pipe(*functions: Callable) -> Callable:
    """从左到右组合函数。"""
    def inner(arg):
        result = arg
        for func in functions:
            result = func(result)
        return result
    return inner

# 独立、可测试的函数
def filter_active(items: Iterable[T]) -> list[T]:
    return [x for x in items if x.is_active]

def normalize_all(items: Iterable[T]) -> list[T]:
    return [x.normalize() for x in items]

def filter_valid(items: Iterable[T]) -> list[T]:
    return [x for x in items if x.is_valid()]

def transform_all(items: Iterable[T]) -> list[T]:
    return [x.transform() for x in items]

def sum_values(items: Iterable) -> float:
    return sum(x.value for x in items)

# 清晰、可测试的管道
process = pipe(
    filter_active,
    normalize_all,
    filter_valid,
    transform_all,
    sum_values
)

result = process(data_source)
```

## 11. 用组合替代继承

**适用场景**：深层继承层次时

**重构前：**
```python
class Animal:
    def eat(self): ...
    def sleep(self): ...

class Mammal(Animal):
    def give_birth(self): ...

class Dog(Mammal):
    def bark(self): ...

class GermanShepherd(Dog):
    def guard(self): ...

# 问题：
# - 紧耦合
# - 无法在运行时改变行为
# - 多重继承冲突
```

**重构后：**
```python
from dataclasses import dataclass

# 行为作为独立类
class Eater:
    def eat(self): ...

class Sleeper:
    def sleep(self): ...

class Barker:
    def bark(self): ...

class Guardian:
    def guard(self): ...

# 组合
@dataclass
class Dog:
    eater: Eater
    sleeper: Sleeper
    barker: Barker

    def eat(self): self.eater.eat()
    def sleep(self): self.sleeper.sleep()
    def bark(self): self.barker.bark()

@dataclass
class GermanShepherd:
    dog: Dog
    guardian: Guardian

    # 委托给组合对象
    def eat(self): self.dog.eat()
    def sleep(self): self.dog.sleep()
    def bark(self): self.dog.bark()
    def guard(self): self.guardian.guard()

# 优点：
# - 灵活组合
# - 易于测试
# - 可在运行时切换行为
```

## 12. 用函数名替代注释

**适用场景**：注释解释代码做了什么时

**重构前：**
```python
# 检查用户是否符合折扣条件
if user.age >= 65 or user.is_student or user.purchases > 10:
    discount = 0.15
```

**重构后：**
```python
def is_eligible_for_discount(user: User) -> bool:
    return user.age >= 65 or user.is_student or user.purchases > 10

if is_eligible_for_discount(user):
    discount = 0.15
```

## 重构的一般流程

1. **识别异味** - 什么使代码难以理解/修改？
2. **编写测试** - 确保现有行为被覆盖
3. **小步修改** - 以微小、安全的步骤重构
4. **运行测试** - 每步后验证行为未改变
5. **频繁提交** - 需要时易于回滚
6. **审查** - 重构后的代码是否更清晰？

## 何时不应该重构

- 正在赶截止日期且代码能正常工作
- 代码计划被删除
- 会破坏现有 API 契约
- 性能关键部分（先进行性能分析）
- 需求不明确（等待明确后再说）

记住：**重构应该让代码更简单，而不是更复杂。**