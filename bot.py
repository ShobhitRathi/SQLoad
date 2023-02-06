import os
import openai
import discord
import itertools
from discord import app_commands

from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# NOT REQUIRED RIGHT NOW
# tree = app_commands.CommandTree(client)

# #BUG -[TODO - fix]
# @tree.command(name='touch', description='do not touch the bot please')
# async def self(interaction: discord.Interaction):
#     await interaction.response.send_message(f"It tickles me when you do that")

def closure(attributes, fds):
    try:
        # Split functional dependencies into individual tuples
        fds = [(fd.split('->')[0], fd.split('->')[1]) for fd in fds]
        closures = {}
        for i in range(1, len(attributes) + 2):
            for attribute_set in itertools.combinations(attributes, i):
                result = set(attribute_set)
                modified = True
                iteration_count = 0
                while modified:
                    modified = False
                    for fd in fds:
                        a, b = fd
                        if set(a) <= result:
                            result |= set(b)
                            if len(result) > len(attributes):
                                modified = True
                    iteration_count += 1
                    if iteration_count > 1000:
                        raise Exception("Infinite loop detected : Possible input mismatch (check your input again)")
                key = "".join(sorted(list(attribute_set))) + "+"
                closures[key] = result
        return closures
    except Exception as e:
        return f"An error occurred: {str(e)}"

