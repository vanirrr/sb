import discord
from discord.ext import commands
from instagrapi import Client
from instagramy import InstagramUser
import os
import json

# Replace with your Instagram credentials
INSTAGRAM_USERNAME = 'vbot_api'
INSTAGRAM_PASSWORD = 'gam555enM'

# Create a new Discord bot client with a specific command prefix
bot = commands.Bot(command_prefix='v', intents=discord.Intents.all())

# Initialize Instagrapi client
instagrapi_client = Client()
instagrapi_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

FOLLOWING_DATA_FILE = "following_data.json"

def login_instagram():
    loader = instagrapi_client
    return loader

@bot.command(name='search_username_by_id')
async def search_username_by_id(ctx, user_id: int):
    try:
        # Use instagrapi to get the username by user ID
        user_info = instagrapi_client.user_info(user_id)
        username = user_info.username

        # Create and send the embed message
        embed = discord.Embed(title="Username Lookup", color=discord.Color.from_str("#8B0000"))
        embed.add_field(name="User ID", value=user_id, inline=False)
        embed.add_field(name="Username", value=username, inline=False)
        embed.set_footer(text="VBOT SERVICES")

        await ctx.send(embed=embed)
    except Exception as e:
        # Handle any exceptions and send an error message
        embed = discord.Embed(title="Error", color=discord.Color.from_str("#8B0000"))
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.set_footer(text="VBOT SERVICES")
        await ctx.send(embed=embed)
        

@bot.command(name='track_following')
async def track_following(ctx, *target_usernames):
    loader = login_instagram()
    if not loader:
        await ctx.send(f"Failed to log in as {INSTAGRAM_USERNAME}.")
        return

    following_data = load_following_data()
    embed = discord.Embed(title="Track Following Changes", color=discord.Color.from_str("#8B0000"))

    for target_username in target_usernames:
        try:
            profile = InstagramUser(target_username, session=instagrapi_client)
            current_following = {follow.username for follow in profile.following}

            if target_username in following_data:
                previous_following = set(following_data[target_username].get('followings', []))
                new_following = current_following - previous_following

                if new_following:
                    new_following_usernames = [instagrapi_client.user_info_by_username(username).username for username in new_following]
                    embed.add_field(name=f"User {target_username}", value=f"Started following: {', '.join(new_following_usernames)}", inline=False)
                else:
                    embed.add_field(name=f"User {target_username}", value="No new followings detected.", inline=False)

                following_data[target_username]['followings'] = list(current_following)
                following_data[target_username]['count'] = len(current_following)
            else:
                embed.add_field(name="Tracking new user", value=target_username, inline=False)
                following_data[target_username] = {
                    'count': len(current_following),
                    'followings': list(current_following)
                }

        except Exception as e:
            embed.add_field(name=f"Error tracking {target_username}", value=str(e), inline=False)

    save_following_data(following_data)
    embed.set_footer(text="VBOT SERVICES")
    await ctx.send(embed=embed)

@bot.command(name='list_followers')
async def list_followers(ctx, target_username: str):
    try:
        profile = InstagramUser(target_username, session=instagrapi_client)
        followers = profile.followers
        followers_list = [follower.username for follower in followers]

        embed = discord.Embed(title=f"Followers of {target_username}", color=discord.Color.from_str("#8B0000"))

        if followers_list:
            # Discord has a character limit, we may need to split messages
            message = ""
            for follower in followers_list:
                if len(message) + len(follower) + 2 < 2000:
                    message += f"{follower}\n"
                else:
                    embed.description = message
                    await ctx.send(embed=embed)
                    message = f"{follower}\n"
            if message:
                embed.description = message
        else:
            embed.description = "No followers found."

        embed.set_footer(text="VBOT SERVICES")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", color=discord.Color.from_str("#8B0000"))
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.set_footer(text="VBOT SERVICES")
        await ctx.send(embed=embed)

@bot.command(name='search_follower')
async def search_username_in_followers(ctx, target_username: str, search_username: str):
    try:
        profile = InstagramUser(target_username, session=instagrapi_client)
        followers = profile.followers
        found = any(follower.username.lower() == search_username.lower() for follower in followers)

        embed = discord.Embed(title=f"Search Follower in {target_username}", color=discord.Color.from_str("#8B0000"))
        if found:
            embed.description = f"Username {search_username} is a follower of {target_username}."
        else:
            embed.description = f"Username {search_username} is not a follower of {target_username}."

        embed.set_footer(text="VBOT SERVICES")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", color=discord.Color.from_str("#8B0000"))
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.set_footer(text="VBOT SERVICES")
        await ctx.send(embed=embed)

