# Sesión 21 sep 2026 — Arquitectura modular, Clean Code y SOLID

| Recurso | Fichero |
| --- | --- |
| Demo guiada | [`03_oop_clean_code_solid.py`](03_oop_clean_code_solid.py) |
| Ejercicio de clase | [`ejercicios/E2_arquitectura.md`](ejercicios/E2_arquitectura.md) |
| Datos de ejemplo | [`Datos/ventas.csv`](Datos/ventas.csv) |

Este documento es la **referencia amplia** de la sesión 3: por qué pasar del notebook al paquete, Clean Code, OOP útil, SOLID aplicado a datos + IA, patrones que compensan, anti-patrones, recorrido del demo y checklist hacia el Proyecto I. Puedes usarlo en clase y como manual cuando refactorices pipelines, APIs y el E2E.

---

## 0. Objetivos de aprendizaje

Al terminar esta sesión (y este documento) deberías ser capaz de:

1. Explicar por qué un notebook excelente para explorar suele ser un **mal artefacto de producción**.
2. Aplicar un mínimo de **Clean Code** (nombres, funciones, errores, efectos laterales).
3. Separar responsabilidades en módulos/clases (`loader`, `validator`, `metrics`, `cli`).
4. Nombrar y aplicar los cinco principios **SOLID** con ejemplos de datos e IA.
5. Usar con criterio los patrones **Repository**, **Pipeline stages**, **Strategy** y **Facade**.
6. Leer y extender el demo `03_oop_clean_code_solid.py`.
7. Refactorizar tu Proyecto I hacia un paquete `ventas_app/` ejecutable por CLI.
8. Detectar over-engineering: cuándo un patrón ayuda y cuándo sobra.

---

## 1. Por qué esta sesión importa en DSIA

### 1.1 Qué entregamos en la asignatura

En DSIA no entregamos “un `.ipynb` que me funciona si ejecuto las celdas en el orden correcto”. Entregamos **soluciones** que otra persona debe poder:

1. **clonar**,
2. **instalar** dependencias,
3. **ejecutar** un comando (CLI / job / API),
4. **testear** piezas por separado,
5. **cambiar** un detalle (origen de datos, proveedor de IA) sin reescribirlo todo.

Esa cadena se rompe si:

- la lógica vive mezclada en celdas con estado global,
- no hay fronteras claras entre I/O y reglas de negocio,
- cada cambio toca el mismo “mega-script”,
- no puedes explicar *dónde* vive cada responsabilidad.

### 1.2 Mapa mental del semestre

```text
Sesión 1  →  venv + Git (reproducibilidad)
Sesión 2  →  pandas (procesar datos)
Sesión 3  →  arquitectura / Clean Code / SOLID   ← hoy
Después   →  tests, automatización, APIs IA, E2E, deploy
```

Todo lo posterior **asume** que sabes partir un flujo en etapas con contratos claros.

### 1.3 Del notebook al sistema (mapa)

```text
Exploración (notebook)              Producción (paquete)
──────────────────────              ────────────────────
celdas + estado global       →      funciones/clases con inputs explícitos
orden de ejecución frágil    →      CLI / job determinista (`python -m …`)
difícil de testear           →      tests unitarios por etapa
rutas absolutas del autor    →      pathlib relativo / config
“me funciona a mí”           →      otro clon + requirements + README
```

**Regla de oro:** el notebook es laboratorio; el paquete es el producto. Puedes (y debes) explorar en notebook; **entregas** código modular.

### 1.4 Analogías útiles

| Concepto | Analogía |
| --- | --- |
| Módulo / clase | Especialista en una tarea |
| Función pura | Receta: mismos ingredientes → mismo plato |
| Efecto lateral | Abrir el frigorífico y tirar comida sin avisar |
| Protocol / interfaz | Enchufe estándar: da igual la marca del electrodoméstico |
| Repository | Mostrador de almacén: “dame los datos”; no importa si vienen de caja o camión |
| Strategy | Cambiar el motor sin rediseñar el coche |
| Facade / CLI | Mostrador de atención al público: un botón, complejidad detrás |
| Over-engineering | Construir un aeropuerto para cruzar un río |

---

## 2. Del notebook al paquete: modelo mental

