# ByteLang

Язык для настраиваемых крошечных интерпретаторов инструкций

# Директивы (Ключевые слова)

Являются инструкциями для компилятора определяющие действие над исходным кодом

## Общие Директивы (Generic)

Доступны из любой единицы трансляции

<blockquote>

### Объявление константного выражения

Синтаксис: `const` ID `=` Expr

Пример: `const x = 1 + 2 * 3 # Константное выражение!`

</blockquote>



<blockquote>

### Определение псевдонима типа

Синтаксис: `type` ID `=` TypeID

Пример: `type vec3f = [3]f32`

</blockquote>



<blockquote>

### Определение структуры

Синтаксис: `struct` ID `{` [Field] `}`

Пример: `struct vec2f { x: f32, y: f32 }`

</blockquote>



<blockquote>

### Определение макроса подстановки

Синтаксис: `macro` ID `(` [ID] `)` `->` Expr

Пример: `macro square(x) -> x * x`

</blockquote>

### Директивы пакета (Package)

<blockquote>

### Объявление нативной процедуры

Синтаксис: `fn` ID `(` [Field] `)` `->` TypeID

Пример: `fn add(x: i16, y: i16) -> i16`

</blockquote>

### Директивы окружения (Environment)

<blockquote>

### Использование пакета

Синтаксис: `use` ID

Синтаксис: `use` ID `{` [ID] `}`

Пример:

```
# Расширить реестры данного окружения..


# ..всеми значениями из реестров пакета foo
use foo

# ..только выбранными значениями 
use bar{my_fn_1, my_fn_2, bar_const} 
```

</blockquote>

### Директивы скетча (Sketch)

<blockquote>

### Объявление пользовательской процедуры

Синтаксис: `fn` ID `(` [Field] `)` `->` TypeID `{` [Statement] `}`

Пример:

```
# Получить квадрат числа
fn square(x: *i16) -> i16 {
    push x
    push x
    mul
    
    ret
}
```

</blockquote>



<blockquote>

### Объявление переменной

Синтаксис: `var` Field `=` Expr

Пример: `var x: u8 = (1 << 8) - 1`

</blockquote>



<blockquote>

### Выбор окружения

Синтаксис: `env` ID

Пример: `env example`

</blockquote>
