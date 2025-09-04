from bilibili_api import search, sync
import pandas as pd
import time
import asyncio
import os
import yaml
from math import ceil

os.chdir(os.path.dirname(os.path.abspath(__file__)))

config = {}
# 读取配置文件
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 全局变量
df_search_data = pd.DataFrame()
keyword = config['keyword']
day_distance = config['day_distance']
if_set_day_limit = config['if_set_day_limit']
day_limit = config['day_limit']
num_limit = config['num_limit']  # 用于记录连续无数据的天数

def get_day(i): #获取i天前的日期
    #输出i天前的日期
    return time.strftime("%Y-%m-%d", time.localtime(time.time() - i*24*60*60))

async def fetch_page_data(page, near_date, current_date, semaphore):
    """获取单页数据"""
    async with semaphore:
        try:
            result = await search.search_by_type(
                keyword=keyword,
                search_type=search.SearchObjectType.VIDEO,
                page=page,
                time_start=near_date,
                time_end=current_date
            )
            return result
        except Exception as e:
            print(f'    爬取第{page}页时发生异常: {str(e)}')
            return None

async def fetch_day_data(current_date, near_date):
    """并发获取一天的所有数据"""
    global day_distance, df_search_data, num_limit
    
    print(f"正在爬取 {current_date} 到 {near_date} 的数据")
    
    # 先获取第一页以了解总数据量
    first_page_result = await search.search_by_type(
        keyword=keyword,
        search_type=search.SearchObjectType.VIDEO,
        page=1,
        time_start=near_date,
        time_end=current_date
    )
    
    if not first_page_result or 'numResults' not in first_page_result:
        print(f"    无法获取总数据量，跳过该日期")
        return 0
    
    total_results = first_page_result['numResults']
    print(f"    总数据量: {total_results}条")
    
    if total_results == 0:
        return 0
    
    # 计算总页数
    total_pages = ceil(total_results / 42)
    print(f"    总页数: {total_pages}")
    
    # 创建信号量限制并发数
    semaphore = asyncio.Semaphore(5)  # 同时最多5个请求
    
    # 准备所有页面的任务
    tasks = []
    for page in range(1, total_pages + 1):
        tasks.append(fetch_page_data(page, near_date, current_date, semaphore))
    
    # 并发执行所有任务
    results = await asyncio.gather(*tasks)
    
    # 处理结果
    df_search_day = pd.DataFrame()
    for i, result in enumerate(results, 1):
        if result and 'result' in result and result['result']:
            df_search_page = pd.DataFrame(result['result'])
            df_search_day = pd.concat([df_search_day, df_search_page])
            print(f'    已获取第{i}页数据，本页{len(df_search_page)}条数据')
        else:
            print(f'    第{i}页无数据或获取失败')
    
    return len(df_search_day)

async def fetch_data():
    global day_distance, df_search_data, num_limit
    
    stop_crawling = True
    
    while stop_crawling:
        day_distance += 1
        current_date = get_day(day_distance - 1)
        near_date = get_day(day_distance)
        
        try:
            data_count = await fetch_day_data(current_date, near_date)
            
            print(f'    {current_date}——{near_date}日数据爬取完毕')
            print(f'    一共{data_count}条数据')

            # 检查停止条件
            if if_set_day_limit:
                if current_date == day_limit:
                    print('达到设定的日期限制，爬虫停止')
                    stop_crawling = False
            else:
                if data_count == 0:
                    num_limit -= 1
                    if num_limit <= 0:
                        print(f'连续{config["num_limit"]}天无数据，爬虫停止')
                        stop_crawling = False
                else:
                    num_limit = config['num_limit']  # 重置计数器

        except Exception as e:
            print(f'处理日期 {current_date} 时发生错误: {str(e)}')
            break

async def main():
    await fetch_data()
    print('已爬取搜索结果')
    df_search_data.to_csv(f'{keyword}_dataset.csv', index=False, encoding='utf-8-sig')
    print('已导出数据集')
    print(df_search_data.shape)

if __name__ == "__main__":
    asyncio.run(main())