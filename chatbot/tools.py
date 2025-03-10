import datetime
import jdatetime
import clickhouse_connect
import json

def gregorian_to_hijri_shamsi(gregorian_date: str) -> str:
    """
    Converts a Gregorian date (YYYY-MM-DD) to Hijri Shamsi (Jalali/Persian) date.

    :param gregorian_date: Date in 'YYYY-MM-DD' format
    :return: Hijri Shamsi date in 'YYYY-MM-DD' format
    """
    jalali = jdatetime.date.fromgregorian(date=gregorian_date)
    shamsi_year, shamsi_month, shamsi_day = jalali.year, jalali.month, jalali.day
    return f"{shamsi_year:04d}-{shamsi_month:02d}-{shamsi_day:02d}"

def hijri_to_grergorian(hijri_date: str) -> str:
    """
    Converts a Hijri Shamsi (Jalali/Persian) date to Gregorian date (YYYY-MM-DD).

    :param hijri_date: Date in 'YYYY-MM-DD' format
    :return: Gregorian date in 'YYYY-MM-DD' format
    """
    year, month, day = map(int, hijri_date.split("-"))
    gregorian = jdatetime.date(year, month, day).togregorian()
    return f"{gregorian.year:04d}-{gregorian.month:02d}-{gregorian.day:02d}"

with open("config.json", "r") as f:
    config = json.load(f)
    ch_config = config["clickhouse"]
    CLICKHOUSE_HOST = ch_config["host"]
    CLICKHOUSE_PORT = ch_config["port"]
    CLICKHOUSE_USER = ch_config["user"]
    CLICKHOUSE_PASSWORD = ch_config["password"]
    CLICKHOUSE_DATABASE = ch_config["database"]
    AVAL_AI_API_KEY = config["aval_ai_api_key"]

# Connect to ClickHouse
client = clickhouse_connect.get_client(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT,
    username=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    database=CLICKHOUSE_DATABASE
)


def get_house_based_min_max_price(min_price=0, max_price=999999999):
    """
    gets houses based on minimum or maximum or both minimum and maximum price
    """
    print("get_house_based_min_max_price called")
    query = """
    SELECT * FROM real_estate
    WHERE TotalPrice BETWEEN {} AND {}
    """.format(min_price, max_price)
    results = client.query_df(query)
    try:
        results['CrawlDate'] = results['CrawlDate'].apply(lambda x: gregorian_to_hijri_shamsi(x))
    except:
        return "No data found"
    return results


def get_dollar_price_in_last_three_days():
    print("get_dollar_price_in_last_three_days called")
    query = """WITH daily_avg AS (
                SELECT
                    date,
                    AVG(price) AS avg_price
                FROM dollar_data
                WHERE date >= now() - INTERVAL 3 DAY
                GROUP BY date
            )
            SELECT
                date,
                avg_price,
                lagInFrame(avg_price, 1) OVER (ORDER BY date) AS previous_price,
                CASE
                    WHEN avg_price > lagInFrame(avg_price, 1) OVER (ORDER BY date) THEN 'Increased'
                    WHEN avg_price < lagInFrame(avg_price, 1) OVER (ORDER BY date) THEN 'Decreased'
                    ELSE 'No Change'
                END AS price_trend
            FROM daily_avg
            ORDER BY date ASC;"""
    results = client.query_df(query)
    results['date'] = results['date'].apply(lambda x: gregorian_to_hijri_shamsi(x))
    results["avg_price"] = results["avg_price"].apply(lambda x: int(x) // 10)
    return results

def day_with_large_increase_dollar():
    """
    Find the day with the largest increase in dollar price.
    """
    print("day_with_large_increase_dollar called")
    query = """
    SELECT date, 
           price, 
           COALESCE(price - lagInFrame(price, 1) OVER (ORDER BY date), 0) AS price_change
    FROM dollar_data
    ORDER BY price_change DESC
    LIMIT 1;
    """
    results = client.command(query)
    # results[0] is a string like '2022-01-01'
    # lets convert it to date
    gregorian_date_object = datetime.datetime.strptime(results[0], "%Y-%m-%d")

    results[0] = gregorian_to_hijri_shamsi(gregorian_date_object)  
    return "In Day {} Dollar Changed {} And Went From {} to {}".format(results[0], results[2], float(results[1]) - float(results[2]), results[1])



def get_gold_price_in_last_three_days():
    """gets gold price in last three days for 1 gram of gold"""
    print("get_gold_price_in_last_three_days called")
    query = """WITH daily_avg AS (
                SELECT
                    date,
                    AVG(price) AS avg_price
                FROM gold_data
                WHERE date >= now() - INTERVAL 3 DAY
                GROUP BY date
            )
            SELECT
                date,
                avg_price,
                lagInFrame(avg_price, 1) OVER (ORDER BY date) AS previous_price,
                CASE
                    WHEN avg_price > lagInFrame(avg_price, 1) OVER (ORDER BY date) THEN 'Increased'
                    WHEN avg_price < lagInFrame(avg_price, 1) OVER (ORDER BY date) THEN 'Decreased'
                    ELSE 'No Change'
                END AS price_trend
            FROM daily_avg
            ORDER BY date ASC;"""
    results = client.query_df(query)
    results['date'] = results['date'].apply(lambda x: gregorian_to_hijri_shamsi(x))
    results["avg_price"] = results["avg_price"].apply(lambda x: int(x) // 10)
    return results

def get_live_dollar_price():
    """
    Get the live dollar price.
    """
    print("get_live_dollar_price called")
    query = """
    SELECT datetime, price
    FROM dollar_data
    ORDER BY datetime DESC
    LIMIT 1;
    """
    results = client.command(query)
    # print(results)
    gregorian_date_object = datetime.datetime.strptime(results[0], "%Y-%m-%d %H:%M:%S")
    gregorian_date_object += datetime.timedelta(hours=3, minutes=30)
    time_object = gregorian_date_object.time()
    # add 2:30 hours to the time using timedelta
    # time_object += datetime.timedelta(hours=2, minutes=30)
    results[0] = gregorian_to_hijri_shamsi(gregorian_date_object)
    return f"Date: {results[0]}, Time: {time_object}, Price: {int(results[1]) // 10} Tomans"
def get_live_gold_price():
    """
    Get the live gold price.
    """
    print("get_live_gold_price called")
    query = """
    SELECT datetime, price
    FROM gold_data
    ORDER BY datetime DESC
    LIMIT 1;
    """
    results = client.command(query)
    # print(results)
    gregorian_date_object = datetime.datetime.strptime(results[0], "%Y-%m-%d %H:%M:%S")
    gregorian_date_object += datetime.timedelta(hours=3, minutes=30)
    time_object = gregorian_date_object.time()
    # add 2:30 hours to the time using timedelta
    # time_object += datetime.timedelta(hours=2, minutes=30)
    results[0] = gregorian_to_hijri_shamsi(gregorian_date_object)
    return f"Date: {results[0]}, Time: {time_object}, Price: {int(results[1]) // 10} Tomans"

# print(get_live_dollar_price())