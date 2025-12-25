# ByteLang - Расширенная спецификация с типами, структурами и generic

## 1. Система типов

### 1.1 Базовые типы
```rust
i8, i16, i32, i64     // знаковые целые
u8, u16, u32, u64     // беззнаковые целые  
f32, f64              // числа с плавающей точкой
bool                  // true/false
void                  // отсутствие значения
type                  // тип типов (для метапрограммирования)
```

### 1.2 Производные типы
```rust
// Указатели
const PtrToU8 = *u8
var buffer: *u8 = 0x1000

// Массивы
const Buffer = [256]u8
var data: [10]i32

// Срезы (указатель + длина)
const Slice = []u8
```

## 2. Структуры и методы

### 2.1 Объявление структур
```rust
// Структура с публичными и приватными полями
pub const String = struct {
    // Публичные поля
    pub len: usize,
    
    // Приватные поля (доступны только внутри модуля)
    data: *u8,
    
    // Статические методы (макросы времени компиляции)
    pub macro fn new(source: []const u8) String {
        return String {
            len: source.len,
            data: source.ptr
        }
    }
    
    // Методы экземпляра
    pub fn at(self: *String, index: usize) u8 {
        // self.data[index]
        return 0 // TODO
    }
    
    // Нативные методы (реализованы в интерпретаторе)
    pub fn concat(self: *String, other: *String) void = 0x70
}
```

### 2.2 Использование структур
```rust
// Создание экземпляра
var str: String = String.new("Hello")

// Доступ к полям
var length = str.len

// Вызов методов
var char = str.at(0)
str.concat(&other_str)
```

## 3. Generic (обобщённые типы)

### 3.1 Generic структуры
```rust
// Generic структура - макрос, возвращающий тип
fn macro Point(T: type) type {
    return struct {
        x: T,
        y: T,
        
        // Псевдоним для Self
        const Self = Point(T)
        
        // Статический метод
        pub macro fn zero() Self {
            return Self { x: 0, y: 0 }
        }
        
        // Метод экземпляра
        pub fn distance(self: *Self, other: Self) T {
            // вычисление расстояния
            var dx = self.x - other.x
            var dy = self.y - other.y
            return dx * dx + dy * dy  // квадрат расстояния
        }
    }
}
```

### 3.2 Инстанцирование generic
```rust
// Создание конкретного типа
const PointI32 = Point(i32)
const PointF32 = Point(f32)

// Использование
var p1: Point(i32) = Point(i32).zero()
var p2: Point(i32) = Point(i32){ x: 12, y: 34 }

// Методы
var dist = p1.distance(p2)
```

## 4. Макросы времени компиляции

### 4.1 Макросы функций
```rust
// Макросы выполняются во время компиляции
pub macro fn min(a: comptime_int, b: comptime_int) comptime_int {
    if a < b {
        return a
    } else {
        return b
    }
}

// Использование
const SIZE = min(100, 200)  // вычисляется на этапе компиляции
```

### 4.2 Макросы типов
```rust
// Макрос, создающий тип
fn macro FixedArray(T: type, size: comptime_int) type {
    return struct {
        data: [size]T,
        
        pub fn get(self: *Self, index: usize) T {
            return self.data[index]
        }
    }
}

// Использование
var arr: FixedArray(i32, 10)
```

## 5. Встроенные функции времени компиляции

### 5.1 Интроспекция типов
```rust
// Получение размера типа
comptime fn sizeof(T: type) usize

// Получение выравнивания
comptime fn alignof(T: type) usize

// Проверка равенства типов
comptime fn type_eq(T1: type, T2: type) bool
```

### 5.2 Операции над типами
```rust
// Создание указателя на тип
comptime fn ptr_to(T: type) type

// Создание массива
comptime fn array_of(T: type, size: comptime_int) type
```

## 6. Модель памяти для структур

### 6.1 Размещение в памяти
Структуры размещаются последовательно в памяти:
```
struct Point { x: i32, y: i32 }
Размер: 8 байт
Расположение: [x: i32][y: i32]
```

### 6.2 Передача структур
- **По значению**: копируется всё содержимое
- **По ссылке**: передаётся указатель

## 7. Компиляция методов и generic

### 7.1 Компиляция методов
Методы компилируются как обычные функции с неявным параметром `self`:

