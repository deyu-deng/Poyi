---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 67e28a0cadea4c0368daeffdef023791_83eefee786a011f18108525400287e28
    ReservedCode1: 4Nlc8RLqxaxqdw9VIgbjyaArV+O6yK3U6h7W04D4AQAF9hvakhUCfy2QJgwRjFEjqN1J6vt+qJ6TSViGFJfgiXMJXV1YuPo/npDNnsyZZcjnz/Kl/MwdnCX0q4mp35jO7X37nfHQY0CzPoWsI7LtG9OaiVm2c7jYWRt+WIXy12lH0lVxCPDdwezKXW8=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 67e28a0cadea4c0368daeffdef023791_83eefee786a011f18108525400287e28
    ReservedCode2: 4Nlc8RLqxaxqdw9VIgbjyaArV+O6yK3U6h7W04D4AQAF9hvakhUCfy2QJgwRjFEjqN1J6vt+qJ6TSViGFJfgiXMJXV1YuPo/npDNnsyZZcjnz/Kl/MwdnCX0q4mp35jO7X37nfHQY0CzPoWsI7LtG9OaiVm2c7jYWRt+WIXy12lH0lVxCPDdwezKXW8=
---

# Altium Designer

设 $m$ 为对象质量、$a$ 为加速度，则本节主关系写作 $F = m a$，方向沿合力方向。

## Files

- 先做量纲检查：左端为 $[M][L][T]^{-2}$，右端展开后一致，故式子在单位上不塌。
- 把上一节的表达式代入本节的边界条件，可约去一个中间量，剩下只含两个参数的形式。

## Prerequisites

- 典型数值代入前先统一单位；此处取 $g = 9.8\,\mathrm{m/s^2}$ 仅为演示，做题时按卷面给定值替换。
- 常见错误是把适用前提当恒成立：本式只在惯性系、且相互作用可视为瞬时传递时成立。
- 此结论在 $v \ll c$ 的极限下退化为上一节的低速形式，可据此自查推导是否走偏。
- 例题为一步建模、二步约元、三步回代；中间变量统一用 $u, v, w$，避免与已知量重名。
