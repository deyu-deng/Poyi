---
---

# Sliding Window 滑动窗口

## 核心定义

两根指针（left / right）夹出一个**连续子数组窗口**，right 向右扩展，left 在条件被破坏时收缩，全程记录满足条件时的最大/最小窗口。适合求解"最长/最短满足某条件的连续子数组"。

## 模板（哈希计数版，O(n) 时间 / O(窗口内不同元素数) 空间）

```python
cnt = {}
left = ans = 0
for right, x in enumerate(nums):
    cnt[x] = cnt.get(x, 0) + 1          # 扩展：新元素入窗
    while cnt[x] > k:                    # 条件被破坏
        y = nums[left]
        cnt[y] -= 1                      # 收缩：左端元素出窗
        left += 1
    ans = max(ans, right - left + 1)    # 记录合法窗口长度
```

**关键洞察**：收缩时只需检查刚入窗的 `cnt[x]`——其他元素原本就合法，只有新元素可能超限，这是 O(n) 摊销的来源（每个元素最多进出窗口各一次）。

## LeetCode 2958（Length of Longest Subarray With at Most K Frequency）

- **题意**：找最长连续子数组，其中任意元素出现次数 ≤ k。
- **解法**：上述模板直接套用，`k` 即最大允许频率。
- **示例**：`nums=[1,2,3,1,2,3,1,2], k=2` → 答案为 6（如 `[1,2,3,1,2,3]`）。
- **C++ 语法差异**：`while (cnt[nums[right]] > k) { --cnt[nums[left++]]; }`，其中 `nums[left++]` 先取值后自增，`--cnt[...]` 先自减再取值。

## 变体与扩展

- 固定窗口大小：只动 right，窗口超长时同步动 left。
- 维护窗口最值：配合单调队列（如滑动窗口最大值）。
- 计数条件复杂化：窗口内多个约束时，可用"不足则扩展、超限则收缩"的通用双指针框架。

## See Also

- [[Hash-Table-Key-Value]] — 窗口内计数的底层数据结构
- [[Quantitative-Trading]] — 量化回测中同样大量使用滑动窗口统计