### 2.1 Qué está bien en un notebook

- Explorar columnas, nulos, outliers.
- Probar una visualización rápida.
- Prototipar una idea de feature o de prompt.
- Documentar el *descubrimiento* para ti o para la clase.

### 2.2 Qué suele fallar al “entregar el notebook”

| Síntoma | Causa | Remedio |
| --- | --- | --- |
| “Ejecuta todas las celdas otra vez” | Estado oculto entre celdas | Script/CLI con `main()` |
| “Cambia la ruta en la celda 7” | Paths hardcodeados | `argparse` + `pathlib` |
| “No sé qué función valida” | Todo mezclado | Módulos por responsabilidad |
| “Si cambio OpenAI se rompe pandas” | Acoplamiento | Abstracciones / Strategy |
| “No puedo testear sin internet” | I/O y lógica juntos | Etapas puras + mocks |

### 2.3 Flujo recomendado en DSIA

```text
1. Explorar en notebook (opcional)
2. Extraer funciones/clases a módulos
3. Orquestar con CLI o job
4. Añadir tests de las etapas puras
5. (Más adelante) API + deploy
```

No hace falta el paso 5 hoy. Sí hace falta que el paso 2–3 quede claro.

### 2.4 Estructura objetivo del ejercicio (E2)

```text
ventas_app/
  __init__.py
  loader.py          # I/O de entrada
  validator.py       # reglas de negocio / calidad
  metrics.py         # agregaciones / KPIs
  cli.py             # orquestación + argparse (Facade)
```

Más adelante, en el E2E, verás el mismo espíritu ampliado:

```text
[CSV / API] → ingesta → validación → features → IA → API → logs
```

Hoy construyes el **esqueleto mental** de ese pipeline.

---

## 3. Clean Code (mínimo viable)

Clean Code no es “código bonito”. Es código que **otra persona (o tú en tres semanas)** entiende y cambia sin miedo.

### 3.1 Nombres que digan *qué* y *por qué*

Mal:

```python
df2 = f(df)
x = df2[df2["u"] > 0]
```

Mejor:

```python
sales = load_sales(path)
valid_sales = sales[sales["unidades"] > 0]
```

Checklist rápida de nombres:

- ¿El nombre es un verbo si es función? (`load`, `validate`, `compute_totals`)
- ¿Es un sustantivo si es dato/clase? (`SalesRecord`, `validator`)
- ¿Evitas abreviaturas opacas (`tmp`, `data2`, `aux`)?
- ¿El booleano se lee como pregunta? (`is_valid`, `has_errors`)

### 3.2 Funciones de un nivel de abstracción

Una función no debe mezclar “política” y “fontanería” en el mismo bloque.

Mal (todo en uno):

```python
def run(path):
    df = pd.read_csv(path)
    df = df[df["unidades"] > 0]
    # llama a OpenAI
    # escribe CSV
    # imprime HTML
```

Mejor (orquestación arriba, detalle abajo):

```python
def run(path: Path, output: Path) -> None:
    frame = load(path)
    records, errors = validate(frame)
    totals = total_by_region(records)
    save_report(output, totals, errors)
```

### 3.3 Efectos laterales explícitos

Un **efecto lateral** es cualquier cosa que cambia el mundo fuera del valor de retorno: escribir disco, llamar red, mutar un DataFrame global, `print` de depuración eterno.

Reglas prácticas:

1. Las funciones “de negocio” preferiblemente **no** escriben ficheros ni llaman APIs.
2. El I/O vive en los **bordes** (`loader`, `cli`, cliente HTTP).
3. Si una función muta un DataFrame, dilo en el nombre o trabaja sobre `copy()`.

```python
# Explícito: no muta el original
work = frame.copy()
work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
```

### 3.4 Errores explícitos, no valores mágicos

Mal:

```python
def load(path):
    if not path.exists():
        return None  # ¿y ahora qué hace el caller?
```

Mejor:

```python
class DataLoadError(Exception):
    """Error al cargar datos de origen."""


def load(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise DataLoadError(f"No existe el fichero: {path}")
    return pd.read_csv(path)
```

Ventajas:

