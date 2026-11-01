---
name: aikey-ai-productivity-video
description: 把中文口播文案自动配音并制作成 1080×1920 竖屏科技风视频。适用于 WorkBuddy 中的 AI 工具介绍、生产力方法与教程口播；首次使用只需配置用户自己的火山引擎豆包语音 API Key。
---

# AIKEY AI 生产力视频（公开版）

用于把用户已经确认的中文口播文案制作成竖屏科技风视频。只处理视频制作，不负责选题、事实背书、封面、账号登录或平台发布。

## 首次配置

1. 优先读取进程环境变量 `VOLCENGINE_API_KEY`，不存在时读取本 Skill 根目录的 `.env`。
2. 如果缺少 API Key，提示用户复制 `.env.example` 为 `.env`，只填写 `VOLCENGINE_API_KEY`。
3. 不要求用户把密钥发送到公开群聊，不在日志、输出或 Git 中显示密钥。
4. 默认音色与模型已经配置好；只有用户明确要求换音色时，才使用可选的 `VOLCENGINE_SPEAKER_ID` 和 `VOLCENGINE_RESOURCE_ID`。

## 制作视频

确认用户提供了 UTF-8 文案文件，或先把用户确认的文案保存为 `.txt`。然后运行：

```bash
python3 <本 Skill 目录>/scripts/create_video.py \
  --text-file /path/to/script.txt \
  --output /path/to/output.mp4
```

用户已提供 MP3/WAV 配音时，可以添加 `--audio /path/to/audio`，脚本会跳过在线配音。

脚本会自动：

- 使用火山引擎 V3 HTTP SSE 接口生成一条连续配音；
- 按文案句子与实际音频时长生成顺序画面卡；
- 在独立工作目录安装缺失的 Remotion 依赖；
- 输出 `1080×1920`、30fps、H.264 + AAC 成片。

## 验收

- 确认输出文件存在且大于 100 KB。
- 用 `ffprobe` 确认分辨率为 `1080×1920`，并同时包含视频流和音频流。
- 抽查开头、中段和结尾，确认不是黑屏、没有明显文字截断或配音缺失。
- 返回成片绝对路径，并明确配音来自用户配置的火山引擎音色。

## 安全边界

- 不读取浏览器账号、Cookie、工作空间记忆或无关私人文件。
- 不包含或调用 AIKEY 内部制作 Skill、私有模板、固定私有音色、账号配置和发布流程。
- 不声称自动生成结果已经过人工事实核查；提醒用户最终人工验收。

