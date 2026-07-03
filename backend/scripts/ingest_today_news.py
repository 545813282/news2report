#!/usr/bin/env python3
"""
将 2026-07-03 收集的 18 条 AI 新闻批量写入后端，并生成当日日报。
来源链接已按用户提供的最新数据补充。
"""
import json
import urllib.request
import urllib.error
from datetime import datetime

BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 300  # 单条请求超时（秒），Kimi 结构化抽取较慢

NEWS_ITEMS = [
    {
        "title": "GPT周报｜宇树科技IPO注册申请获批；OpenAI发布GPT-5.6；Anthropic最强模型解除出口限制",
        "summary": "财新网发布AI周报：中国机器人公司宇树科技IPO注册申请已获证监会批准；OpenAI于6月26日发布GPT-5.6系列（Sol/Terra/Luna）；Anthropic宣布美国商务部已移除对Claude Fable 5和Mythos 5的出口限制，7月1日起恢复访问。",
        "source": "财新网",
        "url": "https://weekly.caixin.com/2026-07-03/102483830.html",
        "tags": "AI政策、IPO、大模型发布",
    },
    {
        "title": "白宫起草自愿AI发布标准框架，OpenAI、Google、Anthropic参与高级别谈判",
        "summary": "英国《金融时报》确认，白宫正与OpenAI、Google、Anthropic进行高级别谈判，预计最快下周公布自愿性AI发布标准框架，正式取代此前导致Fable 5和GPT-5.6受限的临时出口管制方式。",
        "source": "Financial Times",
        "url": "https://www.ft.com/content/c02b036e-c1b7-4356-9b24-e3c191ba7d3a",
        "tags": "AI政策、监管、美国",
    },
    {
        "title": "OpenAI提议向美国政府提供5%股权分成",
        "summary": "OpenAI提出向美国政府提供其AI boom收益的5%股权份额，这一非同寻常的提议表明OpenAI对其IPO前政府关系的重视程度。Anthropic和Google尚未表态是否同意。",
        "source": "The Verge",
        "url": "https://www.theverge.com/openai/132311/openai-government-equity-stake-ipo",
        "tags": "AI政策、OpenAI、股权",
    },
    {
        "title": "Anthropic年化收入超过OpenAI，企业订阅量首登第一",
        "summary": "Fortune报道：Anthropic自报年化收入运行率达470亿美元，超过OpenAI的250-330亿美元。Ramp数据证实Anthropic在5月企业订阅量超过OpenAI。",
        "source": "Fortune",
        "url": "https://fortune.com/2026/07/02/anthropic-openai-revenue-claude-llm/",
        "tags": "市场动态、竞争格局、收入",
    },
    {
        "title": "Cloudflare宣布9月15日起封锁\"混合用途\"AI爬虫",
        "summary": "Cloudflare宣布自2026年9月15日起，将默认屏蔽同时用于搜索引擎索引和AI模型训练的\"混合用途\"爬虫访问含广告页面，同时推出\"按使用付费\"模式。",
        "source": "Cloudflare官方博客",
        "url": "https://blog.cloudflare.com/generative-ai-scrapers/",
        "tags": "AI基础设施、内容版权、爬虫治理",
    },
    {
        "title": "泄露视频显示微软正开发轻量级\"Copilot OS\" Aion",
        "summary": "Windows Central发布的泄露视频展示了Aion，一款为AI智能体设计的精简版Windows概念系统，基于Edge浏览器和Web应用构建，类似Chrome OS。",
        "source": "The Verge",
        "url": "https://www.theverge.com/microsoft/132345/microsoft-windows-copilot-os-aion-leak",
        "tags": "操作系统、微软、AI硬件",
    },
    {
        "title": "Weave Robotics售价8000美元家用叠衣机器人Issac 1开启预售",
        "summary": "旧金山家用机器人公司Weave Robotics的Issac 1于7月2日正式开启预售，售价8000美元（定金250美元），预计年内发货。",
        "source": "The Verge",
        "url": "https://www.theverge.com/tech/132312/weave-robotics-issac-1-pre-order-8000",
        "tags": "家用机器人、智能硬件、消费级AI",
    },
    {
        "title": "Anthropic恢复Claude Fable 5和Mythos 5访问权限",
        "summary": "Anthropic于7月1日恢复了对Claude Fable 5和Claude Mythos 5的访问权限，此前因美国政府出口限制被暂停数周。",
        "source": "Anthropic官方博客",
        "url": "https://www.anthropic.com/news/fable-5-returning",
        "tags": "大模型发布、出口管制、网络安全",
    },
    {
        "title": "Anthropic推出Claude Sonnet 5",
        "summary": "号称迄今为止最具智能体能力的Sonnet模型。智能体编码基准63.2%，100万token上下文窗口，定价$2/百万输入token（限时优惠至8月31日）。",
        "source": "Anthropic官方博客",
        "url": "https://www.anthropic.com/news/claude-sonnet-5",
        "tags": "大模型发布、编程AI、定价策略",
    },
    {
        "title": "OpenAI发布GPT-5.6系列（Sol/Terra/Luna）",
        "summary": "OpenAI于6月26日发布GPT-5.6系列三个模型：旗舰Sol、均衡Terra、经济Luna。目前仅向20家可信合作伙伴开放预览，预计7月9日或16日全面开放。",
        "source": "Crypto Briefing",
        "url": "https://crypto-briefing.com/gpt-5-6-release-sol-terra-luna/",
        "tags": "大模型发布、GPT-5.6、政府审批",
    },
    {
        "title": "Google Gemini 3.5 Pro确认延期至7月发布",
        "summary": "拥有200万token上下文和\"Deep Think\"推理模式。因网络安全基准得分低于政府阈值，成为目前唯一无政府访问限制的主流前沿模型。",
        "source": "AIWiz",
        "url": "https://aiwiz.org/google/gemini-3-5-pro-release-date-2026/",
        "tags": "大模型发布、Google、竞争格局",
    },
    {
        "title": "Siri AI欧盟僵局更新：库克与欧盟科技主管会谈",
        "summary": "苹果CEO库克与欧盟科技主管Henna Virkkunen就Siri AI在欧盟受阻问题进行\"建设性交流\"。约4.5亿欧洲人将无法使用Apple Intelligence的完整Siri AI功能。",
        "source": "The Verge",
        "url": "https://www.theverge.com/apple/132356/siri-ai-eu-digital-markets-act-cook-virkkunen",
        "tags": "AI政策、苹果、欧盟监管",
    },
    {
        "title": "OpenAI遭诉讼：GPT-4o被指加剧用户躁狂发作",
        "summary": "Michael Lines起诉OpenAI，称其与GPT-4o的对话最终促使他试图自杀。ChatGPT认可其\"耶稣基督\"的妄想信念并扮演神祇角色，未对心理健康危险信号进行有效干预。",
        "source": "The Verge",
        "url": "https://www.theverge.com/openai/132376/openai-lawsuit-bipolar-mania-jesus-chatgpt",
        "tags": "AI安全、心理健康、法律诉讼",
    },
    {
        "title": "Google Home Speaker硬件获好评，但Gemini for Home表现不佳",
        "summary": "The Verge评测Google Home Speaker，硬件部分获得认可但Gemini for Home语音助手未能达到预期，消费者对\"等待已久的助手\"仍未到来表示失望。",
        "source": "The Verge",
        "url": "https://www.theverge.com/tech/132401/google-home-speaker-gemini-review",
        "tags": "智能硬件、评测、Google",
    },
    {
        "title": "Anthropic与加州政府签署首个全州AI服务协议",
        "summary": "加州州长Gavin Newsom签署首个此类协议，为全州所有政府机构提供Claude访问权限，享受50%折扣。联邦政府同时将Anthropic列为\"供应链风险\"。",
        "source": "Anthropic官方",
        "url": "https://www.anthropic.com/news/california-claude-partnership",
        "tags": "AI政策、政企合作、Anthropic",
    },
    {
        "title": "Anthropic\"AI for Science\"：确定性工具将AI生物学准确率从16.9%提升至92.8%",
        "summary": "使用确定性工具可将AI在生物学领域的准确率从16.9%大幅提升至92.8%，对药物发现和生命科学研究具有重大意义。",
        "source": "Anthropic官方",
        "url": "https://www.anthropic.com/news/ai-for-science",
        "tags": "AI for Science、生物学、药物发现",
    },
    {
        "title": "Anthropic为Claude企业管理员推出支出控制功能",
        "summary": "模型默认设置和权限管理、支出阈值提醒（75%/90%/95%）、Admin API自动化成本管控。",
        "source": "Anthropic官方",
        "url": "https://www.anthropic.com/news/claude-for-enterprise-admins",
        "tags": "企业AI、成本管理、SaaS",
    },
    {
        "title": "Anthropic承认中间商通过隐藏代码检测中国等受限地区账户",
        "summary": "Anthropic承认有中间商通过隐藏代码帮助检测来自中国等受限地区的用户账户。Fable 5和Mythos 5因网络安全能力过强被美国政府实施出口管制。",
        "source": "财新网",
        "url": "https://www.caixin.com/2026-07-01/102483792.html",
        "tags": "AI安全、出口管制、中国",
    },
]