- el fallo es **visible**,
- el caller decide si captura o deja subir,
- los tests pueden `pytest.raises(DataLoadError)`.

### 3.5 Comentarios: el *porqué*, no el *qué*

Mal:

```python
# Sumamos unidades * precio
amount = units * unit_price
```

Mejor (si hace falta):

```python
# El CSV histórico trae IVA incluido; no volver a aplicarlo aquí.
net = gross / 1.21
```

Si el comentario solo narra el código obvio, borra el comentario y mejora el nombre.

### 3.6 Números mágicos y constantes

Mal:

```python
if score > 0.73:
    ...
```

Mejor:

```python
MIN_CONFIDENCE = 0.73
if score > MIN_CONFIDENCE:
    ...
```

En datos, tipifica umbrales de calidad (`MIN_UNITS = 0`) cerca de la regla de negocio.

### 3.7 Tipado gradual (ayuda a Clean Code)

No hace falta ser fanático de los types, pero firmas claras ayudan:

```python
def total_by_region(records: list[SalesRecord]) -> dict[str, float]:
    ...
```

En el demo usamos `Protocol`, `dataclass` y anotaciones: son documentación ejecutable.

### 3.8 Checklist Clean Code de esta sesión

- [ ] Nombres legibles
- [ ] Funciones cortas / un nivel
- [ ] I/O en los bordes
- [ ] `raise` con excepciones propias
- [ ] Sin números mágicos sueltos
- [ ] Sin `print` de depuración en la entrega (logging si hace falta)

---

## 4. OOP útil (sin dogma)

No necesitas un diagrama UML de 40 clases. Necesitas **objetos que encapsulen una responsabilidad**.

### 4.1 Cuándo una función basta

Si no hay estado ni variantes:

```python
def total_amount(units: float, unit_price: float) -> float:
    return units * unit_price
```

### 4.2 Cuándo una clase ayuda

- Hay **configuración** (`path`, API key, umbrales).
- Hay **variantes** intercambiables (CSV vs JSON, mock vs OpenAI).
- Quieres un **contrato** (`Protocol`) para tests y DIP.

### 4.3 `dataclass` para datos

```python
@dataclass(frozen=True)
class SalesRecord:
    region: str
    product: str
    units: float
    unit_price: float

    @property
    def amount(self) -> float:
        return self.units * self.unit_price
```

`frozen=True` evita mutaciones accidentales: el registro es un valor, no un cajón de basura.

### 4.4 `Protocol`: interfaces sin herencia pesada

```python
class SalesRepository(Protocol):
    def load(self) -> pd.DataFrame: ...
```

Cualquier clase con `load() -> DataFrame` **cumple** el protocolo (duck typing tipado). Ideal para DIP y tests.

### 4.5 Excepciones de dominio

```python
class DataLoadError(Exception):
    """Error al cargar datos de origen."""


class ValidationError(Exception):
    """Datos que no cumplen reglas de negocio."""
```

Separa “no pude leer el fichero” de “el fichero está mal de negocio”.

---

## 5. SOLID aplicado a datos + IA

SOLID no es un examen teórico: es una lista de **presiones de diseño** que aparecen cuando tu script crece.

### 5.1 Tabla rápida (DSIA)

| Principio | Pregunta guía | Ejemplo en DSIA |
| --- | --- | --- |
| **S**ingle Responsibility | ¿Esta clase tiene un solo motivo de cambio? | `Validator` no escribe CSV |
| **O**pen/Closed | ¿Puedo extender sin reescribir lo estable? | Nuevas métricas sin tocar validación |
| **L**iskov Substitution | ¿Puedo sustituir una implementación sin romper al caller? | Cualquier `Repository` se comporta como `load()` |
| **I**nterface Segregation | ¿Obligo a depender de métodos que no uso? | Protocol con 1–2 métodos |
| **D**ependency Inversion | ¿El núcleo depende de abstracciones? | Orquestador no importa CSV/OpenAI concretos |

### 5.2 S — Single Responsibility

**Idea:** una unidad = un motivo para cambiar.

En el demo:

- `CsvSalesRepository` — cómo se lee.
- `SalesValidator` — qué es válido.
- `SalesMetrics` — cómo se agrega.
- `main` — orquesta.

