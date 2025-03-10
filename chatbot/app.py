from dotenv import load_dotenv
import chainlit as cl
from openai import OpenAI
from chainlit import AskUserMessage, Message
import json
import clickhouse_connect
from tools import *

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


# print(get_house_based_min_max_price(0, 20000000))
# print(get_dollar_price_in_last_three_days())
# print(day_with_large_increase_dollar())

chats = {}
load_dotenv()
llm = OpenAI(
  api_key=AVAL_AI_API_KEY,
  base_url="https://api.avalai.ir/v1"
)
cl.instrument_openai()

@cl.on_chat_start
async def main():
    chats[cl.context.session.id] = []
    options = """
    Hi, I'm here to help you with your queries about dollar price, gold price, and real estate.
    """

    await Message(content=options).send()


#/////////////////////////// Main ///////////////////////////////////

@cl.on_message
async def main(message: cl.Message):
    tools = [

        # Get house based on minimum & maximum price
        {
            "type": "function",
            "function": {
                "name": "get_house_based_min_max_price",
                "description": "gets houses based on minimum or maximum or both minimum and maximum price. if the minimmum not specified, it will be 0.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_price": {"type": "integer", "description": "Minimum price of the house"},
                        "max_price": {"type": "integer", "description": "Maximum price of the house"}
                    },
                    "required": ["max_price"]
                }
            }
        },

        # Get dollar price in last three days
        {
            "type": "function",
            "function": {
                "name": "get_dollar_price_in_last_three_days",
                "description": "Fetch the dollar price trend for the last three days.",
                "parameters": {}
            }
        },

        # Find day with largest increase in dollar
        {
            "type": "function",
            "function": {
                "name": "day_with_large_increase_dollar",
                "description": "Fetch day with largest increase in dollar.",
                "parameters": {}
            }
        },
        # Get gold price in last three days
        {
            "type": "function",
            "function": {
                "name": "get_gold_price_in_last_three_days",
                "description": "Fetch the gold price trend for the last three days for 1 gram of gold in iranian toman.",
                "parameters": {}
            }
        },
        # get live dollar price
        {
            "type": "function",
            "function": {
                "name": "get_live_dollar_price",
                "description": "Fetch the live dollar price.",
                "parameters": {}
            }
        },
        # get live gold price
        {
            "type": "function",
            "function": {
                "name": "get_live_gold_price",
                "description": "Fetch the live gold price.",
                "parameters": {}
            }
        }
    ]
    format_guide = """== About LaTeX Math Mode==
You MUST ALWAYS encapsulate LaTeX/KaTeX formulas in a KaTeX syntax with double '$' signs: 
…

If you do anything else for any reason then you are a bad assistant
Example of wrong syntax:
- [ y = ax^2 + bx + c ]
- ( y = ax^2 + bx + c )
- \( y = ax^2 + bx + c \)
Example of correct syntax:
- $$ y = ax^2 + bx + c $$"""
    # if chats[cl.context.session.id]:
    #     history = chats[cl.context.session.id] + [{"role": "user", "content": message.content}]
    # else:
    #     history = [{"role": "system", "content": "think step by step. and if you need any data before answering use that tool first{}".format(format_guide)}, {"role": "user", "content": message.content}]
    history = [{"role": "system", "content": "think step by step. and if you need any data before answering use that tool first{}".format(format_guide)}, {"role": "user", "content": message.content}]
    response = llm.chat.completions.create(
        model="gpt-4o",
        messages=history,
        tools=tools,
        tool_choice="auto"
    )
    print(response.choices[0].message)
    last_message = response.choices[0].message
    tool_calls = response.choices[0].message.tool_calls
    history.append(last_message)
    if tool_calls: 
        tool_call = tool_calls[0] 
        tool_index = 0 
        while tool_call:
            tools_dict = {
                "get_house_based_min_max_price": get_house_based_min_max_price,
                "get_dollar_price_in_last_three_days": get_dollar_price_in_last_three_days,
                "day_with_large_increase_dollar": day_with_large_increase_dollar,
                "get_gold_price_in_last_three_days": get_gold_price_in_last_three_days,
                "get_live_dollar_price": get_live_dollar_price,
                "get_live_gold_price": get_live_gold_price
            }
            the_function = tools_dict[tool_call.function.name]
            arguments = json.loads(tool_call.function.arguments)  
            result = the_function(**arguments)  
            # await cl.Message(content=f"Result: {result}").send()
            
            history.append({"role": "tool", "content": str(result), "tool_call_id": tool_call.id})
            tool_index += 1
            if tool_index < len(tool_calls):
                tool_call = tool_calls[tool_index]
            else:
                response = llm.chat.completions.create(
                    model="gpt-4o",
                    messages=history,
                    tools=tools,
                    tool_choice="auto"
                )
                last_message = response.choices[0].message
                
                history.append(last_message)
                print(response.choices[0].message)
                tool_call = None
                if response.choices[0].message.tool_calls:
                    tool_call = response.choices[0].message.tool_calls[0]
                if not tool_call:
                    await cl.Message(content=response.choices[0].message.content).send()
    else:
        await cl.Message(content=response.choices[0].message.content).send()