@bot.command(name='latest_post_engagement')
async def view_latest_post_engagement(ctx, target_username: str):
    try:
        profile = instagrapi_client.user_info_by_username(target_username)
        latest_post = profile.media[0]  # Assuming the latest post is the first one

        embed = discord.Embed(title=f"Latest Post Engagement by {target_username}", color=discord.Color.from_str("#8B0000"))
        embed.add_field(name="Post ID", value=str(latest_post.pk), inline=False)
        embed.add_field(name="Caption", value=latest_post.caption_text, inline=False)

        await ctx.send(embed=embed)

        await ctx.send("Enter `e` for engagement, `c` for comments, or `l` for likes:")
        choice = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
        embed.clear_fields()
        
        if choice.content.lower() == 'e':
            embed.add_field(name="Likes", value=str(latest_post.like_count), inline=False)
            embed.add_field(name="Comments Count", value=str(latest_post.comment_count), inline=False)
        elif choice.content.lower() == 'c':
            comments = [f"{comment.user.username}: {comment.text}" for comment in latest_post.comments]
            embed.add_field(name="Comments", value="\n".join(comments), inline=False)
        elif choice.content.lower() == 'l':
            likers = [like.username for like in latest_post.likers]
            embed.add_field(name="Likes", value=", ".join(likers), inline=False)
        else:
            embed.description = "Invalid choice. Please try again."
        
        embed.set_footer(text="VBOT SERVICES")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", color=discord.Color.from_str("#8B0000"))
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.set_footer(text="VBOT SERVICES")
        await ctx.send(embed=embed)

@bot.command(name='cmd')
async def cmd_command(ctx):
    embed = discord.Embed(title="Commands", description="List of available commands", color=discord.Color.from_str("#8B0000"))
    embed.add_field(name="vtrack_following <target_usernames>", value="Track following changes of target users", inline=False)
    embed.add_field(name="vlist_followers <target_username>", value="List followers of the target user", inline=False)
    embed.add_field(name="vsearch_follower <target_username> <search_username>", value="Search for a follower in the target user's followers", inline=False)
    embed.add_field(name="vlatest_post_engagement <target_username>", value="View engagement details of the target user's latest post", inline=False)
    embed.add_field(name="vget_user_info <target_username>", value="Get information about the target user's Instagram profile", inline=False)
    embed.add_field(name="vsearch_username_by_id <user_id>", value="Search for a username by user ID", inline=False)
    embed.set_footer(text="VBOT SERVICES")
    await ctx.send(embed=embed)

@bot.command(name='get_user_info')
async def get_user_info(ctx, target_username: str):
    try:
        profile = instagrapi_client.user_info_by_username(target_username)

        embed = discord.Embed(title=f"User Info for {target_username}", color=discord.Color.from_str("#8B0000"))
        embed.add_field(name="Username", value=profile.username, inline=False)
        embed.add_field(name="Full Name", value=profile.full_name, inline=False)
        embed.add_field(name="Biography", value=profile.biography, inline=False)
        embed.add_field(name="Followers", value=str(profile.follower_count), inline=False)
        embed.add_field(name="Following", value=str(profile.following_count), inline=False)
        embed.add_field(name="Posts", value=str(profile.media_count), inline=False)
        embed.set_thumbnail(url=profile.profile_pic_url)
        embed.set_footer(text="VBOT SERVICES")

        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", color=discord.Color.from_str("#8B0000"))
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.set_footer(text="VBOT SERVICES")
        await ctx.send(embed=embed)

# Helper functions to handle data files
def load_following_data():
    if os.path.exists(FOLLOWING_DATA_FILE) and os.path.getsize(FOLLOWING_DATA_FILE) > 0:
        try:
            with open(FOLLOWING_DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding following data: {e}")
            return {}
    return {}

def save_following_data(data):
    try:
        with open(FOLLOWING_DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving following data: {e}")

# Replace with your Discord bot token
bot.run('MTI3Mjk2NDgzODAyODQ4MDU3Mw.GqT7em.vxoOTUuksUgvYO9SSzG8egG7DlvUyujQ0COrbM')