Si mañana cambia el formato CSV, **no** deberías tocar las métricas.

Señal de alarma:

```python
class SalesService:
    def load(self): ...
    def validate(self): ...
    def call_openai(self): ...
    def send_email(self): ...
    def plot(self): ...
```

Eso no es un servicio: es un cajón.

### 5.3 O — Open/Closed

**Idea:** abierto a extensión, cerrado a modificación del núcleo estable.

Ejemplo: añadir `average_ticket_by_product` en `SalesMetrics` **sin** reescribir `SalesValidator`.

En IA: añadir proveedor `anthropic` sin reescribir el pipeline que ya funciona con `mock`/`openai` (Strategy).

### 5.4 L — Liskov Substitution

**Idea:** si el código espera un `SalesRepository`, cualquier implementación válida debe poder sustituirse.

Contrato mínimo:

```python
def load(self) -> pd.DataFrame:
    """Devuelve un DataFrame o lanza DataLoadError. No devuelve None."""
```

Romper Liskov:

```python
class BrokenRepo:
    def load(self):
        return None  # el caller espera DataFrame
```

### 5.5 I — Interface Segregation

**Idea:** interfaces pequeñas.

Bien:

```python
class SalesRepository(Protocol):
    def load(self) -> pd.DataFrame: ...
```

Mal:

```python
class MegaRepository(Protocol):
    def load(self): ...
    def save(self): ...
    def sync_s3(self): ...
    def train_model(self): ...
    def render_pdf(self): ...
```

Quien solo quiere leer no debería “implementar” media nube.

### 5.6 D — Dependency Inversion

**Idea:** el orquestador depende de abstracciones, no de detalles.

En el demo:

```python
repo: SalesRepository = CsvSalesRepository(data_path)
```

`main` programa contra `SalesRepository`, no contra “CSV para siempre”.

Mañana:

```python
repo: SalesRepository = JsonSalesRepository(path)
# o FakeSalesRepository en tests
```

En IA (visión del curso):

```text
Pipeline ──► AiProvider (Protocol)
               ├── MockProvider
               ├── OpenAIProvider
               └── …
```

### 5.7 SOLID en una frase por principio (para el DESIGN.md de E2)

1. **S** — `validator.py` solo valida; no persiste.
2. **O** — puedo añadir métricas nuevas en `metrics.py` sin tocar el loader.
3. **L** — `JsonSalesRepository.load()` respeta el mismo contrato que el CSV.
4. **I** — el Protocol del repo solo exige `load()`.
5. **D** — `cli.py` recibe/usa abstracciones; el detalle CSV se inyecta fuera.

No hace falta citar los cinco en el ejercicio: **tres bien anclados al código** bastan.

---

## 6. Patrones que sí compensan en este curso

### 6.1 Repository

**Problema:** el resto del código no debería saber si los datos vienen de CSV, JSON, SQL o API.

**Solución:** encapsular la lectura detrás de `load()`.

```python
class CsvSalesRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> pd.DataFrame:
        if not self._path.exists():
            raise DataLoadError(f"No existe el fichero: {self._path}")
        return pd.read_csv(self._path)
```

**Cuándo usarlo:** siempre que exista más de una fuente *posible*, o quieras testear sin ficheros reales.

### 6.2 Pipeline stages (etapas)

**Problema:** un `run()` monolítico mezcla descarga, limpieza, modelo y escritura.

**Solución:** etapas con entradas/salidas claras; I/O en los bordes.

```text
load → validate → metrics → (opcional) persist / report
```

Cada etapa debería ser testeable con datos en memoria.

### 6.3 Strategy

**Problema:** cambiar de proveedor de IA (o de algoritmo) obliga a `if/else` por todo el código.

**Solución:** misma interfaz, varias implementaciones.

```python
class AiProvider(Protocol):
    def complete(self, prompt: str) -> str: ...


class MockProvider:
    def complete(self, prompt: str) -> str:
        return f"[mock] {prompt[:80]}"


class OpenAIProvider:
    def complete(self, prompt: str) -> str:
        ...  # llamada real
```

El pipeline recibe un `AiProvider`. En CI usas `mock`.

### 6.4 Facade

