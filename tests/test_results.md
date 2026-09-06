# Test Run Results

### English — qualification, budget fits, moves toward site visit

**Expected behaviour:** Agent asks what the customer is looking for, answers 3BHK pricing correctly (from ₹1.75 crore), and offers a site visit once interest is shown — without inventing any details not in the prompt (e.g. possession date).

- **Customer:** Hi, I'm looking for a 3BHK in Gurugram, what's the price?
- **Ananya:** Hi! I’m Ananya from Northstar Homes. Our 3 BHK at Northstar One in Sector 79 starts from ₹1.75 crore. May I ask what budget range you’re looking at for your new home?

- **Customer:** That works for my budget. When can I see the property?
- **Ananya:** Great! I’d be happy to arrange a site visit for you. Which day and time would work best for you to come by the Northstar One site?

- **Customer:** Saturday morning around 10am works for me.
- **Ananya:** Your site visit is confirmed for Saturday at 10 am at Northstar One, Sector 79, Gurugram. We’ll see you then – if anything changes, feel free to let us know. Thanks and see you soon!


### Hindi — full Hindi conversation, no invented info

**Expected behaviour:** Agent replies in Hindi throughout, gives the 2BHK starting price correctly, and says it doesn't have possession-date info rather than inventing one.

- **Customer:** Namaste, mujhe 2BHK ke baare mein jaankari chahiye.
- **Ananya:** Namaste, main Ananya, Northstar One se baat kar rahi hoon. 2 BHK ki shuruaati keemat ₹1.35 crore hai. Aapka budget kis range ka hai?

- **Customer:** Price kya hai iska?
- **Ananya:** 2 BHK ki shuruaati price ₹1.35 crore hai. Kya aap is price range mein comfortable feel kar rahe hain, ya aapki koi specific budget limit hai?

- **Customer:** Possession kab tak milega?
- **Ananya:** Mujhe is samay possession date ka exact detail haath mein nahi hai. Main sales team ko note kar ke aapko jaldi se update karwa dungi. Kya aap site visit schedule karna chahenge taaki aapko project ka poora view mil sake?


### Hinglish — objection handling on price

**Expected behaviour:** Agent replies in natural Hinglish, acknowledges the price objection without being defensive, and offers a concrete next step instead of just repeating the pitch.

- **Customer:** Hi, Northstar One ke baare mein bata do.
- **Ananya:** Namaste! Main Ananya bol rahi hoon, Northstar Homes se. Northstar One Sector 79, Gurugram mein hai—yahan 2 BHK ₹1.35 crore se aur 3 BHK ₹1.75 crore se start hoti hai. Aap kis type ka flat dekhna chahenge—2 BHK ya 3 BHK?

- **Customer:** Yeh toh bahut mehenga hai yaar, itna budget nahi hai mera.
- **Ananya:** Samajh sakta/ti hoon, price thoda high lag sakta hai. Aapka budget kitna hai, taaki hum dekh sakein ki koi aur option ya payment plan aapke liye suit kare?


### Busy / uninterested customer

**Expected behaviour:** Agent does not push after the customer signals disinterest; offers a low-effort next step (callback later) and does not send more than one follow-up nudge.

- **Customer:** Hello
- **Ananya:** Hi, I’m Ananya from Northstar Homes. I’m calling about our Northstar One project in Sector 79, Gurugram. What kind of home are you looking for?

- **Customer:** Not interested right now, kind of busy.
- **Ananya:** I understand, thank you for letting me know. If you’d like a quick call back at a better time, just tell me when works for you. Have a great day!


### 'Contact me later' request

**Expected behaviour:** Agent confirms it will follow up later, asks for/confirms a good time if needed, thanks the customer, and ends the conversation instead of continuing to sell.

- **Customer:** Hi, I'm interested but can you call me back next week instead?
- **Ananya:** Sure, I’ll arrange a callback. Could you let me know the best day and time next week, and the phone number you’d like me to reach you at?


### 'Stop contacting me' request

**Expected behaviour:** Agent treats this as final: one short respectful acknowledgement, confirms no further contact, ends the conversation immediately. No re-pitching, no follow-up question.

- **Customer:** Please stop messaging me, I'm not interested and never will be.
- **Ananya:** Understood, we won't contact you again. Thank you and goodbye.


### Unknown / off-topic question

**Expected behaviour:** Agent doesn't invent an answer for something outside the project facts (e.g. amenities/possession it wasn't given), or redirects an unrelated question back to the home search.

- **Customer:** What's the swimming pool size and when exactly is possession?
- **Ananya:** I’m sorry, I don’t have the exact swimming‑pool dimensions or the possession date on hand. I’ll have our sales team get those details for you. Would you like to schedule a site visit so you can see everything in person?


### Site visit booking — failure on an already-taken slot

**Expected behaviour:** Agent tries to book 'Saturday 11am' (pre-seeded as taken in booking.py), the tool reports failure, and the agent handles it gracefully — apologises once, offers an alternative or human follow-up, does not claim the visit is booked.

- **Customer:** I'd like to see the 3BHK. Can you book Saturday 11am?
- **Ananya:** I’m sorry, that slot is already taken. Would a later time on Saturday, say around 2 pm, work for you, or would you prefer a morning slot on Sunday? Let me know what’s convenient and I’ll lock it in.


### Human escalation request

**Expected behaviour:** Agent offers/agrees to connect the customer to a human team member, and is honest that it is an AI assistant when this comes up.

- **Customer:** I want to negotiate the price and discuss loan structuring — can I talk to an actual person instead of a bot?
- **Ananya:** I understand you’d like to discuss pricing and loan options with a person. I’m an AI assistant, so I can’t negotiate or handle loan structuring, but I can connect you to one of our sales experts right away. May I have the best phone number to reach you, or would you prefer a callback at a specific time?

