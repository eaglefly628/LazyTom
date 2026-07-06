# LazyTom — 项目技术文档 & Session 交接

> 最后更新：Session end, commit `4bbaa18`
> 分支：`claude/design-lazytom-ui-b3lLa`
> 平台：macOS (开发) + iOS (最终目标 App Store)

---

## 1. 项目背景

**LazyTom** 是一位父亲和 有拖延症小朋友 合作开发的番茄钟 App，最终目标发布到 Apple App Store。

- **商业模式**：一次性付费（$2.99–$4.99），**不做**应用内购买 / 广告 / 订阅
- **差异化卖点**：
  1. 由真正有拖延症的小朋友参与设计
  2. 积分兑换真实奖励（家长设菜单 + 孩子直接兑换 + 家长可看记录）
  3. 情绪感知任务推荐（市面独有）
- **主创父子**：父亲（编程指导）+ 小朋友（学 Python 编程 + 提功能需求）

---

## 2. 技术栈

| 项 | 选型 | 理由 |
|----|------|------|
| 框架 | **Flet 0.84.0** (Python) | 小朋友学 Python，底层 Flutter 渲染 UI 质感好，支持跨平台 iOS 发布 |
| 语言 | Python 3.12+ | 简单，适合初学者 |
| 存储 | JSON 本地文件 (`~/.lazytom/data.json`) | 无需数据库，简单直观 |
| 测试 | pytest | 188 个测试全过 |
| UI 动画 | asyncio + `page.run_task` | Flet 0.84.0 官方推荐，macOS 上唯一可用 |
| 开发设备 | Mac Air | 可直接 `flet run` + `flet build ipa` |

**⚠️ 已发现的 Flet 0.84.0 特有 API 陷阱（必看）：**

| 错误用法（旧版）| 正确用法（0.84.0）|
|---|---|
| `ft.alignment.center` | `ft.Alignment.CENTER` |
| `ft.padding.symmetric(...)` | `ft.Padding.symmetric(...)` (deprecated warning) |
| `ft.padding.only(...)` | `ft.Padding.only(...)` |
| `ft.NavigationDestination` | `ft.NavigationBarDestination` |
| `ft.ImageFit.COVER` | `ft.BoxFit.COVER` |
| `Text(..., decoration=X)` | `Text(..., style=ft.TextStyle(decoration=X))` |
| `page.open(dialog)` | `page.overlay.append(dialog)` + `page.update()` |
| `page.close(dialog)` | `page.overlay.remove(dialog)` + `page.update()` |
| `threading.Timer` + `page.update()` | `page.run_task(async_fn)` + `asyncio.sleep()` |
| `TextButton(text="X")` | `TextButton(content=ft.Text("X"))` |

---

## 3. 项目结构

```
LazyTom/
├── main.py                    # 应用入口 + 底部导航（Timer/Garden/Tasks/Settings）
├── theme.py                   # 单一暖色系配色 tokens（linen + moss + clay）
├── timer_engine.py            # 番茄钟纯逻辑（状态机，无 UI 依赖）
├── points_engine.py           # 积分系统纯逻辑
├── task_engine.py             # 任务管理 + 5档难度 + 3种排序
├── mood_engine.py             # 情绪感知（Phase 1 规则版，非 AI）
├── storage.py                 # JSON 本地持久化
│
├── views/
│   ├── timer_view.py          # 主计时器页面（"Begin Focus" 大按钮）
│   ├── points_view.py         # 积分历史 = "Your Garden"（moss hero + 7 日柱状图）
│   ├── tasks_view.py          # 任务管理（"Start with this" 卡片 + composer）
│   └── settings_view.py       # 设置（主题预览 + 时长 + 声音 + DND）
│
├── components/
│   ├── countdown_ring.py      # 圆形倒计时环（30fps 平滑动画）
│   ├── timer_controls.py      # Begin Focus / Pause / Resume 胶囊按钮
│   ├── points_badge.py        # 火焰打卡 chip（cream + clay）
│   └── mood_picker.py         # 心情选择 overlay 弹窗
│
├── tests/                     # 188 个测试
│   ├── test_timer_engine.py
│   ├── test_points_engine.py
│   ├── test_task_engine.py
│   ├── test_mood_engine.py
│   └── test_storage.py
│
├── assets/backgrounds/        # 旧主题背景图（现在设计已不用）
├── refcode/design_handoff_lazytom/  # 设计参考（JSX 原型 + tokens + 截图）
└── README.md
```