**Problema:** el usuario (o el compañero) no quiere conocer 12 clases internas.

**Solución:** una puerta simple — CLI, función `run()`, o endpoint `/analyze`.

```bash
python -m ventas_app.cli --input Datos/ventas.csv --output Datos/ventas_limpias.csv
```

La fachada **orquesta**; no mete la lógica de negocio dentro del `argparse`.

### 6.5 Patrones que normalmente NO necesitas aún

| Patrón | Por qué aparcarlo |
| --- | --- |
| Abstract Factory | Overkill con una sola familia de objetos |
| Visitor | Raro en pipelines de datos del curso |
| Singleton global | Esconde dependencias; complica tests |
| Microservicios desde el día 1 | Primero un paquete claro en un repo |

**Heurística:** si no te quita dolor real esta semana, no lo introduzcas.

---

## 7. Anatomía del demo `03_oop_clean_code_solid.py`

### 7.1 Cómo ejecutarlo

Desde la carpeta del tema (con el venv activado):

```bash
cd 1_programacion_avanzada_python
python 03_oop_clean_code_solid.py
```

Salida esperada (orden/números según el CSV):

```text
Registros válidos: … | inválidos: …
Importe por región:
  …: …
```

### 7.2 Mapa de piezas

```text
DataLoadError / ValidationError     excepciones de dominio
SalesRecord                         valor inmutable + amount
SalesRepository (Protocol)          contrato de lectura
CsvSalesRepository                  detalle CSV
SalesValidator.split                SRP: valida y separa errores
SalesMetrics.total_by_region        OCP: métricas aparte
main()                              orquestación (DIP)
```

### 7.3 Recorrido línea a línea (idea)

1. Se resuelve la ruta a `Datos/ventas.csv` con `Path(__file__).parent` (portable).
2. Se construye un repo tipado como `SalesRepository`.
3. `load()` lee o lanza `DataLoadError`.
4. `split()` convierte filas válidas a `SalesRecord` y deja las inválidas aparte.
5. `total_by_region()` agrega importes.
6. `main` solo imprime el resumen.

### 7.4 Qué NO hace el demo (a propósito)

- No escribe CSV de salida (eso lo harás en E2).
- No llama a ninguna API de IA.
- No monta tests (llegarán en sesiones siguientes).
- No usa un framework web.

Es un **esqueleto pedagógico**: lo mínimo para ver SOLID en un flujo de ventas.

### 7.5 Extensiones naturales (después de clase)

1. `JsonSalesRepository` sin tocar `SalesMetrics`.
2. Guardar inválidos a `Datos/ventas_errores.csv`.
3. Añadir `average_units_by_product`.
4. Sustituir `print` por `logging`.
5. Extraer `main` a `cli.py` con `argparse`.

---

## 8. Diseño modular: contratos entre capas

### 8.1 Capas mínimas

```text
┌─────────────────────────────────────┐
│  cli / API / job   (orquestación)   │  ← I/O usuario
├─────────────────────────────────────┤
│  metrics / domain services          │  ← reglas / cálculos
├─────────────────────────────────────┤
│  validator                          │  ← calidad / negocio
├─────────────────────────────────────┤
│  repository / http clients          │  ← I/O externo
└─────────────────────────────────────┘
```

Dependencias preferibles: **hacia abajo** (orquestación → dominio → I/O), no al revés.

### 8.2 Contratos que debes fijar pronto

Aunque sea en un README de 10 líneas:

1. **Schema de entrada** (columnas: `region`, `producto`, `unidades`, `precio_unitario`, …).
2. **Qué es fila válida**.
3. **Schema de salida** (CSV limpio, JSON de métricas, etc.).
4. **Comando de demo** (un solo `python -m …`).

En el E2E del tema 5 verás la misma idea ampliada a `/health` y `/analyze`.

### 8.3 DataFrame vs objetos de dominio

Dos estilos válidos en el curso:

| Estilo | Pros | Contras |
| --- | --- | --- |
| Todo en `DataFrame` | Rápido con pandas | Fácil mezclar etapas; tipado débil |
| Filas → `SalesRecord` | Contratos claros, tipado | Más código de mapeo |

El demo usa el segundo en la zona de métricas: tras validar, trabajas con objetos explícitos.

