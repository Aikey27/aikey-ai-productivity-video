# AIKEY AI 生产力视频 Skill（WorkBuddy 公开版）

把中文口播文案自动制作成 `1080×1920` 竖屏科技风视频。安装到 WorkBuddy 后，学员只需填写自己的火山引擎豆包语音 API Key，之后提交文案即可自动配音并导出 MP4。

## 安装到 WorkBuddy

1. 点击 GitHub 页面右上角 `Code` → `Download ZIP`。
2. 解压后，在 WorkBuddy 新建任务，把 `aikey-ai-productivity-video` 文件夹拖入对话框。
3. 发送：

   > 请帮我安装这个 Skill。安装完成后告诉我 Skill 名称，不要运行。

4. 安装后，新建任务，输入 `/` 并选择 `aikey-ai-productivity-video`。

## 配置配音：只填一个 API Key

在 Skill 根目录复制配置样例：

```bash
cp .env.example .env
```

打开 `.env`，只需填写：

```dotenv
VOLCENGINE_API_KEY=你的_API_Key
```

默认使用火山引擎豆包语音 2.0 的公共音色 `zh_female_vv_uranus_bigtts`。需要换成自己有权使用的音色时，再设置可选的 `VOLCENGINE_SPEAKER_ID` 与 `VOLCENGINE_RESOURCE_ID`。

`.env` 已在 `.gitignore` 中，不会被正常提交到 GitHub。也可以不创建 `.env`，直接在运行环境设置同名环境变量。

火山引擎官方文档：[单向流式语音合成（HTTP）](https://docs.volcengine.com/docs/doubao-voice/unidirectional-streaming-text-to-speech-http?lang=zh)。接口调用可能产生费用，以火山引擎控制台为准。

## 使用

把 UTF-8 `.txt` 文案发给 WorkBuddy，然后说：

> 请调用 aikey-ai-productivity-video，把这份文案做成竖屏视频，输出为 production-video.mp4。

也可以在终端运行：

```bash
python3 scripts/create_video.py \
  --text-file /path/to/script.txt \
  --output /path/to/production-video.mp4
```

如果已有配音，可添加 `--audio /path/to/narration.mp3`，跳过火山引擎。

## 运行条件

- Python 3.10+
- Node.js 18+ 与 npm
- FFmpeg（含 `ffprobe`）
- 首次运行需要联网安装 Remotion 依赖

## 公开版边界

- 只包含视频制作，不包含选题、封面、平台发布、账号登录和运营流程。
- 不包含 AIKEY 内部 Skill、私有音色、现成配音、成片、Cookie、密钥或本地绝对路径。
- 请只使用自己有权使用的文案和音色；自动生成后必须人工检查。
- 本仓库代码采用 MIT License；第三方依赖遵循各自许可证。

