---
date: 2026-11-25
title: "Belgium's budget gap grows, Anthropic's Claude Ship, and Europe's thin gas cushion"
summary: "Anthropic lets Claude approve code under a team's own rules, Nvidia reinstates Jensen Huang, Belgium's party leaders talk of more than ten billion euros in savings, the EU proposes a twenty-second sanctions package, and cold weather meets Europe's lowest gas stocks in years."
writer: claude
---

## Intro
Good morning Thomas, it's Wednesday the twenty-fifth of November. Here's your Daily Brief. Today: Belgium's party leaders meet for hours, and the budget hole they're talking about gets bigger, not smaller. Anthropic launches Claude Ship, which lets AI approve code under rules a team writes itself. And Europe's gas price jumps as the cold meets unusually empty storage.

## AI
We start with AI, and with a launch that moves the AI from writing code to signing it off.

On Monday, Anthropic launched Claude Ship. According to SiliconANGLE and the Apple news site 9to5Mac, it's a set of three AI agents that take a pull request all the way from review to approval. A pull request, if you haven't met the term, is a proposed change to a codebase that a team checks before it goes live.

The first agent, Code Review, already existed and is generally available. It reads the change and flags problems. The second is new and called PR Steward. When automated tests fail, when two changes clash, or when the reviewer leaves comments, PR Steward fixes them. After every fix, it writes a note explaining what it changed and how to undo it. The third part is the interesting one: Claude Approvals. A team writes its approval policy in plain English, in a file that sits in the code repository. Claude then approves only the changes that policy allows. According to SiliconANGLE, that policy can also draw on the findings of the review agent, and on a company's own automated checks. Everything else still goes to a person.

SiliconANGLE says Claude Ship is for Claude Team and Enterprise customers and works with GitHub. The new parts are in beta. Developers can try it on their own changes with a command called slash ship in Claude Code. Anthropic's own advice is cautious. It suggests running Claude Approvals in an observe-only mode first, starting with a single repository, and setting a monthly spending limit. In its blog post, quoted by SiliconANGLE, Anthropic notes that most teams want a person to approve every change, and that this is easy only when people write every line. That's the problem it's trying to solve: AI now writes so much code that human review has become the bottleneck.

Next, a reversal at Nvidia. Yesterday we reported that Nvidia's chairman had ruled out taking Jensen Huang back as chief executive. That has changed. In a press release filed with the American market regulator, Nvidia says its board voted unanimously on Monday to reinstate Huang as president, chief executive and board member, effective immediately. The board says it took input from senior levels of the United States government, and is confident his return poses no national security risk. Huang's own reaction was short: "I can't wait to get back to work." The investigation by independent directors continues. Nvidia has also set up a new board committee for national security and export controls, and is hiring a chief compliance officer. The Neuron newsletter, citing Bloomberg, reports Nvidia's shares rose about thirty-one per cent on the news. Reuters, also cited by The Neuron, reports that President Trump and Vice-President Vance pushed for his return.

Staying with chips. TechCrunch, as summarised by The Neuron, reports that Amazon has agreed to buy the technology and research team of the start-up Decart, in a deal reported at seven and a half billion dollars. Decart makes software that lets AI models run efficiently on different kinds of chips, so developers don't have to rewrite their models for each one. The Belgian tech site IT Daily reported back in October that talks were under way. For Amazon, the logic is clear. It wants customers to move from Nvidia's chips to its own Trainium chips, and Decart's software lowers the cost of switching.

And one product update from Google. According to TechCrunch, again via The Neuron, AI Mode in Google Search can now connect to your Google Drive and Google Wallet, if you choose to turn that on. Wallet access is read-only. The idea is more personal answers, using your own documents and receipts.

So why does Claude Ship matter for a product manager? Look at where the control sits. Anthropic hasn't asked teams to trust the AI blindly. It's asked them to write down their rules, in plain language, and let the AI apply them, with a human fallback and an undo note on every change. That's a pattern worth copying in any product that automates decisions: make the policy visible and editable, start in observe-only mode, and expand trust step by step.

## Politics
Over to politics, and to Belgium first, where the party leaders talked late into the evening, and the number on the table grew.

On Tuesday afternoon, Prime Minister Bart De Wever met the presidents of the five governing parties, as he had announced after his visit to the King. VRT News followed it live. The meeting was supposed to end at six, but ran well over. There was no agreement.

The most striking detail came from CD&V's president, Sammy Mahdi. He said the leaders will meet again this weekend, and that the exercise is becoming broader and bigger. Asked by VRT whether the government is now looking for around thirteen billion euros rather than ten, he said it was indeed about that kind of amount. Before the meeting, Les Engagés' president, Yvan Verougstraete, had floated an effort of fourteen billion. The extra four billion, he said, could pay for lower taxes on labour and more investment. The MR's president, Georges-Louis Bouchez, wouldn't give a figure. He told RTBF that the government is waiting for updated figures from the Monitoring Committee, the civil service body that tracks the budget, within a few days.

And Vooruit? Its president, Conner Rousseau, said afterwards that his questions had not been answered. He wants guarantees on an extra contribution from millionaires, and he wants to protect the indexation of wages and benefits. He said he would consult his party and hopes to give clarity today. So the shape of the problem has shifted. On Monday, the question was whether Vooruit would accept De Wever's balance between cuts and taxes. Now the other parties are talking about a bigger package overall, which could leave room to give each side something. But a bigger package also means more savings to find, and that is exactly what Vooruit has been resisting. VRT's political reporters say it is too early to say the crisis is over. The deadline De Wever set on Monday still stands: no budget by New Year's Eve, and the government ends.

