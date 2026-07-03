"""
AI舆情分析日报系统 - 后端入口
"""
from src.config import OPENAI_API_KEY, NEWS_LIMIT


def main():
    """系统主入口"""
    print("=" * 50)
    print("AI舆情分析日报系统 - 后端服务")
    print("=" * 50)
    print(f"模型: {OPENAI_API_KEY[:6] + '***' if OPENAI_API_KEY else '未配置'}")
    print(f"新闻采集数量: {NEWS_LIMIT}")
    print("\n阶段流程:")
    print("1. 数据层: 获取AI新闻数据")
    print("2. 结构化层: Schema设计与抽取")
    print("3. 分析层: 热点聚合与事件分析")
    print("4. 输出层: 日报Markdown/图表/HTML生成")


if __name__ == "__main__":
    main()
