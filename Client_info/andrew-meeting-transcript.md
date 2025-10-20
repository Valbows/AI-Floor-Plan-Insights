# Client Meeting Transcript - Andrew
**Date:** January 2025
**Attendees:** Val, Ariel, Robert, Lee, Andrew, Timothy
**Meeting Type:** Product Demo & Requirements Gathering

---

## Full Transcript

**Valery Rene (09:16):** Good morning, Andrew. Pleasure to meet you. My name is Val.

**Andrew (09:19):** We.

**Valery Rene (09:20):** We are. I'm with my teammate Ariel, Robert and Lee. We built the AI floor planning and market insights. And the pathway that we wanted to take was working with a listing agent. And the listing agent Persona will be Jessica Wong. Jessica just found a property that somebody wants to sell and she's grabbing that floor plan and she's going to pass it over to the listing coordinator, Chris Parker. And Chris Parker is going to use our platform in order to do floor plan analysis and get marketing insights quickly. And I'm going to kick this off by showing you the platform. Please feel free to jump in if you have any questions. But I'm just going to work walk through a basic workflow. So this is the platform that we created. It'll be able to log all of the properties that you created. But we'll start off with the search. You'll be able to upload a floor.

**Andrew (10:18):** Plan.

**Valery Rene (10:26):** And everybody can see my screen, right? Just double check.

**Timothy Asprec (10:29):** Yes, you're good to go.

**Valery Rene (10:32):** And then you'll be able to add the address and from there. This is not going to be like the movie gone in 60 seconds. This is going to be built in 60 seconds where our AI is going to do most of the heavy lifting. What we're doing is we're extracting the information from the floor plan, square footage, rooms, bathrooms, doors, windows. We're also using that address and we're going to go and find all the relevant market insights. This is also malleable. So the ones that we took was just to show that the pipeline is created, we can focus that on whatever is most important for you. But for now, we're just taking a couple analysis of the neighborhood pricing. So what is the relevant pricing per square footage in that neighborhood based on the address? And we're going to compare that to the square footage that was calculated by our AI and we're going to be producing that information. We'll also be able to have a couple other pretty cool pieces of information that we'll be able to show you as well. This was just based on some of the research that we did to kind of help you with that pipeline. You said that you also are part of the marketing team, so I think you'll be excited to see that some of the stuff that we were able to calculate will also help you in that space. And while our AI magic is taking place, I'll take another second here and we'll be ready to go. The other thing is I wanted to focus on is also letting you know the ability for this platform to be able to be edited as well as the final portion of that is that we can take that link that is edited and we'll be able to pass that link on to the final end user.

**Andrew (12:40):** One question while this goes. Is there any functionality to be able.

**Andrew (12:46):** To pull floor plans directly from a website as opposed to uploading them?

**Valery Rene (12:54):** Yes, that definitely is a possibility. There's a couple different ways that we could do that. Either through something like an MLS integration or we can even set up a system where we can pull it from platforms like Zillow and Redfin.

**Andrew (13:08):** Okay, yeah, that would be, that would be great.

**Valery Rene (13:17):** It's taking a little bit longer than I would like, but I'm going to jump right into. I'm sorry, I didn't mean to cut you off, but I don't know.

**Andrew (13:23):** Good.

**Valery Rene (13:26):** Sorry, what was the, the last part you were saying, Andrew?

**Andrew (13:31):** Yeah, it's great that I can pull it and then. Sorry, I lost my second question, but.

**Andrew (13:37):** I'll let you guys kind of go back to walking, walking this through.

**Valery Rene (13:42):** Yeah, I'm just gonna show you what the created platform would look like. So once that that information is processed, this will be with the floor plan. This will be the extracted information. On this right hand side here. You'll be able to see a lot of the market insights. You'll be able to see trend analysis, investment analysis, the investment analysis. Right now we're pulling that information from CoreLogic, but we have some fallbacks as well. So we can go and confirm that information with Zillow and Redfin. This is the marketing content. This can also be used as neighborhood analysis for parks in the area, schools, trains close to the property. Some key insights and this is some of the, you know, the start of the social media content that can be created, all done for the user so that everything is catered to that particular listing as well as SEO keywords. But if you don't like anything you see, we can also edit any of that information on the fly and it'll be saved as well. And then the last part is after you send that link over, this will be the link that you can send over to the end user. And after you send that link, you can actually see if the person that's interested in purchasing that property actually opened it up. How, how interested are, are they in the property? And that is essentially the platform. You'll be able to have a record of all the properties that you created. You'll be able to search them just in case there's something that you remember the address but don't remember the place. And you can always jump back in and get that information.

**Andrew (15:33):** Awesome.

**Andrew (15:33):** Yeah, I mean, I like the idea of like being able to integrate it with like, you know, mls, I guess.

**Andrew (15:38):** In New York it's with Remny, so it's a little bit difference the rs.

**Andrew (15:42):** But same idea and definitely doable.

**Valery Rene (15:47):** Because.

**Andrew (15:47):** The ability to pull those floor plans, opposed to, you know, uploading one by.

**Andrew (15:52):** One is more, I think valuable, especially at scale, depending on how we're using it.

**Andrew (15:58):** Is there any ability to kind of like look at like actual like full like sort of the room dimensions as opposed to like just high level, like bedrooms and bathrooms? Is it able to like pull like the actual dimensions of each space and kind of put that into, you know, some sort of like either spreadsheet or database?

**Valery Rene (16:22):** Yes. So we can actually break this down by room. So if, if the information is available, we can break that down by room. So you can know exactly what square footage the bedroom is, the bathroom and we could go room by room. And we can also have that as just a breakdown here on the side.