One piece of good news for the government, reported by VRT. The European Commission says Belgium is, for now, still on track under the European Union's deficit procedure, based on the regional budgets and the federal measures already announced. But it warned the deficit would rise without new measures, and it will look again in the spring.

Over to the European Union. On Monday, Commission President Ursula von der Leyen presented a twenty-second package of sanctions against Russia. According to the Kyiv Independent, it targets Russian sport, with a proposed ban on Russian nationals competing for Russia at events in the EU. It also proposes an entry ban on former Russian soldiers, tighter limits on tourist visas, and a ban on European firms helping Russia repair its refineries. For the first time, the Commission wants to use a new tool against a whole country: Kyrgyzstan, which it says lets crypto platforms dodge sanctions. These are proposals. All twenty-seven member states must agree before any of it takes effect.

Money is the other big EU story. Euronews describes a showdown over the next seven-year EU budget. António Costa, the President of the European Council, has tabled a proposal with another round of cuts. According to Euronews, Germany calls it a step in the right direction but not enough, while France calls it unacceptable. The European Parliament, which has a veto, opposes the cuts. EU leaders are due to discuss it next week. And today in Strasbourg, as we mentioned yesterday, members of Parliament debate how to finance Ukraine.

To the world. In Ukraine, President Volodymyr Zelensky said on Tuesday that the American envoys Jared Kushner and Steve Witkoff want a peace deal as soon as possible, ideally before January. European Pravda reports he said Ukraine wants peace, but not at Ukraine's expense alone. If no acceptable deal comes, he said, Ukraine will ask the new American Congress, which starts in January, for more weapons and tougher sanctions. The Ukrainian news site h.ua adds that a delivery of forty-eight Patriot air-defence missiles is held up, waiting for approval from the American Defence Secretary, Pete Hegseth.

And Spain votes on Sunday in an early general election. Polls disagree. The state pollster, the CIS, predicted earlier this month that Pedro Sánchez's Socialists would come first, with the conservative People's Party and the far-right Vox just short of a majority. The Catalan paper Ara notes that most other polls give those two right-wing parties a better chance of winning a majority together.

## Energy
Over to energy, and to a story that hits Belgian homes directly: the price of gas.

According to the financial site The Private Banker, drawing on Bloomberg, the main European gas contract, the Dutch TTF, jumped by as much as eight point six per cent on Monday, to about ninety-six euros per megawatt-hour. It gave back part of that during the day, but the direction is clear. A year ago, the same contract traded at around thirty euros. Now it's roughly three times that.

Two things are colliding. First, the cold. Forecasters expect freezing temperatures in Britain, Germany and France this week, and a longer cold spell in central and eastern Europe into early December. Second, storage. The Private Banker says the EU's gas stores were about sixty-nine per cent full at the weekend, against roughly eighty-two per cent a year ago. Germany, Europe's biggest gas user, is at about fifty-seven per cent. The underlying cause, it says, is the loss of liquefied gas from the Middle East, after QatarEnergy declared force majeure. That's a legal notice that a supplier can't deliver because of events beyond its control. Many traders also held back from buying during the summer, hoping prices would fall, so Europe entered winter with less in the tank.

And there's a date coming. The EU's ban on Russian gas imports takes effect in January. The Private Banker notes that importers have taken almost all the liquefied gas from Russia's Yamal plant this year, paying about eight point seven billion euros for it.

What does this mean for you in Belgium? Gas plants usually set the price of electricity when wind and sun fall short. Selectra reported last week that during a calm, grey spell earlier this month, Belgian power averaged about three hundred and twenty euros per megawatt-hour for three days, the highest since twenty twenty-two. If you're on a dynamic contract, you feel that immediately. On a variable contract, it shows up later, through your monthly or quarterly price. On a fixed contract, nothing changes until you renew.

Now, a start-up story with a Belgian angle. Tech Funding News reports that Good Heat, a young company based in Amsterdam, has raised two million euros. The Dutch fund SET Ventures led the round, with Shell Ventures joining. Good Heat wants to replace gas boilers in factories with heat batteries, which store cheap electricity as heat and release it as steam. The twist is the business model. Good Heat builds, finances, owns and runs the battery on the factory site. The customer simply buys the heat, on contracts of ten to twenty years. Six European projects are under exclusive negotiation, two of them in Belgium, and the Dutch and Belgian ones are the furthest along. As SET Ventures' managing partner, Anton Arts, puts it, industrial heat isn't held back by technology, but by the difficulty of delivering and financing projects.

And a countdown to keep in mind. The Belgian state and Engie still aim to agree the main terms of the state's takeover of Engie's seven Belgian reactors by the twelfth of December. According to World Nuclear News, the two sides said significant differences remain, especially on the price. That's seventeen days away, and the government doing the deal is fighting for its own survival.

## Term of the day
Today's term is policy as code. It means writing your rules down in a file that a computer can read and apply on its own, instead of keeping them in people's heads or in a document nobody opens.

Think of a company expense policy. Normally a manager reads each claim and decides. With policy as code, the rule says: meals under fifty euros, with a receipt, are approved automatically. Anything else goes to the manager. The rule is written once, everyone can read it, and every decision follows it the same way.

It came up today with Anthropic's Claude Ship. Teams write their approval policy in plain English, in a file next to their code, and Claude applies it. The difference from the classic version is that the rules no longer need to be written in a programming language.

## Outro
That's your Daily Brief for Wednesday. Watch for Vooruit's answer today, the Monitoring Committee's new figures, and the party leaders' meeting this weekend. Keep warm, and keep an eye on those hourly prices. Talk to you tomorrow.
