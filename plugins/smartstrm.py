#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
@File    :   smartstrm.py
@Desc    :   触发 SmartStrm 生成/整理 strm 文件
             基于 Cp0204/quark-auto-save 插件，针对 QAS-X 框架增强适配
@Time    :   2026/09/27
@Author  :   xiaoQQya, x1ao4, yanshhhh
"""
import requests


class Smartstrm:

    default_config = {
        "webhook": "",   # SmartStrm Webhook 地址
        "strmtask": "",  # SmartStrm 任务名，支持多个如 `tv,movie`
        "xlist_path_fix": "",  # 路径映射；quark 驱动无须填写；openlist 驱动形如 `/quark:/`
    }
    default_task_config = {
        "auto_trigger": True,  # 是否在转存完成后自动触发 SmartStrm
    }
    is_active = False

    def __init__(self, **kwargs):
        self.plugin_name = self.__class__.__name__.lower()
        if kwargs:
            for key, _ in self.default_config.items():
                if key in kwargs:
                    setattr(self, key, kwargs[key])
                else:
                    print(f"{self.plugin_name} 模块缺少必要参数: {key}")
            # 标准化 URL，避免末尾斜杠导致路径拼接出现 //
            if self.webhook:
                self.webhook = self.webhook.strip()
                if not self.webhook.startswith(("http://", "https://")):
                    self.webhook = f"http://{self.webhook}"
                self.webhook = self.webhook.rstrip("/")

            if self.webhook and self.strmtask:
                if self.get_info():
                    self.is_active = True

    def run(self, task, **kwargs):
        if not self.is_active:
            return

        task_config = task.get("addition", {}).get(
            self.plugin_name, self.default_task_config
        )
        if not task_config.get("auto_trigger"):
            return

        if not task.get("savepath"):
            return

        savepath = task["savepath"].strip().rstrip("/")
        if not savepath.startswith("/"):
            savepath = "/" + savepath

        payload = {
            "event": "qas_strm",
            "data": {
                "strmtask": self.strmtask,
                "savepath": savepath,
                "xlist_path_fix": self.xlist_path_fix,
            },
        }

        try:
            response = requests.request(
                "POST",
                self.webhook,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=5,
            )
            response = response.json()
            if response.get("success"):
                task_data = response.get("task") or {}
                print(
                    f"🌐 SmartStrm: [{task_data.get('name', '')}] "
                    f"{task_data.get('storage_path', savepath)} 触发成功 ✅"
                )
            else:
                print(f"🌐 SmartStrm: 触发失败 ❌ {response.get('message', '')}")
        except Exception as e:
            print(f"🌐 SmartStrm: 触发出错 ❌ {e}")

    def get_info(self):
        """获取 SmartStrm 信息"""
        try:
            response = requests.request(
                "GET",
                self.webhook,
                timeout=5,
            )
            response = response.json()
            if response.get("success"):
                print(
                    f"🌐 SmartStrm: 连接成功 {response.get('version', '')}"
                )
                return response
            print(
                f"🌐 SmartStrm: 连接失败 ❌ {response.get('message', '')}"
            )
            return None
        except Exception as e:
            print(f"🌐 SmartStrm: 连接出错 ❌ {e}")
            return None