### 8.4 Dónde poner la config

- Rutas y flags → CLI (`argparse`) o variables de entorno.
- Secretos → `.env` (**nunca** en Git).
- Constantes de negocio → módulo `constants.py` o cerca de la regla.

---

## 9. Anti-patrones frecuentes (lista negra)

Memoriza estos; salen en casi todos los proyectos de alumnos:

1. **`utils.py` de 800 líneas** — cajón de sastre; parte por responsabilidad.
2. **`except Exception: pass`** — silencia fallos; captura excepciones concretas o deja subir.
3. **Mezclar HTTP + pandas + prompt de IA** en una sola función.
4. **Abstract Factory** para un único CSV.
5. **Rutas absolutas** (`/Users/yo/Desktop/...`).
6. **Mutar el DataFrame global** del notebook y luego “importar magia”.
7. **Clases sin comportamiento** (solo getters/setters Java-style) cuando bastaba un `dataclass`.
8. **God object** `PipelineManagerServiceHelper`.
9. **Dependencia circular** `a.py` importa `b.py` que importa `a.py`.
10. **Refactor cosmético** (renombrar sin separar responsabilidades) y llamar a eso “arquitectura”.

### 9.1 Código oloroso → refactor mínimo

| Olor | Refactor |
| --- | --- |
| Función de 120 líneas | Extraer etapas con nombres |
| `if provider == "openai"` repetido | Strategy |
| Tests imposibles sin red | Inyectar Protocol / mock |
| Mismo CSV leído en 4 sitios | Repository único |

---

## 10. Ejemplo guiado: de script a `ventas_app/`

### 10.1 Antes (todo junto)

```python
df = pd.read_csv("Datos/ventas.csv")
df = df[df["unidades"] > 0]
print(df.groupby("region")["unidades"].sum())
```

Útil para explorar. Frágil para entregar.

### 10.2 Después (esqueleto E2)

```text
ventas_app/
  __init__.py
  loader.py
  validator.py
  metrics.py
  cli.py
```

`cli.py` (idea):

```python
def main() -> None:
    args = parse_args()
    frame = load(Path(args.input))
    records, errors = validate(frame)
    totals = total_by_region(records)
    save(Path(args.output), records, errors, totals)
```

### 10.3 Comando objetivo

```bash
python -m ventas_app.cli --input Datos/ventas.csv --output Datos/ventas_limpias.csv
```

### 10.4 `DESIGN.md` (Parte 3 del ejercicio)

Escribe **3 bullets** con anclaje real:

```markdown
- SRP — `validator.py` solo decide validez; no escribe el CSV de salida.
- DIP — `cli.py` programa contra un Protocol `SalesRepository`, no contra pandas/CSV directo.
- OCP — añadí `top_products` en `metrics.py` sin modificar el loader.
```

Si el bullet no apunta a un fichero/clase real, no cuenta.

---

## 11. Clean Code + SOLID en contextos de IA

### 11.1 El prompt también es código

- Versiona prompts en ficheros (`prompts/…`), no solo en el chat.
- Separa **construcción del prompt** de **llamada HTTP**.
- No mezcles parsing del CSV dentro del cliente OpenAI.

### 11.2 Mock primero

Para CI y demos sin clave:

```text
AiProvider = MockProvider | OpenAIProvider
```

Misma interfaz → Liskov + DIP. El Tema 4 del curso profundiza en esto.

### 11.3 Fallos de red ≠ fallos de negocio

- Error HTTP / timeout → excepción de infraestructura.
- Respuesta malformada del modelo → validación de salida.
- Fila de ventas inválida → `ValidationError` / fila a cuarentena.

No uses un único `except Exception` para los tres.

### 11.4 Coste y determinismo

- En desarrollo: mock o modelos baratos.
- Loguea tokens/coste cuando haya llamadas reales (más adelante).
- Un pipeline “flaky” por la IA suele ser un problema de **contrato de salida**, no solo del modelo.

---

## 12. Tests: por qué la arquitectura lo hace posible

Aunque los tests formales lleguen después, diseña ya para ellos.

