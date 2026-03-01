# 设计模式参考

本文档提供了 Python 中常用设计模式的详细实现。

## 创建型模式

### 工厂模式（Factory Pattern）

**适用场景**：当对象创建逻辑复杂或需要集中管理时。

**完整实现**：
```python
from abc import ABC, abstractmethod
from typing import Protocol
from pathlib import Path

# 使用 Protocol 实现鸭子类型
class VideoExporter(Protocol):
    def prepare_export(self, video_data: str) -> None: ...
    def do_export(self, folder: Path) -> None: ...

# 具体实现
class LosslessVideoExporter:
    def prepare_export(self, video_data: str) -> None:
        print("准备视频数据以进行无损导出。")

    def do_export(self, folder: Path) -> None:
        print(f"以无损格式导出视频数据到 {folder}。")

class H264VideoExporter:
    def prepare_export(self, video_data: str) -> None:
        print("准备视频数据以进行 H.264 导出。")

    def do_export(self, folder: Path) -> None:
        print(f"以 H.264 格式导出视频数据到 {folder}。")

# 工厂函数
def create_video_exporter(format: str) -> VideoExporter:
    exporters = {
        "lossless": LosslessVideoExporter,
        "h264": H264VideoExporter,
    }
    if format not in exporters:
        raise ValueError(f"未知格式: {format}")
    return exporters[format]()

# 使用示例
exporter = create_video_exporter("h264")
exporter.prepare_export("video_data")
exporter.do_export(Path("/exports"))
```

### 抽象工厂模式（Abstract Factory Pattern）

**适用场景**：当需要创建一系列相关的对象时。

```python
from abc import ABC, abstractmethod

# 抽象产品
class Button(ABC):
    @abstractmethod
    def click(self) -> str: ...

class Checkbox(ABC):
    @abstractmethod
    def check(self) -> str: ...

# 具体产品 - Windows 风格
class WindowsButton(Button):
    def click(self) -> str:
        return "Windows 按钮被点击"

class WindowsCheckbox(Checkbox):
    def check(self) -> str:
        return "Windows 复选框被选中"

# 具体产品 - Mac 风格
class MacButton(Button):
    def click(self) -> str:
        return "Mac 按钮被点击"

class MacCheckbox(Checkbox):
    def check(self) -> str:
        return "Mac 复选框被选中"

# 抽象工厂
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

# 具体工厂
class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

# 工厂选择器
def get_factory(platform: str) -> GUIFactory:
    factories = {
        "windows": WindowsFactory,
        "mac": MacFactory,
    }
    return factories[platform]()

# 使用示例
factory = get_factory("mac")
button = factory.create_button()
checkbox = factory.create_checkbox()
print(button.click())
print(checkbox.check())
```

### 建造者模式（Builder Pattern）

**适用场景**：当需要逐步构建复杂对象时。

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Pizza:
    size: str
    cheese: bool = False
    pepperoni: bool = False
    mushrooms: bool = False
    olives: bool = False

    def __str__(self) -> str:
        toppings = []
        if self.cheese: toppings.append("奶酪")
        if self.pepperoni: toppings.append("意大利辣肠")
        if self.mushrooms: toppings.append("蘑菇")
        if self.olives: toppings.append("橄榄")
        return f"{self.size}号披萨，配料：{', '.join(toppings)}"

class PizzaBuilder:
    def __init__(self, size: str):
        self.size = size
        self._cheese = False
        self._pepperoni = False
        self._mushrooms = False
        self._olives = False

    def add_cheese(self) -> "PizzaBuilder":
        self._cheese = True
        return self

    def add_pepperoni(self) -> "PizzaBuilder":
        self._pepperoni = True
        return self

    def add_mushrooms(self) -> "PizzaBuilder":
        self._mushrooms = True
        return self

    def add_olives(self) -> "PizzaBuilder":
        self._olives = True
        return self

    def build(self) -> Pizza:
        return Pizza(
            size=self.size,
            cheese=self._cheese,
            pepperoni=self._pepperoni,
            mushrooms=self._mushrooms,
            olives=self._olives
        )

