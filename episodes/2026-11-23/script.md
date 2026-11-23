---
date: 2026-11-23
title: "De Wever back at the palace, COP31 collapses, and OpenAI makes idle voice agents cheaper"
summary: "OpenAI's GPT-Live-1.1 and its cheaper standby mode, AWS lets AI agents buy software, De Wever reports to the King again without a budget, Fitch holds Belgium at A plus, COP31 ends without a deal, and Groen opens the door to nuclear power."
writer: claude
---

## Intro
Good morning Thomas, it's Monday the twenty-third of November. Today: Bart De Wever goes back to the King this morning, still without a budget. The climate summit in Antalya ends with no deal at all, the first such failure since Copenhagen. And OpenAI puts a new voice model in its API, with a pricing trick that matters for anyone building voice products.

## AI
We start with AI, and with a launch that is really about the cost of silence.

On Friday, OpenAI announced on its developer forum that GPT-Live-1.1 is now available in its API. GPT-Live is OpenAI's real-time voice model, the one you talk to rather than type to. Version one point one has been the voice of ChatGPT for paying subscribers since the middle of October. Now developers can build their own voice agents on it. OpenAI says the new version has more natural and consistent accents across languages, handles letters and numbers better, follows instructions more closely, and completes tasks more reliably.

The more interesting part is a new setting called standby. Here is the problem it solves. A voice agent on a phone line or in an app usually spends most of the call waiting. The customer is looking for their account number, or thinking, or talking to someone else in the room. Until now, you paid the full rate for every minute the line was open, whether anyone was talking or not. With standby, the developer sets an idle timeout of between five and sixty seconds. After that much silence, the model pauses, while the connection stays open, and it wakes up again as soon as someone speaks.

The prices, according to OpenAI: five American cents a minute when the model is active, and two cents a minute in standby. The reasoning and tool calls behind the voice, which are handled by a separate model, are billed on top.

The technology site i-SCOOP worked through an example. Take an hour-long session in which people actually talk for twelve minutes, with a ten-second timeout. The voice layer would cost about one dollar sixty, against three dollars without standby. It also points out some limits. The documentation only mentions standby for browser-style connections, not for phone lines connected through other routes, so developers shouldn't assume it works everywhere. And because standby still costs forty per cent of the active rate, it can never cut the voice bill by more than sixty per cent. For European builders, i-SCOOP notes that OpenAI offers data storage and processing inside Europe for live sessions, but its table names the older model, so teams should check it applies to version one point one.

Staying with agents, but this time agents that spend money. Last Thursday, Amazon Web Services announced on its marketplace blog that AI agents can now find and buy certain products on AWS Marketplace by themselves. The purchases go through a payment service called AgentCore payments, and land on the customer's normal AWS bill. The safeguards are the point. Before an agent can buy anything, a person sets a spending limit for that task. Companies can restrict agents to an approved list of sellers. And every transaction is logged for audit. In AWS's own technical example, a research agent gets a budget of five cents and a cap of two cents per request. For larger purchases made through AWS's shopping assistant, AWS says a human still has to confirm before the purchase is complete. In an interview with the analyst firm Constellation Research, the AWS vice-president Matt Yanchyshyn said buyers using that assistant convert at six to seven per cent. That's AWS's own figure, with no method published.

And briefly, Google DeepMind has opened Genie 4 to subscribers of its top AI Ultra plan. Genie is a world model: you describe a scene and it generates a world you can walk around in, live. According to Google's blog, you can now change the weather, the characters or the action mid-session with a text prompt, and for the first time the world comes with sound that adapts to the scene. Decrypt notes that Google itself warns objects can drift between views and complex physics is still hard. Subscribers on the cheaper Pro plan can join a waitlist.

So why does GPT-Live-1.1 matter for a product manager? Because it shows that the business model of a voice feature depends on the shape of real conversations, not just the price per minute. If you're planning a voice product, measure how much of a typical session is silence, because that number now decides a big part of your margin.

## Politics
Over to politics, and to Belgium first, where the Prime Minister is due back at the palace this morning.

According to VRT News, the core cabinet, the Prime Minister and his deputy prime ministers, meets at half past nine, with Vooruit at the table. At half past eleven, Bart De Wever reports to King Philippe. It's his fourth visit to the palace this month. A week ago, the King refused to let the talks end there and asked De Wever to keep negotiating, to avoid what the palace called a damaging political and budgetary crisis. He set today as the next check-in.

Has anything moved? A little. VRT reports that De Wever and Vooruit's chairman Conner Rousseau met on Friday evening for about three hours. What they discussed has not been made public, and VRT says it is unclear whether trust has been restored. All parties say they want to keep talking, and none is openly pushing for the government to fall.

The main sticking point is still what VRT calls the strongest shoulders, the wealthiest Belgians. Vooruit wants a substantial contribution from millionaires. According to VRT, De Wever proposed lowering the threshold of the tax on securities accounts from one million euros to seven hundred and fifty thousand. Vooruit had not accepted that. The other three partners, the MR, Les Engagés and CD&V, accepted De Wever's framework more than a week ago.

De Wever also set out the bigger picture at an N-VA members' day in Antwerp. As VRT reports it, he said the roughly ten billion euros being negotiated now will not be enough, and that around twenty billion more must be found in the years ahead. In his words, "we have only filled a third of the hole."

In the meantime, the government is preparing for the possibility that no budget is ready in time. On Friday it approved the first batch of provisional twelfths for January to March next year. That's an emergency rule that lets the state keep spending, month by month, roughly in line with the previous year's budget. The Budget Minister, Vincent Van Peteghem, now has to file it in the Chamber.

