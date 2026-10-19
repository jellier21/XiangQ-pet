# 桌宠开发文档

## 1. 当前版本

项目使用 PyQt6 初始化了一个透明、无边框、置顶显示的桌宠窗口。桌宠启动后默认处于“待机”状态，持续循环播放 `assets/idle` 中的序列帧。

右键桌宠可以打开菜单：

- **打招呼**：播放 `assets/greet` 中的完整序列帧，播放结束后自动回到待机。
- **查阅**：播放 `assets/consult` 中的完整序列帧，播放结束后自动回到待机。
- **退出桌宠**：关闭应用。

左键按住桌宠可以拖动窗口位置，方便将桌宠放到桌面任意区域。

## 2. 目录结构

```text
pet/
├─ assets/
│  ├─ idle/                 # 待机循环帧
│  ├─ greet/                # 打招呼单次动画帧
│  └─ consult/              # 查阅单次动画帧
├─ app/
│  ├─ config.py             # 应用名称、状态枚举、动画参数
│  ├─ models/
│  │  ├─ animation.py       # 动画及素材来源数据结构
│  │  └─ auth.py            # 用户认证信息数据结构
│  ├─ services/
│  │  ├─ asset_loader.py    # 按目录加载并校验 PNG 素材
│  │  ├─ animation_player.py # 使用 QTimer 播放序列帧
│  │  ├─ auth_store.py       # 读取和保存 config/auth.json
│  │  └─ registration_client.py # 异步注册请求
│  └─ ui/
│     └─ pet_window.py       # 透明桌宠窗口、菜单、拖动和首次启动交互
├─ config/
│  └─ auth.json             # 本地用户认证信息，由首次注册成功后生成
├─ main.py                  # 程序入口
├─ requirements.txt         # Python 依赖
└─ DEVELOPMENT.md           # 本开发文档
```

## 3. 运行环境

建议使用 Python 3.11 或更高版本，并在项目目录创建虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

当前工作区原有 `.venv` 缺少 Python 标准库 `encodings`，无法正常启动解释器。如果运行该环境时出现 `ModuleNotFoundError: No module named 'encodings'`，请删除并重新创建 `.venv` 后再安装依赖。

## 4. 首次启动注册流程

程序启动时读取 `config/auth.json`：

- 文件不存在、为空、JSON 格式无效，或缺少 `name`、`mark`、`uuid` 时，视为首次启动。
- 已存在完整认证信息时，直接进入待机，不会重复注册。

首次启动的交互顺序如下：

1. 播放一次 `greet` 打招呼动画。
2. 动画结束后，在人物上方显示对话框询问名字，在人物下方显示输入框和确定按钮。
3. 用户提交名字后，向 `http://127.0.0.1:8080/api/user/register` 发送 `multipart/form-data` 请求，字段名为 `name`。
4. 等待接口响应期间循环播放 `consult` 查阅动画，避免界面阻塞。
5. 接口成功返回后读取响应中的 `uuid` 和 `mark`，与输入的 `name` 一起写入 `config/auth.json`，然后回到待机。
6. 请求失败或响应格式不正确时停止查阅动画，显示错误信息并允许用户重新提交。

成功后的 `config/auth.json` 格式为：

```json
{
  "name": "John Doe",
  "mark": false,
  "uuid": "84be0a74-6a9b-4e7b-97bd-54d6eece936c"
}
```

## 5. 扩展动画状态

添加新状态时，建议按以下步骤进行：

1. 在 `app/config.py` 的 `PetState` 中增加状态值和显示名称。
2. 在 `assets/` 下新增与状态值同名的帧目录。
3. 在 `AssetLoader.load_animations()` 中添加 `AnimationSource`。
4. 在 `PetWindow.contextMenuEvent()` 中添加对应菜单动作，或将动作提取为独立菜单服务。
5. 根据状态是否循环设置 `loop=True` 或 `loop=False`。

序列帧按文件名字典序排序，因此素材文件名应使用固定宽度编号，例如 `frame_01.png`、`frame_02.png`，避免 `frame_10.png` 排在 `frame_2.png` 前面。

## 6. 设计约定

- `main.py` 只负责创建 `QApplication` 和启动主窗口。
- UI 交互保留在 `app/ui`，素材加载和动画播放保留在 `app/services`。
- 状态名称和动画参数集中在 `app/config.py`，避免散落字符串。
- 素材加载时会根据 `AnimationSource.scale` 对完整画布进行缩放；当前待机素材使用 `0.54` 倍缩放，以匹配动作素材中约 `200px` 的人物高度。
- PNG 透明通道会被保留；当前只对待机状态的完整画布做统一缩放，不裁剪单帧内容，避免动画播放时人物位置跳动。
- 单次动画结束统一回到 `PetState.IDLE`，后续可在此基础上添加状态机、气泡、音效和持久化配置。
- 注册请求使用 Qt 异步网络 API，不能在 UI 线程中使用同步网络请求，以保证查阅动画和输入界面继续响应。