**Andrew (16:42):** Yeah, I mean it's more for like internal uses. Like we study like basically one of the use cases that I was imagining here is if we could analyze, you know, let's say a group of floor plans in a comp set. If we're designing and building a project, let's say real world example is we're building goannas right now, we could then look at, you know, all the floor plans of everything available in Goannis and actually see you know, what the dimensions are of each room and even take it one step further, potentially correlate it.

**Andrew (17:15):** To the rents that they're getting.

**Andrew (17:17):** So, like, we could say, okay, like we know that a floor plan with, you know, X dimensions is more highly correlated to a higher per foot number than, you know, let's say a floor.

**Andrew (17:28):** Plan with, you know, X characteristics.

**Andrew (17:31):** So, like, it's not an exact science. Just because real estate is kind of funky in terms of like sort of all the proxies that are there. But with a large enough sample size, I do think we could actually extrapolate some interesting data where we could actually see, you know, what size units are performing better on a per foot basis. Or, you know, there's just a lot of things that we can glean from them. And so that's something that is. This is sort of like, you know, I see kind of what you guys did and it's, you know, really, you know, I'm impressed and kind of how much progress kind of what you guys have built in a short amount of time. This is a little more front facing in some ways. So I think something that could be really interesting is looking at sort of that more sort of internal analysis for us to help inform kind of what.

**Andrew (18:19):** Units we are designing and ultimately building.

**Valery Rene (18:24):** Do you envision something like a forecasting system? So we create that analysis for you and then we compare it to what's happening in the marketplace. Like, three bedrooms are hot in this area. This is the going square footage. And would you like that type of information to be pulled in while you're making your forecasting analysis?

**Andrew (18:45):** Yeah, I mean, I think it gets very granular.

**Andrew (18:49):** That's why I like the idea of like pulling, you know, what you're showing here shows like the square footage of each room, but typically in a New York floor plan, if you were to pull them, it typically shows dimensions. And so if we were able to like look at the dimensions of each room and then start to run like a bunch of correlations. So let's say we're running, you know, sort of every single dimension. So we're running like a living room width versus like bedroom width against like the dollars per foot that these units are actually renting for. I think you could, you know, again, you know, on a enough sample size, we'd actually get some real insights into like, what types of layouts are most effective in terms of like, what they're.

**Andrew (19:38):** Getting it right, if that makes sense.

**Valery Rene (19:42):** And I, I guess what part of that analysis that you're current, what Part of that workflow is currently taking the most time for your team. So when you're doing it without AI or, or I don't know if you're using any competing services, what does that workflow look like? And what's the biggest pain point? What's the reason why it takes so long?

**Andrew (20:03):** Yeah, and the biggest pain point is you literally have to manually go floor plan by floor plan and then type into a spreadsheet, you know, every single dimension. We actually did, I had someone do this, like an intern, and that was like a big project, but they were literally tracking. We did it for like condo sales.

**Andrew (20:22):** And co op sales.

**Andrew (20:23):** Co ops are harder because you don't get the square footage. So like primarily condos. And we were looking at basically every like condo as to say in all of Brooklyn. They would go through and pull out and put into a spreadsheet like, you know, living room with living room length, bedroom with like all these different data points. And then we looked at, you know, what the sale price was and what really kind of solve for is like how this correlates to price per square foot, because that's kind of the ultimate metric. So we had, you know, the price per square foot number and then we.

**Andrew (20:57):** Basically ran a bunch of like, regression.

**Andrew (21:00):** Analysis and looked at like, how each.

**Andrew (21:02):** Sort of data point correlated to price per square foot.

**Andrew (21:06):** And again, it's not an exact science because there's a lot of like, variables involved. But again, there was, I think, enough there that we actually able to say, like, you know, living rooms with the, you know, length and width of like 17 and like 21, for example, had.

**Andrew (21:23):** The highest correlation to breakfast. Right, but so we're actually able to.

**Andrew (21:27):** Like, get some like, real insight there. And you know, with some caveats.

**Andrew (21:32):** But like, I think it gave us.

**Andrew (21:33):** Enough to say, okay, like, we're looking at this and like, it seems like second bedrooms, like the sizing matter too much. For example, like, and one plausible theory is because, you know, people are using that home offices now and things like that, so like, they're not as concerned. Maybe it's like a, you know, a newborn or like a young child and the size is less important than the.

**Andrew (21:54):** Actual living room size. So if you're like attributing more space.

**Andrew (21:58):** To the living room and shrinking the bedroom, like we were able to kind of actually solve and see, you know, that data, that information from analysis like that. And again, I understand it's a little.

**Andrew (22:10):** Bit different than kind of like what.

**Andrew (22:11):** You'Re showing, but that is, I think one Pain point that takes, you know, it's really like difficult to keep up with. Like you know, when the intern left.

**Andrew (22:22):** Like we kind of like I didn't.

**Andrew (22:24):** Really like bring someone in to, you know, continue to do this. So like something with like AI I.

**Andrew (22:29):** Think could solve that and it'd be.

**Andrew (22:31):** Really interesting because I think that's a big selling point not just for us, but like if we were to pitch our third party brokerage on the developer and we'd say look, like we know your market, like we know exactly what you should be building because we have.

**Andrew (22:43):** All the data, it's pretty compelling.

**Valery Rene (22:47):** So the market insight data that you would most want to focus on is around analyzing that information for investability. Like, like, like how, how, how, how valuable can we make this property on the market? Like would you want that information to be the key focus of the market insights that we pull into the platform?

**Andrew (23:09):** Yeah, I think put another way, like what we're trying to solve for is.

**Andrew (23:13):** Like you know, what layout with specific, like what are the optimal dimensions of each layout and what type of unit relative to the market and what produces.

**Andrew (23:25):** What correlates the highest to price for square foot.

---

## Meeting End