| Pieza | Cómo testearla |
| --- | --- |
| `validate` | DataFrame pequeño en memoria |
| `metrics` | lista de `SalesRecord` fabricada |
| `CsvSalesRepository` | CSV temporal en `tmp_path` |
| CLI | invocar con ficheros de fixture |

Señal de buena arquitectura: puedes testear métricas **sin** disco ni red.

Señal de mala: el único test posible es “ejecutar el notebook completo”.

---

## 13. Over-engineering: cuándo parar

### 13.1 Preguntas de freno

1. ¿Hay **hoy** una segunda implementación real (JSON, mock, otra API)?
2. ¿El patrón reduce duplicación o solo añade archivos?
3. ¿Un compañero nuevo lo entiende en 5 minutos?
4. ¿El ejercicio pide esto o lo estás inventando?

Si respondes “no” a 1–3, simplifica.

### 13.2 Nivel suficiente para el 21 sep

- Paquete con 3–4 módulos.
- Excepciones propias.
- CLI con argparse.
- 3 principios SOLID explicados con anclaje.
- Nombres limpios.

**No** necesitas: DI container, capas hexagonales completas, 15 Interfaces, microservicios.

---

## 14. Seguridad y hábitos (sí, también aquí)

- No hardcodees API keys al “probar el Strategy de OpenAI”.
- No subas `Datos/` enormes o personales sin criterio; usa muestras.
- No dejes rutas con usuarios (`/Users/david/...`) en el repo.
- README del proyecto: cómo instalar, cómo ejecutar el CLI, qué columnas espera.

---

## 15. Ejemplo extremo a extremo en clase (guión sugerido)

1. Ejecutar el demo y leer la salida.  
2. Señalar en el código: Protocol, Validator, Metrics, `main`.  
3. Pregunta: “¿dónde tocarías para leer JSON?” → solo repo.  
4. Pregunta: “¿dónde añadir ticket medio?” → metrics.  
5. Abrir E2 y crear el esqueleto `ventas_app/`.  
6. Mover responsabilidades.  
7. Cerrar con 3 bullets en `DESIGN.md`.

Tiempo orientativo: 20–25 min demo + 30 min E2.

---

## 16. Autoevaluación (antes de dar por cerrada la sesión)

Responde en voz alta o por escrito:

1. ¿Qué diferencia un notebook de un paquete entregable?
2. ¿Qué es un efecto lateral? Pon un ejemplo.
3. ¿Por qué `Validator` no debería escribir el CSV?
4. ¿Qué problema resuelve Repository?
5. ¿Cómo demostrarías DIP en tu `cli.py`?
6. ¿Cuándo Strategy es overkill?

Si dudas en más de dos, relee las secciones 2, 5 y 6.

---

## 17. Checklist de salida

### Código

- [ ] Demo `03_oop_clean_code_solid.py` ejecutado en tu máquina  
- [ ] Esqueleto `ventas_app/` creado  
- [ ] `loader` / `validator` / `metrics` / `cli` separados  
- [ ] CLI corre con `--input` / `--output`  
- [ ] Excepciones `DataLoadError` / `ValidationError` (o equivalentes)  

### Diseño

- [ ] `DESIGN.md` o README con **3** principios SOLID anclados  
- [ ] Al menos un nombre críptico eliminado  
- [ ] Al menos un número mágico eliminado  
- [ ] Sin `print` de depuración sueltos en la entrega  

### Comprensión

- [ ] Sé explicar notebook vs paquete en una frase  
- [ ] Sé qué patrones usamos y cuáles aparcamos  
- [ ] Sé dónde pondría un `MockProvider` más adelante  

---

## 18. Para la siguiente sesión

1. Deja `ventas_app/` funcionando en tu repo del Proyecto I.  
2. No mezcles de nuevo toda la lógica en un solo fichero “para ir más rápido”.  
3. Cuando lleguen tests y APIs, reutiliza las mismas fronteras (I/O vs dominio).  
4. Ojea a futuro el esquema E2E: `5_desarrollo_end_to_end/01_arquitectura_e2e.md` — es la misma idea a escala.

---

## 19. Apéndice A — Chuleta rápida

### Ejecutar demo

```bash
cd 1_programacion_avanzada_python
python 03_oop_clean_code_solid.py
```

