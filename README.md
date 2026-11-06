# Global Half-Hour Time (GHHT) Standard Specification

---


## Language Selection / Выбор языка / 언어 선택 / 言語の選択 / 语言选择 / Sprachauswahl / Selección de idioma / Sélection de la langue

* [English](#english)
* [Русский](#русский)
* [한국어](#한국어)
* [日本語](#日本語)
* [简体中文](#简体中文)

---

# English

# INTERNATIONAL STANDARD GHHT-1

**Global Half-Hour Time System**
*Global Half-Hour Time (GHHT) Standard Specification*

---

## 1. PURPOSE AND SCOPE

This standard defines the architecture, mathematical model, and rules for calculating **Global Half-Hour Time (GHHT)**. The system is intended for the depoliticized synchronous division of the globe into fixed time zones oriented to physical-geographic coordinates, and excludes the use of administrative (state) borders and seasonal shifts (summer/winter time).

---

## 2. GEOMETRIC AND TEMPORAL STRUCTURE OF THE SYSTEM

### 2.1. Base division unit (Time band)

The globe is divided by longitude into **48 equal geodesic zones (bands)**.

The width of one time band is strictly **7.5°** of meridian arc.

Each band corresponds to a unique integer zone index ($I_z$) in the range from **−24 to +23**.

### 2.2. Centering and zone boundaries

The reference point of the spatial grid is the **Prime Meridian (0.0°)**, which strictly defines the center of the central time zone ($I_z = 0$).

The geographic boundaries of zone $I_z = 0$ lie between the meridians **−3.75°** and **+3.75°**.

For any arbitrary point on the planet with longitude $λ$ (where $−180.0° ≤ λ < +180.0°$), the time zone index is determined by mathematical rounding to the nearest grid step:

$$
I_z = round(λ / 7.5)
$$

### 2.3. Zone local time scale (Offset)

The internal time within each zone is shifted relative to the central zone ($I_z = 0$) by a fixed amount that is a multiple of **0.5 hours (30 minutes)**. The zone offset ($O_z$) is calculated as:

$$
O_z = I_z × 0.5
$$

The local time designation is formed as $GHHT[±][Offset in hours]$.
*Example: For a zone with index +5, the designation is* $GHHT+2.5$.

### 2.4. Astronomical accuracy criterion (Zenith)

Within any GHHT zone, the calculated local noon (the highest position of the Sun — Zenith) is tied to the geodesic longitude of the observation meridian $λ$ and is calculated by the internal formula:

$$
EQ T_zenith = (12.0 − λ/15.0 + O_z) (mod 24.0)
$$

*Standard note:* thanks to the half-degree grid step, at any point on Earth the true astronomical noon by local GHHT clocks is guaranteed to occur in the range **from 11:45 to 12:15** (maximum deviation does not exceed ±15 minutes).

---

## 3. INTEGRATION WITH COORDINATED UNIVERSAL TIME (UTC)

To ensure global synchronization of physical devices and computing systems, the GHHT standard uses the Coordinated Universal Time (UTC) scale as an external time reference.

### 3.1. Basic scale binding

**Time zero point:** The time scale of the central zone $GHHT+0.0$ at the 0.0° meridian is fully equivalent to the **UTC (Greenwich)** time scale.

The increment of seconds, minutes, and hours in the GHHT system fully coincides with the metric of the UTC scale.

### 3.2. Conversion of UTC time to local GHHT time

To calculate the current local GHHT time ($T_GHHT$) at a geographic point with longitude $λ$, algebraic addition with the calculated time shift interval ($Δt$) is applied to the $T_UTC$ scale reading:

$$
T_GHHT = T_UTC + Δt
$$

Where the time shift value $Δt$ (expressed in hours) is calculated as a function of longitude $λ$:

$$
Δt = round(λ / 7.5) × 0.5
$$

The rounding function $round(x)$ is performed to the nearest integer according to the rules of mathematical rounding (in the case of half-integer values — to the nearest even number or away from zero, depending on the geodesic coordinate system used).

### 3.3. Synchronization requirements (Metrological assurance)

To guarantee system accuracy, software and hardware complexes implementing the GHHT standard must support two modes of UTC scale verification:

**Autonomous (internal) mode:** Continuous reading of the hardware platform's system clock under the operating system.

**Network (reference) mode:** Forced periodic synchronization with primary time reference servers via the **NTP (Network Time Protocol)**. The device must calculate the network offset (delta shift $Δ_NTP$) relative to the system clock:

$$
Δ_NTP = T_NTP_Server − T_System
$$

If an NTP server is available, the corrected scale must be used for GHHT calculation:

$$
T_UTC = T_System + Δ_NTP
$$

If communication is lost, the device must automatically switch to autonomous mode with status fixation.

---


# Русский
# МЕЖДУНАРОДНЫЙ СТАНДАРТ GHHT-1

**Глобальная система единого получасового времени**
*Global Half-Hour Time (GHHT) Standard Specification*

---

## 1. НАЗНАЧЕНИЕ И ОБЛАСТЬ ПРИМЕНЕНИЯ

Настоящий стандарт определяет архитектуру, математическую модель и правила исчисления **Глобального Получасового Времени (GHHT)**. Система предназначена для деполитизированного синхронного деления земного шара на фиксированные временные зоны, ориентированные на физико-географические координаты, и исключает использование административных (государственных) границ и сезонных сдвигов (летнее/зимнее время).

---

## 2. ГЕОМЕТРИЧЕСКАЯ И ВРЕМЕННАЯ СТРУКТУРА СИСТЕМЫ

### 2.1. Базовая единица деления (Временная полоса)

Земной шар разделён по долготе на **48 равных геодезических зон (полос)**.

Ширина одной временной полосы составляет строго **7.5°** дуги меридиана.

Каждой полосе соответствует уникальный целочисленный индекс зоны ($I_z$) в диапазоне от **−24** до **+23**.

### 2.2. Центрирование и границы зон

Базовой точкой отсчёта пространственной сетки является **Нулевой меридиан (0.0°)**, который строго определяет центр центральной временной зоны ($I_z = 0$).

Географические границы зоны $I_z = 0$ пролегают между меридианами **−3.75°** и **+3.75°**.

Для любой произвольной точки на планете с долготой $λ$ (где $−180.0° ≤ λ < +180.0°$) индекс временной зоны определяется путем математического округления до ближайшего шага сетки:

$$
I_z = round(λ / 7.5)
$$

### 2.3. Шкала локального времени зон (Смещение)

Внутреннее время внутри каждой зоны сдвинуто относительно центральной зоны ($I_z = 0$) на фиксированную величину, кратную **0.5 часа (30 минутам)**. Смещение зоны ($O_z$) рассчитывается как:

$$
O_z = I_z × 0.5
$$

Обозначение локального времени формируется как $GHHT[±][Смещение в часах]$.
*Пример: Для зоны с индексом +5 обозначение имеет вид* $GHHT+2.5$.

### 2.4. Астрономический критерий точности (Зенит)

Внутри любой зоны системы GHHT расчётный локальный полдень (наивысшая точка нахождения Солнца — Зенит) привязан к геодезической долготе меридиана наблюдения $λ$ и рассчитывается по внутренней формуле:

$$
EQ T_zenith = (12.0 − λ/15.0 + O_z) (mod 24.0)
$$

*Примечание стандарта:* благодаря полуградусному шагу сетки, в любой точке Земли истинный астрономический полдень по локальным часам GHHT гарантированно наступает в диапазоне **от 11:45 до 12:15** (максимальное отклонение не превышает ±15 минут).

---

## 3. ИНТЕГРАЦИЯ С ВСЕМИРНЫМ КООРДИНИРОВАННЫМ ВРЕМЕНЕМ (UTC)

Для обеспечения глобальной синхронизации физических устройств и вычислительных систем стандарт GHHT использует шкалу Всемирного координированного времени (UTC) в качестве внешнего эталона времени.

### 3.1. Базовая привязка шкал

**Временной нуль-пункт:** Шкала времени центральной зоны $GHHT+0.0$ на меридиане 0.0° полностью эквивалентна шкале времени **UTC (Гринвич)**.

Приращение секунд, минут и часов в системе GHHT полностью совпадает с метрикой шкалы UTC.

### 3.2. Преобразование времени UTC в локальное время GHHT

Для вычисления текущего локального времени GHHT ($T_GHHT$) в географической точке с долготой $λ$ к показанию шкалы $T_UTC$ применяется алгебраическое сложение с расчетным временным интервалом сдвига ($Δt$):

$$
T_GHHT = T_UTC + Δt
$$

Где величина временного сдвига $Δt$ (выраженная в часах) вычисляется как функция от долготы $λ$:

$$
Δt = round(λ / 7.5) × 0.5
$$

Округление функции $round(x)$ выполняется к ближайшему целому числу по правилам математического округления (в случае полуцелых значений — к ближайшему четному или в сторону удаления от нуля, в зависимости от используемой геодезической системы координат).

### 3.3. Требования к синхронизации (Метрологическое обеспечение)

Для гарантирования системной точности программно-аппаратные комплексы, реализующие стандарт GHHT, должны поддерживать два режима верификации шкалы UTC:

**Автономный (внутренний) режим:** Непрерывное чтение системных часов аппаратной платформы под управлением операционной системы.

**Сетевой (эталонный) режим:** Принудительная периодическая синхронизация с серверами первичного эталона времени по протоколу **NTP (Network Time Protocol)**. Устройство обязано вычислять сетевое смещение (дельта-сдвиг $Δ_NTP$) относительно системных часов:

$$
Δ_NTP = T_NTP_Server − T_System
$$

В случае доступности NTP-сервера, для расчёта времени GHHT обязана применяться скорректированная шкала:

$$
T_UTC = T_System + Δ_NTP
$$

При потере связи устройство обязано автоматически переходить в автономный режим с фиксацией статуса.

---

# 简体中文

# 国际标准 GHHT-1

**全球半小时时间系统**
*Global Half-Hour Time (GHHT) Standard Specification*

---

## 1. 目的和适用范围

本标准定义了**全球半小时时间（GHHT）** 的架构、数学模型和计算规则。该系统旨在将地球按物理地理坐标同步划分为固定的时区，实现去政治化，并排除使用行政（国家）边界和季节性调整（夏令时/冬令时）。

---

## 2. 系统的几何和时间结构

### 2.1. 基本划分单位（时间带）

地球按经度划分为 **48个相等的测地学区（带）**。

一个时间带的宽度严格为子午线弧的 **7.5°**。

每个带对应一个唯一的整数区索引（$I_z$），范围为 **−24 至 +23**。

### 2.2. 中心定位和区域边界

空间网格的基准点是 **本初子午线（0.0°）** ，它严格定义中央时区（$I_z = 0$）的中心。

$I_z = 0$ 区的地理边界位于子午线 **−3.75°** 和 **+3.75°** 之间。

对于地球上任意经度为 $λ$ 的点（其中 $−180.0° ≤ λ < +180.0°$），时区索引通过数学舍入到最近的网格步长来确定：

$$
I_z = round(λ / 7.5)
$$

### 2.3. 区域本地时间标度（偏移）

每个区域内的内部时间相对于中央区（$I_z = 0$）偏移一个固定的量，该量为**0.5小时（30分钟）** 的倍数。区域偏移（$O_z$）计算如下：

$$
O_z = I_z × 0.5
$$

本地时间标识形如 $GHHT[±][以小时为单位的偏移]$。
*示例：对于索引为 +5 的区域，标识为* $GHHT+2.5$。

### 2.4. 天文精度标准（天顶）

在任何 GHHT 区域内，计算的本地正午（太阳的最高位置——天顶）与观测子午线的测地经度 $λ$ 相关联，并按内部公式计算：

$$
EQ T_zenith = (12.0 − λ/15.0 + O_z) (mod 24.0)
$$

*标准说明：* 由于半度网格步长，在地球上任何地点，按本地 GHHT 时钟的真实天文正午保证出现在**11:45 至 12:15** 之间（最大偏差不超过 ±15 分钟）。

---

## 3. 与协调世界时（UTC）的集成

为确保物理设备和计算系统的全球同步，GHHT 标准使用协调世界时（UTC）标度作为外部时间基准。

### 3.1. 基本标度绑定

**时间零点：** 中央区 $GHHT+0.0$ 在 0.0° 子午线上的时间标度完全等同于 **UTC（格林尼治）** 时间标度。

GHHT 系统中秒、分和小时的增量与 UTC 标度的度量完全一致。

### 3.2. 将 UTC 时间转换为本地 GHHT 时间

要计算经度为 $λ$ 的地理点处的当前本地 GHHT 时间（$T_GHHT$），对 $T_UTC$ 标度读数应用与计算的时间偏移间隔（$Δt$）的代数加法：

$$
T_GHHT = T_UTC + Δt
$$

其中时间偏移值 $Δt$（以小时表示）作为经度 $λ$ 的函数计算：

$$
Δt = round(λ / 7.5) × 0.5
$$

舍入函数 $round(x)$ 按数学舍入规则舍入到最接近的整数（对于半整数值——舍入到最接近的偶数或远离零，取决于所使用的测地坐标系）。

### 3.3. 同步要求（计量保障）

为保证系统精度，实现 GHHT 标准的软件和硬件综合体必须支持两种 UTC 标度验证模式：

**自主（内部）模式：** 在操作系统下连续读取硬件平台的系统时钟。

**网络（参考）模式：** 通过 **NTP（网络时间协议）** 与主时间基准服务器强制周期性同步。设备必须计算相对于系统时钟的网络偏移（增量偏移 $Δ_NTP$）：

$$
Δ_NTP = T_NTP_Server − T_System
$$

如果 NTP 服务器可用，则必须使用校正后的标度进行 GHHT 计算：

$$
T_UTC = T_System + Δ_NTP
$$

如果通信丢失，设备必须自动切换到自主模式并固定状态。

---

# 日本語

# 国際標準 GHHT-1

**全球半時間システム**
*Global Half-Hour Time (GHHT) Standard Specification*

---

## 1. 目的および適用範囲

本標準は、**全球半時間（GHHT）** のアーキテクチャ、数学モデル、および計算規則を定義する。本システムは、地球を物理地理座標に基づく固定された時間帯に同期分割することを目的とし、脱政治化を図り、行政（国家）境界および季節調整（夏時間/冬時間）の使用を排除する。

---

## 2. システムの幾何学的および時間的構造

### 2.1. 基本分割単位（時間帯）

地球は経度によって**48の等しい測地帯（帯）** に分割される。

1つの時間帯の幅は子午線弧の厳密に**7.5°** である。

各帯は**−24 から +23** の範囲の一意の整数帯インデックス（$I_z$）に対応する。

### 2.2. 中心配置と帯境界

空間グリッドの基準点は**本初子午線（0.0°）** であり、中央時間帯（$I_z = 0$）の中心を厳密に定義する。

$I_z = 0$ の帯の地理的境界は子午線**−3.75°**と**+3.75°** の間に位置する。

地球上の任意の経度 $λ$ の点（$−180.0° ≤ λ < +180.0°$）について、時間帯インデックスは最近接のグリッドステップへの数学的丸めによって決定される：

$$
I_z = round(λ / 7.5)
$$

### 2.3. 帯の現地時間スケール（オフセット）

各帯内の内部時間は、中央帯（$I_z = 0$）に対して**0.5時間（30分）** の倍数である固定量だけシフトされる。帯オフセット（$O_z$）は次のように計算される：

$$
O_z = I_z × 0.5
$$

現地時間の表記は $GHHT[±][時間単位のオフセット]$ の形式で形成される。
*例：インデックス +5 の帯の場合、表記は* $GHHT+2.5$ *となる。*

### 2.4. 天文精度基準（天頂）

任意の GHHT 帯内において、計算された現地正午（太陽の最高位置——天頂）は観測子午線の測地経度 $λ$ に結び付けられ、内部式によって計算される：

$$
EQ T_zenith = (12.0 − λ/15.0 + O_z) (mod 24.0)
$$

*標準注記：* 半度グリッドステップのおかげで、地球上の任意の地点において、現地 GHHT 時計による真の天文正午は**11:45 から 12:15** の範囲で必ず発生する（最大偏差は ±15 分を超えない）。

---

## 3. 協定世界時（UTC）との統合

物理デバイスおよび計算システムのグローバル同期を確保するため、GHHT 標準は協定世界時（UTC）スケールを外部時間基準として使用する。

### 3.1. 基本スケールの結合

**時間零点：** 0.0° 子午線における中央帯 $GHHT+0.0$ の時間スケールは、**UTC（グリニッジ）** 時間スケールと完全に等価である。

GHHT システムにおける秒、分、時間の増分は UTC スケールの計量と完全に一致する。

### 3.2. UTC 時間から現地 GHHT 時間への変換

経度 $λ$ の地理的地点における現在の現地 GHHT 時間（$T_GHHT$）を計算するには、$T_UTC$ スケールの読み取り値に、計算された時間シフト間隔（$Δt$）の代数的加算を適用する：

$$
T_GHHT = T_UTC + Δt
$$

ここで、時間シフト値 $Δt$（時間単位）は経度 $λ$ の関数として計算される：

$$
Δt = round(λ / 7.5) × 0.5
$$

丸め関数 $round(x)$ は数学的丸めの規則に従って最近接整数に実行される（半整数値の場合——使用される測地座標系に応じて、最近接偶数またはゼロから遠ざかる方向へ）。

### 3.3. 同期要件（計量保証）

システム精度を保証するため、GHHT 標準を実装するソフトウェアおよびハードウェア複合体は、UTC スケール検証の2つのモードをサポートしなければならない：

**自律（内部）モード：** オペレーティングシステム下でのハードウェアプラットフォームのシステムクロックの連続読み取り。

**ネットワーク（参照）モード：** **NTP（ネットワークタイムプロトコル）** による一次時間基準サーバーとの強制的な定期同期。デバイスはシステムクロックに対するネットワークオフセット（デルタシフト $Δ_NTP$）を計算しなければならない：

$$
Δ_NTP = T_NTP_Server − T_System
$$

NTP サーバーが利用可能な場合、GHHT 計算には補正されたスケールを使用しなければならない：

$$
T_UTC = T_System + Δ_NTP
$$

通信が失われた場合、デバイスは自動的に自律モードに切り替え、ステータスを固定しなければならない。

---

# 한국어

# 국제 표준 GHHT-1

**글로벌 반시간 시스템**
*Global Half-Hour Time (GHHT) Standard Specification*

---

## 1. 목적 및 적용 범위

본 표준은 **글로벌 반시간(GHHT)** 의 아키텍처, 수학적 모델 및 계산 규칙을 정의한다. 본 시스템은 지구를 물리지리적 좌표에 기반한 고정 시간대들로 동기 분할하는 것을 목적으로 하며, 탈정치화를 도모하고 행정(국가) 경계 및 계절 조정(서머타임/윈터타임)의 사용을 배제한다.

---

## 2. 시스템의 기하학적 및 시간적 구조

### 2.1. 기본 분할 단위(시간대)

지구는 경도에 따라 **48개의 동일한 측지 구역(대)** 으로 분할된다.

하나의 시간대 폭은 자오선 호의 엄격히 **7.5°** 이다.

각 대는 **−24에서 +23** 범위의 고유한 정수 구역 인덱스($I_z$)에 대응한다.

### 2.2. 중심 설정 및 구역 경계

공간 그리드의 기준점은 **본초자오선(0.0°)** 이며, 이는 중앙 시간대($I_z = 0$)의 중심을 엄격히 정의한다.

$I_z = 0$ 구역의 지리적 경계는 자오선 **−3.75°** 와 **+3.75°** 사이에 위치한다.

지구상의 임의의 경도 $λ$ 지점($−180.0° ≤ λ < +180.0°$)에 대해, 시간대 인덱스는 가장 가까운 그리드 단계로의 수학적 반올림에 의해 결정된다:

$$
I_z = round(λ / 7.5)
$$

### 2.3. 구역 현지 시간 척도(오프셋)

각 구역 내부의 시간은 중앙 구역($ I_z = 0 $)에 대해 **0.5시간(30분)** 의 배수인 고정량만큼 이동된다. 구역 오프셋($O_z$)은 다음과 같이 계산된다:

$$
O_z = I_z × 0.5
$$

현지 시간 표기는 $GHHT[±][시간 단위 오프셋]$ 형식으로 구성된다.
*예: 인덱스 +5인 구역의 경우 표기는* $GHHT+2.5$ *이다.*

### 2.4. 천문 정밀도 기준(천정)

임의의 GHHT 구역 내에서 계산된 현지 정오(태양의 최고 위치——천정)는 관측 자오선의 측지 경도 $λ$에 연결되며 내부 공식에 의해 계산된다:

$$
EQ T_zenith = ($ 12.0 − λ/15.0 + O_z $) (mod 24.0)
$$

*표준 주석:* 반도 그리드 단계 덕분에, 지구상의 임의의 지점에서 현지 GHHT 시계에 의한 진정한 천문 정오는 **11:45에서 12:15** 범위에서 반드시 발생한다(최대 편차는 ±15분을 초과하지 않는다).

---

## 3. 협정 세계시(UTC)와의 통합

물리적 장치 및 컴퓨팅 시스템의 글로벌 동기화를 보장하기 위해, GHHT 표준은 협정 세계시(UTC) 척도를 외부 시간 기준으로 사용한다.

### 3.1. 기본 척도 결합

**시간 영점:** 0.0° 자오선에서 중앙 구역 $GHHT+0.0$의 시간 척도는 **UTC(그리니치)** 시간 척도와 완전히 동등하다.

GHHT 시스템에서 초, 분, 시간의 증분은 UTC 척도의 계량과 완전히 일치한다.

### 3.2. UTC 시간에서 현지 GHHT 시간으로의 변환

경도 $λ$ 의 지리적 지점에서 현재 현지 GHHT 시간($ T_GHHT $)을 계산하려면, $ T_UTC $ 척도 판독값에 계산된 시간 이동 간격($ Δt $)의 대수적 덧셈을 적용한다:

$$
T_GHHT = T_UTC + Δt
$$

여기서 시간 이동 값 $Δt$(시간 단위)는 경도 $λ$의 함수로 계산된다:

$$
Δt = round(λ / 7.5) × 0.5
$$

반올림 함수 $round(x)$ 는 수학적 반올림 규칙에 따라 가장 가까운 정수로 수행된다(반정수 값의 경우——사용되는 측지 좌표계에 따라 가장 가까운 짝수 또는 0에서 멀어지는 방향으로).

### 3.3. 동기화 요구사항(계량 보증)

시스템 정밀도를 보장하기 위해, GHHT 표준을 구현하는 소프트웨어 및 하드웨어 복합체는 UTC 척도 검증의 두 가지 모드를 지원해야 한다:

**자율(내부) 모드:** 운영 체제 하에서 하드웨어 플랫폼의 시스템 시계를 연속적으로 읽는 것.

**네트워크(참조) 모드:** **NTP(네트워크 시간 프로토콜)** 를 통한 1차 시간 기준 서버와의 강제 주기적 동기화. 장치는 시스템 시계에 대한 네트워크 오프셋(델타 이동 $Δ_NTP$)을 계산해야 한다:

$$
Δ_NTP = T_NTP_Server − T_System
$$

NTP 서버를 사용할 수 있는 경우, GHHT 계산에는 보정된 척도를 사용해야 한다:

$$
T_UTC = T_System + Δ_NTP
$$

통신이 손실되면 장치는 자동으로 자율 모드로 전환하고 상태를 고정해야 한다.