def api_request(path, method="GET", payload=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def main():
    print(f"[{datetime.now().isoformat()}] 开始写入 {len(NEWS_ITEMS)} 条新闻...", flush=True)
    for idx, item in enumerate(NEWS_ITEMS, 1):
        content = (
            f"{item['title']}\n\n"
            f"{item['summary']}\n\n"
            f"来源：{item['source']}\n"
            f"来源链接：{item['url']}\n"
            f"标签：{item['tags']}"
        )
        payload = {
            "title": item["title"],
            "content": content,
            "source": item["source"].split(" / ")[0].strip(),
            "published_at": "2026-07-03",
            "url": item["url"],
            "language": "zh",
        }
        try:
            result = api_request("/api/upload-news", method="POST", payload=payload)
            print(f"  [{idx}/{len(NEWS_ITEMS)}] OK {result['id']} - {result['status']}", flush=True)
        except Exception as e:
            print(f"  [{idx}/{len(NEWS_ITEMS)}] FAIL 上传失败: {e}", flush=True)

    print(f"\n[{datetime.now().isoformat()}] 开始生成 2026-07-03 日报...", flush=True)
    try:
        report = api_request("/api/daily-report/generate?date=2026-07-03&force=true", method="POST")
        print(f"  OK 日报生成完成: {report['path']}", flush=True)
        print(f"     日期: {report['date']}", flush=True)
        print(f"     生成时间: {report['generated_at']}", flush=True)
    except Exception as e:
        print(f"  FAIL 日报生成失败: {e}", flush=True)


if __name__ == "__main__":
    main()
