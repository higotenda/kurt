import impl.discp as discp

if __name__ == "__main__":
	bot, client = discp.make_client();
	client.run(discp.DISCORD_BOT_TOKEN);