Staying with Belgium, markets gave the government some breathing room. Late on Friday, the rating agency Fitch kept Belgium's credit rating at A plus, with a stable outlook. According to The Brussels Times, Fitch said prolonged and complex political talks are not unusual in Belgium, and it expects a deal in the end, as happened last year. But it also warned that debt is very high and rising, among the highest of countries with this rating. It sees a risk of an interest snowball from twenty thirty, where rising interest costs feed further debt. De Wever called Fitch's message a clear warning if the reform drive stalls. Moody's and S and P reached broadly the same view last month.

Over to the European Union, where the European Commission has confirmed that it was hit by a cyberattack carried out with the help of AI tools. According to Reuters, the Commission's spokesperson Thomas Regnier said it was "an AI-generated cybercampaign". The attack was first detected on the twenty-second of October. Several internal systems, including those for payslips, leave and medical reimbursements, were taken offline as a precaution, and most have since been restored. Regnier said there was no evidence of a breach affecting Commission staff as a whole, and no ransom demand. He would not say who was behind it. Politico reported that the EU's own cyber-security team found the attackers had used a publicly available AI tool for finding weaknesses. The Dutch liberal member of the European Parliament, Bart Groothuis, criticised the Commission for keeping information internal. The investigation is continuing.

And finally, Ukraine. On Saturday, a Russian missile strike hit Kryvyi Rih, President Zelensky's home city. According to the local American broadcaster Local Ten, citing Ukrainian authorities, two people were killed and at least sixty injured. It came just days after the meetings in Shenzhen and Berlin that we covered on Friday, where no date was set for new talks with Russia.

## Energy
Over to energy, and to Belgium first, where one of the country's most anti-nuclear parties has changed its mind.

On Saturday, at a members' congress in Antwerp, Groen, the Flemish Greens, voted to accept nuclear power as a possible transition technology on the way to a fully renewable energy supply. According to VRT News, three hundred and ninety-four of the five hundred and sixty-six members present voted in favour, which is seventy per cent. The party's goal is still one hundred per cent renewable energy, and nuclear would only play a role under certain conditions. The new chairman, Aimen Horch, called it part of the party's renewal, and said "this is only the beginning."

That's a big shift for a party born in the environmental movement, which made the nuclear phase-out one of its main causes for years. Not everyone was pleased. Before the vote, Greenpeace Belgium urged members to vote the proposal down. Its spokesperson Joeri Thijs argued that keeping old reactors open is risky, slow and expensive, and that renewables remain the fastest and cheapest route.

The timing matters, because the federal government and Engie are still negotiating over the state taking over Engie's Belgian reactors. Both sides set themselves a new target date of the twelfth of December to agree the main terms. Groen is in opposition federally, so the vote doesn't change that deal. But it removes one of the loudest voices against nuclear power in Flemish politics.

Over to the climate summit, which ended in failure. On Sunday afternoon, about forty-four hours after the official close, COP31 in Antalya broke up without a main agreement. According to ABC News in Australia, it was the longest UN climate summit ever, and the first time since Copenhagen in two thousand and nine that the talks failed to adopt a deal by consensus.

The dispute was about fossil fuels. As we reported on Friday, the final drafts by the co-hosts, Australia and Türkiye, no longer mentioned them at all. Russia and Saudi Arabia supported leaving them out. The European Union refused. Speaking for the EU, the Irish climate minister Darragh O'Brien said the talks had been "hijacked by some oil states", according to ABC. UN News reports that the EU called a text without fossil fuels unconscionable. Panama and the Marshall Islands also rejected it. The Australian minister Chris Bowen, who led the talks, said the outcome was very disappointing, and that a transition away from fossil fuels simply did not have the support of the parties. The UN Secretary-General, António Guterres, called it deeply disappointing.

Not everything was lost. According to Down To Earth, several separate decisions were adopted, including one on a just transition, meaning support for workers and communities who depend on fossil fuels. A road map on finance to help countries adapt to climate impacts will report back next year. The next summit, COP32, is in Addis Ababa, in Ethiopia. And ABC notes that commitments from earlier summits still stand.

And finally, gas, which explains a lot about Europe's energy bills this winter. According to investingLive, the American bank Goldman Sachs expects the European gas price to roughly halve next year, to around forty-five euros per megawatt-hour on average, from about eighty-five in mid-November. That's a forecast, and it comes with a big warning. If gas exports from the Gulf stay at a quarter or less of their pre-war level and this winter is colder than normal, Goldman says prices could approach one hundred and fifty euros in the first months of next year. With storage low and a cold spell under way, the next few weeks will show which scenario we are in.

## Term of the day
Today's term is full-duplex. It describes a connection where both sides can talk and listen at the same time. A phone call is full-duplex: you can interrupt the other person, and they hear you while they are still speaking. An old walkie-talkie is half-duplex: you press a button to talk, say "over", and only then can the other person reply.

For voice AI, this makes a big difference. A full-duplex model can hear you start to interrupt, stop mid-sentence, and change course, just like a person would. That's what makes a conversation feel natural rather than like taking turns at a microphone.

It came up today because OpenAI's GPT-Live is a full-duplex voice model. Its new standby mode is a way to keep that always-open line without paying full price while nobody speaks.

## Outro
That's your Daily Brief for Monday. Tomorrow, we'll look at what came out of De Wever's visit to the palace, and how Europe reacts to the end of COP31. Have a good day, Thomas, and I'll talk to you tomorrow.
