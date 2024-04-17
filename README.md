# 🌳 Dendron Examples

<div align="center" style="margin-bottom: 0em;">

[![][arxiv-badge]][arxiv] [![][discord-badge]][discord] [![][twitter-badge]][twitter]


**Dendron is a library for building software agents using behavior trees and language models.**

</div>

## Dependencies

You will need to install dendron, of course. You can do this via

```
pip install dendron
```

## Example Applications

### Tutorial 1: A Chat Agent

The content of Tutorial 1 can be found in the `tutorial_1` directory.  Following the tutorial you will build a example behavior tree that implements a chat agent. This agent listens to a human via microphone, performs automatic speech recognition (ASR), uses a chat model to generate a response, and plays the audio of that response using a text-to-speech (TTS) system. All locally, using models downloaded from Hugging Face:

![image](https://github.com/RichardKelley/dendron/raw/main/docs/img/4_asr_voice_chat.svg)


[arxiv-badge]: https://img.shields.io/badge/arXiv-2404.07439-B31B1B?style=flat-square&logo=arXiv&link=https%3A%2F%2Farxiv.org%2Fabs%2F2404.07439
[arxiv]: https://arxiv.org/abs/2404.07439

[discord]: https://discord.gg/ncBeGQJ9Bk
[discord-badge]: https://img.shields.io/badge/Discord-chat-%235865F2?logo=discord&logoColor=white&link=https%3A%2F%2Fdiscord.gg%2FncBeGQJ9Bk

[twitter]: https://twitter.com/richardkelley
[twitter-badge]: https://img.shields.io/twitter/follow/richardkelley