**架构原则：**
- 逻辑（`*_engine.py`）与 UI（`views/`）严格分离
- 引擎类是纯 Python，无 Flet 依赖，方便测试
- `storage.py` 是所有持久化的唯一入口

---

## 4. 已完成功能（Phase 1 + Phase 2 部分）

### Phase 1 核心功能 ✅
- ✅ 番茄计时器（idle/running/paused/completed 状态机）
- ✅ 30fps 平滑圆环动画（`page.run_task` + `asyncio.sleep`）
- ✅ 时长自定义：±1min（<5min）/ ±5min（≥5min），最低 1min
- ✅ 10 秒测试模式（🐛 图标按钮）
- ✅ 键盘快捷键（↑/↓ 调时长）
- ✅ 积分系统（0.4 分/分钟，25min = 10 分）
- ✅ JSON 持久化到 `~/.lazytom/data.json`
- ✅ 设置页面（时长、积分规则）

### Phase 2 已完成 ✅
- ✅ **任务管理**：Task 模型 + 5档难度 + 3种排序（Easy First / Hard First / Manual）
- ✅ **任务时长**：每个任务可设时长，8 个预设 + 自定义输入
- ✅ **模板系统**：10 个初中生任务预设（Math Homework 等）
- ✅ **任务→计时器联动**：点 ▶ 自动跳到 Timer + 同步任务名和时长
- ✅ **情绪感知 Phase 1（非 AI 版）**：
  - 4 档心情（💪 精力充沛 / 🙂 一般 / 😔 累 / 😴 疲惫）
  - 开始前 + 完成后各问一次
  - 规则推荐算法（累→只推 Very Easy；精力好→推 Very Hard）
  - 心情历史持久化
  - Tasks 页 "💭 Recommend for me" 按钮

### 完整视觉重设计 ✅（最新 commit）
按设计稿实现的暖色系风格：
- Linen 底色 `#EFE9D9` + Moss 苔绿 `#2F5A3A` + Clay 赤陶 `#C97A57`
- "Begin Focus" 大胶囊按钮取代小图标（防止拖延症"逃跑"）
- Timer 屏顶部：日期 + 打卡火焰 chip + 5 段进度条
- Garden 屏（原 Points）：深绿 hero 卡片 + 大字 + 7 日柱状图
- Tasks 屏：**"Start with this"** 推荐卡（赤陶 sun icon）+ 分段控件
- 难度从大色块 → **6×6 小圆点** 减少视觉噪音

---

## 5. 待办事项（新 Session 接手继续做）

### 🔥 高优先级（先验证 & 修 bug）

1. **在 Mac 上验证新 UI**：`git pull && flet run main.py`
   - 检查所有 4 个屏幕是否符合设计稿
   - 特别关注：`ft.Container(ink=True, on_click=...)` 这个 API 在 0.84.0 是否有效（timer_controls.py 用了）
   - 如果任何 UI 元素报错，参考 §2 的 "Flet 0.84.0 API 陷阱"表修复

2. **Settings 页面主题切换是否需要恢复？**
   - Agent 重设计时移除了运行时主题切换（现在只显示 3 个主题预览卡）
   - 用户可能想要回来能切换，需要问清楚

### 📋 Phase 2 剩余功能

3. **"就 5 分钟"快速启动按钮**
   - Timer 主页最显眼位置加一个巨大按钮
   - 点击直接开始 5 分钟微任务（不用先设时长）
   - 5 分钟到了后温柔问："再来 5 分钟？"

4. **连续打卡火焰 + 冻结令牌**
   - 每日至少完成 1 个番茄钟维持连续天数
   - 火焰图标越来越大
   - 每 7 天连续得 1 个"冻结令牌"（跳过 1 天不断连续）
   - Timer 顶部的打卡 chip 已经有雏形，需要真实数据驱动

### 🎁 Phase 3：积分兑换奖励

5. **家长端设置奖励菜单**
   - Settings 页加 "Rewards" 区（游戏时间 30 分 / 户外活动 50 分 / 买书 100 分 等）
   - 家长可以增删奖励项和积分要求

6. **孩子端兑换**
   - Points/Garden 页加 "兑换" 按钮
   - 积分够了直接兑换（不需家长审批）

7. **家长查看兑换记录**
   - Settings 或独立页面显示所有兑换历史

### 🤖 Phase 4：AI 增强（情绪感知升级 + 拍照识别）

用户已确认要做，倾向国产模型：
- **文字对话**：DeepSeek V3（¥1/¥4 每百万 tokens，超便宜）
- **拍照识别作业**：通义千问 Qwen-VL-Max 或 豆包视觉版

