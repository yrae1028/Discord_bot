import discord
from discord.ext import commands
import datetime
import os
import asyncio
import csv
import random
import json

def main():
    prefix = '.'
    intents = discord.Intents.all()

    client = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive=True, help_command=None)

    @client.event
    async def on_ready():
        print("Bot is ready")

        # 매주 일요일 23:59에 개인 메시지를 보낼 작업 예약
        while True:
            now = datetime.datetime.now()
            days_until_sunday = (6 - now.weekday()) % 7
            sunday_23_59 = now + datetime.timedelta(days=days_until_sunday, hours=-now.hour + 23, minutes=-now.minute + 59, seconds=-now.second)
        
            delta = sunday_23_59 - now
            await asyncio.sleep(delta.total_seconds())
        
            user_id = 1120174667529990268
            user = await client.fetch_user(user_id)
            await send_ranking_dm(user)

    async def send_ranking_dm(user):
      with open("data/score.json", 'r', encoding="utf8") as f:
        dict = json.load(f)

      sorted_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)

      rank = 1
      rank_msg = ""
      for item in sorted_dict:
        rank_msg += f"{rank}. {item[0]} - {item[1]} Points\n"
        rank += 1

      embed = discord.Embed(
        title=":trophy: Quiz Ranking",
        description=rank_msg,
        color=0x00A2FF,
      )
      await user.send(embed=embed)       
      await asyncio.sleep(60)
      
      with open("data/score.json", 'r', encoding="utf8") as f:
        dict = json.load(f)
      dict.clear()

      with open("data/score.json", 'w', encoding='utf-8') as f: 
        json.dump(dict, f, ensure_ascii=False)   

    class Quiz:
        def __init__(self):
            self.quizDict = {}
            self.used_problems = []
            with open("./data/quiz.csv", 'r', encoding='utf8') as f:
                reader = csv.reader(f)
                for row in reader:
                    self.quizDict[row[0]] = row[1]  # key: row[0], value: row[1]

        def new(self):
            if len(self.quizDict) == len(self.used_problems):
                self.used_problems.clear()
                return None, None

            problemList = list(set(self.quizDict.keys()) - set(self.used_problems))
            problem = random.choice(problemList)
            answer = self.quizDict[problem]
            self.used_problems.append(problem)
            return problem, answer

    quiz = Quiz()

    @client.command(name="Quiz")
    @commands.has_permissions(administrator=True)
    async def quiz_command(ctx):
      while True:  
        problem, answer = quiz.new()
        
        if problem is not None and answer is not None:
           embed = discord.Embed(title=":question: Quiz", description=problem, color=0x00A2FF)
           await ctx.send(embed=embed)

           def checkAnswer(message):
             return message.channel == ctx.channel and message.content.strip().lower() == answer.strip().lower()

           answer_received = False
           while not answer_received:
            try:
              msg = await client.wait_for("message", check=checkAnswer)
              with open("data/score.json", 'r', encoding="utf8") as f:
                dict = json.load(f)

              if not msg.author.bot and msg.author.name not in dict.keys():
                dict[msg.author.name] = 1
              elif not msg.author.bot:
                dict[msg.author.name] = dict[msg.author.name] + 1

              with open("data/score.json", 'w', encoding='utf-8') as f:
                json.dump(dict, f, ensure_ascii=False)

              embed = discord.Embed(
                title=":trophy: [{msg.author.name}], Correct Answer! +1 point ",
                description=f"Now, [{msg.author.name}] has [{dict[msg.author.name]}] point(s).",
                color=0x00FF00,
              )
              await ctx.send(embed=embed)
              answer_received = True
            except asyncio.CancelledError:
              pass

            await asyncio.sleep(3)
        else:    
          embed = discord.Embed(
            title=":bulb: All Quizzes Have Been Solved.",
            description="Congrets! BUDDHIs. You have become wise. The quiz is reset.",
            color=0x00A2FF,
          )
          await ctx.send(embed=embed)
          break


    @client.command(name="Score")
    async def score_command(ctx, user: discord.Member = None):
        user = user or ctx.author

        with open("data/score.json", 'r', encoding="utf8") as f:
            dict = json.load(f)

        if user.name not in dict.keys():
            score = 0
        else:
            score = dict[user.name]

        embed = discord.Embed(
            title=":bar_chart: Check your point(s)",
            description=f"{user.mention}, you have [{score}] Point(s).",
            color=0x00A2FF,
        )
        await ctx.send(embed=embed)

    @client.command(name="Ranking")
    async def ranking_command(ctx):
        with open("data/score.json", 'r', encoding="utf8") as f:
            dict = json.load(f)

        sorted_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)

        rank = 1
        rank_msg = ""
        for item in sorted_dict:
            rank_msg += f"{rank}. {item[0]} - {item[1]}Points\n"
            rank += 1

        embed = discord.Embed(
            title=":trophy: Quiz Ranking",
            description=rank_msg,
            color=0x00A2FF,
        )
        await ctx.send(embed=embed)

    @client.command(name="Reset")
    @commands.has_permissions(administrator=True)
    async def reset_scores(ctx):
        with open("data/score.json", 'r', encoding="utf8") as f:
            dict = json.load(f)

        dict.clear()

        with open("data/score.json", 'w', encoding='utf-8') as f:
            json.dump(dict, f, ensure_ascii=False)

        embed = discord.Embed(
            title=":arrows_counterclockwise: Score has been reset",
            description="All user's score have been reset.",
            color=0xFFA500,
        )
        await ctx.send(embed=embed)

    @reset_scores.error
    async def reset_scores_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title=":x: Insufficient permissions.",
                description="Administrator permissions are required.",
                color=0xFF0000,
            )
            await ctx.send(embed=embed)

    @client.command(name="Help")
    async def help_command(ctx):
        embed = discord.Embed(
            title=":rotating_light: Help Center 'Playground Quiz'",
            description="""Welcome to the Playground Quiz channel, BUDDHIs.
:white_check_mark: Participants earn points by answering quizzes correctly.:100:
:white_check_mark: Every week, there's a special gift for the person who ranks first in the quiz ranking.
:bulb: Become wise, be reborn, and gain enlightenment.:person_in_lotus_position:
:scroll: Rules :scroll: 
:one: Once the correct answer to a question appears, the next question will come out.
:two: The quiz ends when all the questions are finished.
:three: Consult with each other to find the right answer.
:four: Playground Quiz commands 
.Quiz - Starts the Quiz competition. This command is only possible for administrators. 
.Score - Check your points. Points are reset every Monday at 00:00. 
.Ranking - Shows the current ranking. Rankings are reset every Monday at 00:00. 
.Help - You can see all commands. 
.Reset - Resets all users' point information.This command is only possible for administrators.
Please enjoy the quiz BUDDHIs.:100:""",
            color=0xFFA500,
        )
        await ctx.send(embed=embed)

    @client.command(name="Cleanup")
    @commands.has_permissions(manage_messages=True)
    async def cleanup_command(ctx, amount: str):
      if amount.isdigit():
        num_amount = int(amount)
        await ctx.channel.purge(limit=num_amount + 1)
        embed = discord.Embed(
            title=":white_check_mark: Success!",
            description=f"{num_amount} message(s) cleanup Sucessful.",
            color=0x00FF00,
        )
        await ctx.send(embed=embed, delete_after=5)
      elif amount.lower() == "all":
        await ctx.channel.purge()
        await asyncio.sleep(1)
        embed = discord.Embed(
            title=":white_check_mark: Success!",
            description="All message(s) cleanup Sucessful.",
            color=0x00FF00,
        )
        await ctx.send(embed=embed, delete_after=5)
      else:
        embed = discord.Embed(
            title=":x: Error",
            description="Please enter a valid number or 'All'.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)

    access_token = os.environ["BOT_TOKEN"]
    client.run(access_token)

if __name__ == '__main__':
    main()