### Paquete ejecutable

```bash
python -m ventas_app.cli --input Datos/ventas.csv --output Datos/ventas_limpias.csv
```

### Protocol mínimo

```python
class SalesRepository(Protocol):
    def load(self) -> pd.DataFrame: ...
```

### Separación mental

```text
I/O (bordes)     → repository, cli, http
Dominio (centro) → validator, metrics, records
```

### SOLID en post-it

```text
S  una razón para cambiar
O  extender sin reescribir el núcleo
L  sustituir sin sorpresas
I  interfaces pequeñas
D  depender de abstracciones
```

---

## 20. Apéndice B — Glosario corto EN/ES

| EN | ES / nota |
| --- | --- |
| Clean Code | código limpio / legible y mantenible |
| technical debt | deuda técnica |
| side effect | efecto lateral |
| coupling | acoplamiento |
| cohesion | cohesión |
| repository | repositorio (acceso a datos) |
| pipeline | tubería / pipeline de etapas |
| strategy | estrategia intercambiable |
| facade | fachada |
| orchestrator | orquestador |
| contract / schema | contrato / esquema de datos |
| single responsibility | responsabilidad única |
| dependency inversion | inversión de dependencias |
| over-engineering | sobreingeniería |

---

## 21. Apéndice C — Preguntas típicas de clase

**¿Tengo que dejar de usar notebooks?**  
No. Úsalos para explorar. Entrega el paquete.

**¿Obligatorio usar clases?**  
No siempre. Sí es obligatorio separar responsabilidades. Clases/Protocols ayudan cuando hay variantes o estado.

**¿Protocol o ABC?**  
En este curso, `Protocol` suele bastar (más simple, duck typing tipado).

**¿Cuántos ficheros son demasiados?**  
Si cada fichero tiene 5 líneas vacías de significado, te pasaste. Si un fichero mezcla load+validate+IA+plot, te faltan.

**¿Puedo poner todo en `services/`?**  
Sí, si dentro sigue habiendo fronteras claras. Un `services/god.py` no mejora nada.

**¿SOLID cae en el examen?**  
Debes **aplicarlo y explicarlo** en el código del proyecto, no solo recitar la tabla.

**¿El demo es la solución del Proyecto I?**  
No. Es una guía de estilo y estructura. Tu dominio puede diferir; los principios no.

**¿Hace falta Docker / microservicios ahora?**  
No. Primero módulos claros y un CLI reproducible.

---

## 22. Apéndice D — Comparativa rápida notebook vs paquete

| Pregunta | Notebook | Paquete DSIA |
| --- | --- | --- |
| ¿Cómo se ejecuta? | “Run All” frágil | `python -m …` |
| ¿Se puede testear una función? | A menudo no | Sí, por etapa |
| ¿Otro alumno lo arranca? | Dudoso | README + requirements |
| ¿Dónde está la validación? | “por ahí” | `validator.py` |
| ¿Cambio de CSV a JSON? | Reescribir celdas | Nuevo Repository |

---

## 23. Apéndice E — Mini rúbrica de autocontrol (arquitectura)

| Criterio | Insuficiente | Adecuado | Sólido |
| --- | --- | --- | --- |
| Separación | Un solo script | 3+ módulos claros | Módulos + contratos explícitos |
| Errores | `None` / `pass` | `raise` con sentido | Excepciones de dominio |
| SOLID | Solo nombres | 3 principios anclados | Extensible (JSON/mock) sin reescritura |
| Clean Code | Nombres pobres | Legible | Sin mágicos ni efectos ocultos |
| Ejecución | Manual en IDE | CLI documentada | CLI + datos de ejemplo |

---

## 24. Cierre

Si dominas este documento, tienes el puente entre “sé pandas” y “entrego una solución”:

> **Etapas claras + responsabilidades separadas + dependencias invertidas donde importa.**

Eso no es burocracia: es lo que permite tests, colaboración, cambiar de proveedor de IA y llegar al E2E sin reescribir el proyecto desde cero.

**Siguiente paso inmediato:** haz el ejercicio [`ejercicios/E2_arquitectura.md`](ejercicios/E2_arquitectura.md) y deja el CLI de `ventas_app/` en verde.