# 使用示例
pizza = (PizzaBuilder("大")
         .add_cheese()
         .add_pepperoni()
         .add_mushrooms()
         .build())
print(pizza)
```

## 行为型模式

### 策略模式（Strategy Pattern）

**适用场景**：当需要在运行时切换多种算法时。

**基于函数的实现方式**（更符合 Python 风格）：
```python
from typing import Callable, List

# 策略作为函数
def bubble_sort(data: List[int]) -> List[int]:
    result = data.copy()
    n = len(result)
    for i in range(n):
        for j in range(0, n-i-1):
            if result[j] > result[j+1]:
                result[j], result[j+1] = result[j+1], result[j]
    return result

def quick_sort(data: List[int]) -> List[int]:
    if len(data) <= 1:
        return data
    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# 上下文
class Sorter:
    def __init__(self, strategy: Callable[[List[int]], List[int]]):
        self.strategy = strategy

    def sort(self, data: List[int]) -> List[int]:
        return self.strategy(data)

# 使用示例
data = [64, 34, 25, 12, 22, 11, 90]
sorter = Sorter(quick_sort)
sorted_data = sorter.sort(data)
print(sorted_data)

# 切换策略
sorter.strategy = bubble_sort
sorted_data = sorter.sort(data)
```

**基于类的实现方式**：
```python
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]: ...

class BubbleSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        # 实现同上
        pass

class QuickSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        # 实现同上
        pass

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort(self, data: List[int]) -> List[int]:
        return self.strategy.sort(data)
```

### 观察者模式（Observer Pattern）

**适用场景**：当一个对象的改变需要通知多个依赖对象时。

```python
from abc import ABC, abstractmethod
from typing import List

# 观察者接口
class Observer(ABC):
    @abstractmethod
    def update(self, temperature: float) -> None: ...

# 被观察者（主题）
class WeatherStation:
    def __init__(self):
        self._observers: List[Observer] = []
        self._temperature: float = 0.0

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self._temperature)

    def set_temperature(self, temperature: float) -> None:
        self._temperature = temperature
        self.notify()

# 具体观察者
class PhoneDisplay(Observer):
    def update(self, temperature: float) -> None:
        print(f"手机显示：当前温度 {temperature}°C")

class WebDisplay(Observer):
    def update(self, temperature: float) -> None:
        print(f"网页显示：当前温度 {temperature}°C")

# 使用示例
station = WeatherStation()
phone = PhoneDisplay()
web = WebDisplay()

station.attach(phone)
station.attach(web)

station.set_temperature(25.5)
station.set_temperature(26.0)
```

### 命令模式（Command Pattern）

**适用场景**：当需要将操作参数化时。

```python
from abc import ABC, abstractmethod
from typing import List

# 命令接口
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...

# 接收者
class Light:
    def __init__(self, location: str):
        self.location = location
        self.is_on = False

    def turn_on(self) -> None:
        self.is_on = True
        print(f"{self.location} 的灯已打开")

    def turn_off(self) -> None:
        self.is_on = False
        print(f"{self.location} 的灯已关闭")

# 具体命令
class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_on()

    def undo(self) -> None:
        self.light.turn_off()

class LightOffCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_off()

    def undo(self) -> None:
        self.light.turn_on()

