from src.logger import get_logger
from src.cache import Cache

logger = get_logger()
cache = Cache()

def generate_analytics_report():
    logger.info("Generating analytics report")
    total_messages = 0
    successful_messages = 0
    total_time = 0
    group_stats = {}

    for group, performance in cache.group_performance.items():
        total_messages += performance['count']
        successful_messages += performance['success_count']
        total_time += performance['total_time']
        success_rate = (performance['success_count'] / performance['count']) * 100 if performance['count'] > 0 else 0
        avg_time = performance['total_time'] / performance['count'] if performance['count'] > 0 else 0
        group_stats[group] = {
            'success_rate': success_rate,
            'avg_time': avg_time
        }

    overall_success_rate = (successful_messages / total_messages) * 100 if total_messages > 0 else 0
    overall_avg_time = total_time / total_messages if total_messages > 0 else 0

    report = f"""
    Analytics Report:
    Total messages sent: {total_messages}
    Successful messages: {successful_messages}
    Overall success rate: {overall_success_rate:.2f}%
    Overall average send time: {overall_avg_time:.2f} seconds

    Top 5 performing groups:
    """

    sorted_groups = sorted(group_stats.items(), key=lambda x: x[1]['success_rate'], reverse=True)[:5]
    for group, stats in sorted_groups:
        report += f"  {group}: Success rate {stats['success_rate']:.2f}%, Avg time {stats['avg_time']:.2f}s\n"

    logger.info(report)
    with open('data/analytics_report.txt', 'w') as f:
        f.write(report)

    logger.info("Analytics report generated and saved to data/analytics_report.txt")