@client.event
async def on_message(message):
    ##FUNCTIONAL DEPENDENCIES TASKS
    if message.content.startswith(";closure"):
        await message.channel.send("Enter the relational Schema R separated by comma:")

        def check(m):
            return m.content and m.author == message.author

        attributes = await client.wait_for("message", check=check)
        attributes = attributes.content.split(',')

        await message.channel.send("Enter the functional dependencies F separated by comma:")

        fds_string = await client.wait_for("message", check=check)
        fds_string = fds_string.content.split(',')

        result = closure(attributes, fds_string)
        if isinstance(result, str):
            await message.channel.send(result)
        else:
            formatted_result = ''
            for key, value in result.items():
                formatted_result += f'{key}: {list(value)}\n'

            await message.channel.send("Result: \n" + str(formatted_result))
    
    ##SQL BASED TASKS
    elif message.content.startswith(";texttosql"):
        await message.channel.send("Enter your database:")
        table_input = (await client.wait_for('message', check=lambda m: m.author == message.author)).content
        table_input = "###" + table_input + "\n"
        await message.channel.send("Enter your query:")
        query = "###{}\nSELECT".format((await client.wait_for('message', check=lambda m: m.author == message.author)).content)
        response = openai.Completion.create(
            model="code-davinci-002",
            prompt=table_input + query,
            temperature=0,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["#", ";"]
        )
        embed = discord.Embed(title="Your SQL query is: \n\n", color=0x292928)
        embed.add_field(name="", value=f"```sql\nSELECT {response['choices'][0]['text'].strip()}\n```", inline=False)
        await message.channel.send(embed=embed)
    elif message.content.startswith(";sqltotext"):
        await message.channel.send("Enter your SQL query:")
        natural_query = (await client.wait_for('message', check=lambda m: m.author == message.author)).content
        response2 = openai.Completion.create(
            engine="text-davinci-002",
            prompt="Translate this SQL query into natural language: " + natural_query,
            temperature=0,
            max_tokens=1024,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["#", ";"]
        )
        await message.channel.send("In natural language it translates to: \n" + response2["choices"][0]["text"].strip())
    
    ##DATALOG BASED TASKS
    elif message.content.startswith(";datalogtotext"):
        await message.channel.send("Enter your query:")
        datalog_query = (await client.wait_for('message', check=lambda m: m.author == message.author)).content
        response3 = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Translate this Datalog query into its natural language: " + datalog_query,
        temperature=0.2,
        max_tokens=1024,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )
        real_resp = response3["choices"][0]["text"]
        start_index = real_resp.find("This")
        if start_index != -1:
            real_resp = real_resp[start_index:]
        await message.channel.send("The natural language equivalent of the given Datalog query is: \n" + real_resp.strip())
    
    ##TUPLE CALCULUS TASKS
    elif message.content.startswith(";trctotext"):
        await message.channel.send("Enter your tuple relation calculus query:")
        trc_query = (await client.wait_for('message', check=lambda m: m.author == message.author)).content
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt="Translate this tuple relation calculus query into natural language: " + trc_query,
            temperature=0,
            max_tokens=1024,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        natural_lang = response["choices"][0]["text"]
        await message.channel.send("The natural language equivalent of the given tuple relation calculus query is: \n" + natural_lang.strip())
    
    ##ENTITY RELATIONSHIP TASKS
    # GENERATING ER DIAGRAMS - LOCKED UNTIL OpenAPI APPROVES DALL-E 2 BETA API CALLS
    # elif message.content.startswith(";erdiag"):
    #     await message.channel.send("Enter the ER diagram description:")
    #     description = (await client.wait_for('message', check=lambda m: m.author == message.author)).content
    #     prompt = "###\n" + description
    #     response = openai.Image.create(
    #         prompt=prompt,
    #         model="image-alpha-001"
    #     )
    #     image_data = response["data"]
    #     with open("erdiagram.jpg", "wb") as f:
    #         f.write(image_data)
    #     with open("erdiagram.jpg", "rb") as f:
    #         await message.channel.send(file=discord.File(f))

    # ER DESCRIPTION - function is working as expected, but the response from OpenAI is empty. (CLOSING THIS FUNCTION on 14.01.2022 @ (UTC+1) 19:14:58 CET till it gets fixed)
    # elif message.content.startswith(";erdesc"):
    #     await message.channel.send("Enter your ER query:")
    #     er_query = (await client.wait_for('message', check=lambda m: m.author == message.author)).content
    #     response4 = openai.Completion.create(
    #         engine="text-davinci-002",
    #         prompt=er_query,
    #         temperature=0,
    #         max_tokens=2048,
    #         top_p=1.0,
    #         frequency_penalty=0.0,
    #         presence_penalty=0.0
    #     )
    #     text_description = response4["choices"][0]["text"]
    #     print(response4["choices"][0])
    #     await message.channel.send("The natural language equivalent of the given tuple relation calculus query is: \n" + text_description.strip())

    ##HELP
    elif message.content.startswith(";help"):
        await message.channel.send("This bot is made for working on the concepts of Datamodelling and Databases\n"
                                   "**DISCLAIMER**: _Note that the answers generated the bot are done using OpenAI API - <https://openai.com/api/> and might not always be correct. However the answers generated are mostly precise and accurate to the actual answer (if they differ) and are constantly being improved._\n"
                                   "BOT PREFIX - `;` \n\n"
                                   "Currently, This bot accepts the following commands:\n\n"
                                   "0 - `;help` - displays this message\n\n"
                                   "**FUNCTIONAL DEPENDENCIES TASKS**\n"
                                   "1 - `;closure` - prompts for a relational Schema R and the functional Dependencies F, then returns the closure of all attributes\n\n"
                                   "**SQL TASKS**\n"
                                   "2 - `;texttosql` - prompts for a database and a query, then generates a SQL response query\n"
                                   "3 - `;sqltotext` - prompts for a SQL query, then translates it into its natural language\n\n"
                                   "**DATALOG TASKS**\n"
                                   "4 - `;datalogtotext` - prompts for a datalog query, then translates it into its natural language\n\n"
                                   "**TUPLE RELATIONAL CALCULUS TASKS**\n"
                                   "5 - `;trctotext` - prompts for a TRC query, then translates it into its natural language\n\n"
                                   "**MISC\n**"
                                   "6 - `;creator` - gives details about this bot developer")
    
    ##MISC
    elif message.content.startswith(";creator"):
        embed = discord.Embed(title="Bot Creator", color=0x292928)
        embed.add_field(name="Name", value="Shobhit Rathi", inline=True)
        author = await client.fetch_user(os.getenv("CREATOR_ID"))
        embed.add_field(name="Discord", value=author.mention, inline=True)
        embed.add_field(name="LinkedIn", value="[LinkedIn Profile](https://www.linkedin.com/in/shobhit-rathi-10/)", inline=False)
        embed.set_footer(text="I created this bot using OpenAI - feel free to reach out")
        await message.channel.send(embed=embed)


client.run(os.getenv("TOKEN_ID"))
