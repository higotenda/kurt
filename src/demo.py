import impl.discp as discp

if __name__ == "__main__":
    client = discp.make_client()
    client.run(discp.DISCORD_BOT_TOKEN)