# 调用者
class RemoteControl:
    def __init__(self):
        self._history: List[Command] = []

    def execute_command(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo_last(self) -> None:
        if self._history:
            command = self._history.pop()
            command.undo()

# 使用示例
living_room_light = Light("客厅")
bedroom_light = Light("卧室")

remote = RemoteControl()
remote.execute_command(LightOnCommand(living_room_light))
remote.execute_command(LightOnCommand(bedroom_light))
remote.undo_last()  # 关闭卧室的灯
```

## 结构型模式

### 适配器模式（Adapter Pattern）

**适用场景**：当需要让不兼容的接口协同工作时。

```python
# 现有接口
class EuropeanSocket:
    def provide_power(self) -> str:
        return "230V"

# 新接口
class USSocket:
    def get_power(self) -> str:
        return "110V"

# 适配器
class SocketAdapter:
    def __init__(self, socket: USSocket):
        self._socket = socket

    def provide_power(self) -> str:
        # 将美国电压转换为欧洲电压
        us_power = self._socket.get_power()
        return f"已将 {us_power} 转换为 230V"

# 使用示例
us_socket = USSocket()
adapter = SocketAdapter(us_socket)
print(adapter.provide_power())
```

### 装饰器模式（Decorator Pattern）

**适用场景**：当需要动态地给对象添加行为时。

```python
from abc import ABC, abstractmethod

# 组件接口
class Coffee(ABC):
    @abstractmethod
    def cost(self) -> float: ...

    @abstractmethod
    def description(self) -> str: ...

# 具体组件
class SimpleCoffee(Coffee):
    def cost(self) -> float:
        return 2.0

    def description(self) -> str:
        return "普通咖啡"

# 装饰器基类
class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee

    def cost(self) -> float:
        return self._coffee.cost()

    def description(self) -> str:
        return self._coffee.description()

# 具体装饰器
class MilkDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 0.5

    def description(self) -> str:
        return f"{self._coffee.description()}，加奶"

class SugarDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 0.2

    def description(self) -> str:
        return f"{self._coffee.description()}，加糖"

# 使用示例
coffee = SimpleCoffee()
print(f"{coffee.description()}：${coffee.cost()}")

coffee = MilkDecorator(coffee)
print(f"{coffee.description()}：${coffee.cost()}")

coffee = SugarDecorator(coffee)
print(f"{coffee.description()}：${coffee.cost()}")
```

### 组合模式（Composite Pattern）

**适用场景**：当需要统一地处理树形结构时。

```python
from abc import ABC, abstractmethod
from typing import List

# 组件
class FileSystemComponent(ABC):
    @abstractmethod
    def get_size(self) -> int: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...

# 叶子节点
class File(FileSystemComponent):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size

    def get_size(self) -> int:
        return self.size

    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"📄 {self.name} ({self.size} 字节)")

# 组合节点
class Directory(FileSystemComponent):
    def __init__(self, name: str):
        self.name = name
        self.children: List[FileSystemComponent] = []

    def add(self, component: FileSystemComponent) -> None:
        self.children.append(component)

    def get_size(self) -> int:
        return sum(child.get_size() for child in self.children)

    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"📁 {self.name}/")
        for child in self.children:
            child.display(indent + 1)

# 使用示例
root = Directory("root")
home = Directory("home")
user = Directory("user")

root.add(home)
home.add(user)
user.add(File("document.txt", 1024))
user.add(File("photo.jpg", 2048))

root.display()
print(f"总大小：{root.get_size()} 字节")
```

## 模式组合

### 工厂 + 策略

```python
from typing import Protocol, Callable

class PaymentStrategy(Protocol):
    def pay(self, amount: float) -> str: ...

class CreditCardPayment:
    def pay(self, amount: float) -> str:
        return f"使用信用卡支付 ${amount}"

class PayPalPayment:
    def pay(self, amount: float) -> str:
        return f"使用 PayPal 支付 ${amount}"

# 工厂
def create_payment_strategy(method: str) -> PaymentStrategy:
    strategies = {
        "credit_card": CreditCardPayment,
        "paypal": PayPalPayment,
    }
    return strategies[method]()

# 使用示例
strategy = create_payment_strategy("paypal")
print(strategy.pay(100.0))
```

## 各模式适用场景

| 模式 | 适用场景 |
|------|----------|
| **工厂模式** | 复杂对象创建、多种类型 |
| **抽象工厂模式** | 一系列相关对象 |
| **建造者模式** | 逐步构建复杂对象 |
| **策略模式** | 可切换的算法 |
| **观察者模式** | 事件通知多个对象 |
| **命令模式** | 操作参数化、撤销/重做 |
| **适配器模式** | 让不兼容接口兼容 |
| **装饰器模式** | 动态添加行为 |
| **组合模式** | 树形结构、统一处理 |

## 需要避免的反模式

1. **过度使用模式** - 简单代码就能解决的问题不要强行使用模式
2. **单例滥用** - 往往暗示全局状态问题
3. **上帝对象** - 一个类/模式承担过多职责
4. **过早抽象** - 等到有 2-3 个相似实现时再抽象