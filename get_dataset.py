from bilibili_api import search, sync
import pandas as pd
import time
import asyncio
import os
import yaml  # 添加yaml支持

os.chdir(os.path.dirname(os.path.abspath(__file__)))

config = {}
# 读取配置文件
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 全局变量
df_search_data = pd.DataFrame()
dataset_dir = config['dataset_dir']

keyword = config['keyword']
day_distance = config['day_distance']
if_set_day_limit = config['if_set_day_limit']
day_limit = config['day_limit']
num_limit = config['num_limit']  # 用于记录连续无数据的天数
sleep_time = config['sleep_time']  # 爬取间隔时间

def get_day(i): #获取i天前的日期
    #输出i天前的日期
    return time.strftime("%Y-%m-%d", time.localtime(time.time() - i*24*60*60))


async def fetch_data():
    global day_distance, df_search_data, num_limit
    
    stop_crawling = True
    
    while stop_crawling:
        day_distance += 1
        now_page = 1  # 从第一页开始
        df_search_day = pd.DataFrame() # 一天的数据
        has_data = True
        
        current_date = get_day(day_distance - 1)
        near_date = get_day(day_distance)
        
        print(f"正在爬取 {current_date} 到 {near_date} 的数据")
        
        try:
            while has_data:
                try:
                    result = await search.search_by_type(
                        keyword=keyword,
                        search_type=search.SearchObjectType.VIDEO,
                        page=now_page,
                        time_start=near_date,
                        time_end=current_date
                    )

                    # 检查是否有结果
                    if not result or 'result' not in result or not result['result']:
                        print(f"    第{now_page}页无数据，停止翻页")
                        has_data = False
                        break
                    
                    df_search_page = pd.DataFrame(result['result']) # 将本页数据转换为DataFrame
                    df_search_day = pd.concat([df_search_day, df_search_page])  # 将本页数据合并到当天数据
                    
                    print(f'    已爬取第{now_page}页，本页{len(df_search_page)}条数据')
                    
                    # 检查是否还有更多页
                    if len(df_search_page) < 42:  # B站默认每页42条
                        print(f"    本页只有{len(df_search_page)}条数据，停止翻页")
                        has_data = False
                        break
                        
                    now_page += 1  # 翻页
                    await asyncio.sleep(sleep_time)  # 添加延迟避免请求过快

                except Exception as e:
                    print(f'    爬取第{now_page}页时发生异常: {str(e)}')
                    has_data = False
                    break

            data_count = len(df_search_day)
            print(f'    {current_date}——{near_date}日数据爬取完毕')
            print(f'    一共{data_count}条数据')

            if not df_search_day.empty:
                df_search_data = pd.concat([df_search_data, df_search_day]) # 将当天数据合并到总数据
                print(f'    已将{data_count}条数据合并到总数据')
                print('-'*50)

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
    try:
        os.makedirs(dataset_dir, exist_ok=True)
    except:
        pass

    df_search_data.to_csv(f'{dataset_dir}/{keyword}.csv', index=False, encoding='utf-8-sig')
    print('已导出数据集')
    print(df_search_data.shape)

if __name__ == "__main__":
    #计时
    start_time = time.time()
    asyncio.run(main())
    print(f'爬取完成，耗时{(time.time() - start_time) / 60}分')