**⚠️ App Store 部署难点**：
- API key 不能打包进 App（会被反编译盗用）
- **推荐**：自建 Python 后端做代理（每月几十块服务器）
- 备选：让用户填自己的 API key（对小朋友不友好）
- 用户还没最终决策，需要讨论

功能需求（用户已明确）：
- 首次打开 App：AI 对话问用户想做什么
- **拍照上传作业** → AI 提取任务 → 自动创建
- 询问当前状态（情绪 + 精力）
- 推荐任务并开始番茄钟

---

## 6. 测试

**188 个测试，全部通过。**

```bash
python -m pytest tests/ -q                       # 快速跑
python -m pytest tests/ -v                       # 详细
python -m pytest tests/ --cov=timer_engine \    # 覆盖率
  --cov=points_engine --cov=storage \
  --cov=task_engine --cov=mood_engine
```

3 大引擎（timer/points/storage）**100% 行覆盖**。
task_engine 和 mood_engine 也是全路径覆盖。

**⚠️ 不要动测试文件**除非改了引擎逻辑。

---

## 7. 开发工作流

```bash
# 日常开发（Mac）
cd ~/Documents/GitHub/LazyTom
source venv/bin/activate  # 如果用了虚拟环境
flet run main.py           # macOS 桌面窗口，热重载

# 跑测试
python -m pytest tests/ -q

# 提交
git add <files>
git commit -m "..."
git push -u origin claude/design-lazytom-ui-b3lLa
```

**分支**：所有开发都在 `claude/design-lazytom-ui-b3lLa`。不要合并到 main（用户没要求）。

**最终打包 iOS**：`flet build ipa`（Mac Air 上运行）→ Xcode 上传 App Store Connect。

---

## 8. 关键交互设计原则（用户明确要求）

1. **不要给拖延症的人"逃跑门"** — idle 状态没有 cancel 按钮，只有 "Begin Focus"
2. **色调要治愈** — 暖色系，不要花花绿绿
3. **UI 要精致有质感** — 参考 Apple 风格，衬线字体用于标题/大数字
4. **积分要能兑换真实奖励** — 不是虚拟成就，是游戏时间/买书之类的家庭协议
5. **一次性付费** — 用户认可产品价值，不做订阅/内购/广告

---

## 9. 已知 bug / 待观察

- Timer 控件里用了 `ink=True`（Material 涟漪效果），需在 Mac 上验证是否报错
- 旧的 `assets/backgrounds/` 图片文件还在 git 里，但代码已不引用（可保留可删除）
- Points 页面重命名为 "Your Garden" 但底部导航图标是 `YARD_OUTLINED`（🌱），需要验证图标是否合适

---

## 10. 新 Session Handoff Checklist

**开新 session 时告诉 Claude 的关键信息：**

```
你接手 LazyTom 项目。请：
1. 先读 /home/user/LazyTom/HANDOFF.md（本文档）
2. 运行 python -m pytest tests/ -q 确认 188 测试全过
3. 查看 git log --oneline -5 了解最近改动
4. 用户当前在 Mac 上验证 UI 重设计效果（commit 4bbaa18），可能会反馈 bug
5. 分支：claude/design-lazytom-ui-b3lLa（不要切换）
6. 项目根目录：/home/user/LazyTom
7. Flet 版本：0.84.0，注意 §2 的 API 陷阱
```

**新 session 优先处理顺序：**
1. 用户反馈的 UI bug（几乎肯定会有几个）
2. 询问 Phase 2 剩余功能 or Phase 3 兑换系统的实现顺序
3. 讨论 Phase 4 AI 集成的后端方案（DeepSeek + 自建 Python 服务器？）

**必读的历史决策：**
- 主题从 3 个（Lakeside/Meadow/Starry Night with Unsplash 背景图）→ 1 个统一暖色系（暖 linen + moss + clay），运行时切换已移除
- 情绪感知选择了"先做规则版，AI 版后续用国产模型"
- 兑换机制：孩子直接兑换 + 家长看记录（不需审批）
- 计时器倒计时用 `page.run_task` + `asyncio`（不能用 threading）

**用户的沟通风格：**
- 中英文混合
- 常用语音输入，有少量口误/错别字（不要纠正）
- 喜欢"先看效果再讨论下一步"，不要过度提前实现
- 讨厌"一个一个报错来修"，让 Claude 一次性排查完再修
- 遇到 bug 会截图错误信息给 Claude