```rust
// Метод: fn distance(self: *Point, other: Point) i32
// Компилируется в функцию с сигнатурой:
// fn Point_distance(self: *Point, other: *Point) i32
```

### 7.2 Манглинг имён для generic
```rust
// Point(i32).distance → Point_i32_distance
// Point(f32).zero → Point_f32_zero
```

## 8. Пример полной программы

### 8.1 Модуль `geometry.bl`
```rust
// Generic структура Vector
fn macro Vector(T: type, N: comptime_int) type {
    return struct {
        data: [N]T,
        
        const Self = Vector(T, N)
        
        // Нулевой вектор
        pub macro fn zero() Self {
            var result: Self
            var i = 0
            while i < N {
                result.data[i] = 0
                i = i + 1
            }
            return result
        }
        
        // Сложение векторов
        pub fn add(self: *Self, other: Self) Self {
            var result: Self
            var i = 0
            while i < N {
                result.data[i] = self.data[i] + other.data[i]
                i = i + 1
            }
            return result
        }
        
        // Скалярное произведение (только для N <= 4)
        pub fn dot(self: *Self, other: Self) T {
            var sum: T = 0
            var i = 0
            while i < N {
                sum = sum + self.data[i] * other.data[i]
                i = i + 1
            }
            return sum
        }
    }
}

// Специализированные типы
const Vec2 = Vector(f32, 2)
const Vec3 = Vector(f32, 3)
const Vec4 = Vector(f32, 4)
```

### 8.2 Модуль `main.bl`
```rust
import geometry

// Глобальные переменные
var v1: Vec3 = Vec3.zero()
var v2: Vec3 = Vec3{ data: [1.0, 2.0, 3.0] }
var result: Vec3

// Главная функция
pub fn main() void {
    // v1 = Vec3.zero()
    // v2 = {1, 2, 3}
    
    // result = v1.add(v2)
    result = v1.add(v2)
    
    // Скалярное произведение
    var dot_product: f32
    dot_product = v1.dot(v2)
    
    // Использование специализированных типов
    var vec2_a: Vec2 = Vec2{ data: [1.0, 2.0] }
    var vec2_b: Vec2 = Vec2{ data: [3.0, 4.0] }
    var vec2_sum: Vec2
    
    vec2_sum = vec2_a.add(vec2_b)
}
```

## 9. Байт-код для структур

### 9.1 Представление в байт-коде
```rust
// Создание структуры на стеке
struct Point { x: i32, y: i32 }

// Инициализация:
push_const 0      ; x = 0
push_const 0      ; y = 0
; На стеке: [0, 0] - это и есть структура
```

### 9.2 Доступ к полям
```rust
// Доступ к полю x (смещение 0)
load_param 0      ; если структура передана как параметр

// Доступ к полю y (смещение 4 для i32)
load_param 4
```

## 10. Интерпретатор для структур

### 10.1 Работа с составными типами
Интерпретатор должен знать о размерах и выравнивании типов для корректной работы с памятью.

```c
// В интерпретаторе
typedef struct {
    size_t size;
    size_t alignment;
    TypeKind kind;
    // Для структур: список полей
    // Для указателей: базовый тип
    // Для массивов: тип элемента и размер
} TypeInfo;

// Диспетчеризация операций над типами
void* get_field_ptr(void* struct_ptr, size_t offset) {
    return (uint8_t*)struct_ptr + offset;
}
```

## 11. Ограничения и особенности

### 11.1 Ограничения generic
- Generic могут быть инстанцированы только с константными параметрами времени компиляции
- Нет runtime generic (как в C++ шаблоны, а не как в Java дженерики)

### 11.2 Ограничения макросов
- Макросы выполняются только во время компиляции
- Не могут иметь побочных эффектов в runtime
- Могут генерировать только валидный код ByteLang

### 11.3 Размеры кода
Каждая инстанциация generic создаёт новый код, что может увеличить размер бинарного файла.

## 12. Итог

ByteLang с поддержкой структур, методов и generic предоставляет:

1. **Абстракции данных**: структуры для группировки связанных данных
2. **Полиморфизм**: generic для создания обобщённых типов и алгоритмов
3. **Интроспекцию**: метапрограммирование через макросы времени компиляции
4. **Инкапсуляцию**: контроль доступа через pub/приватные поля

Это превращает ByteLang из простого процедурного языка в язык, способный выражать сложные абстракции, сохраняя при этом контроль над памятью и эффективность выполнения.