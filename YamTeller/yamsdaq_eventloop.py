import settings

def loop(reddit, session):
    raise ValueError("This feature is not yet implemented. Shutting down!")  # TODO: Remove this when done

    #
    # # TODO: Check sub for new companies. Create models for said companies.
    #
    # # Iterate through existing companies:
    # companies = session.query(Company).all()
    #
    # for company in companies:
    #     post = r.submission(company.submission_id)
    #
    #     # Parse buy and sell requests
    #     data = {'buys': 0, 'sells': 0}
    #     comments = [] # Todo: get all comments here
    #     for comment in comments:
    #         author = comment.author
    #         body = comment.body
    #
    #         command = body.split(' ', 1)[0].upper()
    #
    #         out = None
    #         try:
    #             commandFn = getYAMSDAQParser(command)
    #             out = commandFn(session, company, data, author, body)
    #         except ValueError as e:
    #             out = "An error occurred: %s" % e.message
    #
    #         author.message("Your YamTeller Transaction Result", out)
    #
    #     # Company value
    #     randomFactor = random.uniform(settings.STOCK_EXCHANGE_RANDOM_LOWERBOUND, settings.STOCK_EXCHANGE_RANDOM_UPPERBOUND)
    #     randomFactor = 1.1 ** data['buys']
    #     randomFactor = randomFactor / float(1.1 ** data['sells'])
    #
    #     newValue = controllers.getCompanyCurrentPrice(session, company) * randomFactor
    #     newValuePt = ValuePoint(value=newValue, company_code=company.code)
    #     session.add(newValuePt)
    #     session.commit()
    #
    #     # Purge the value database
    #
    #     # Iterate through the windows. We want the number of data points to roughly equal the same thing throughout
    #     # the different windows.
    #     currentWindowEnd = newValuePt.datetime
    #     currentWindowLength = datetime.timedelta(seconds=settings.VALUEWINDOWS[0])
    #     currentWindowStart = newValuePt - currentWindowLength
    #
    #     targetNPoints = 0 # TODO: Get the data point count in the smallest window
    #
    #     for i in xrange(1, len(settings.VALUEWINDOWS)):
    #         windowLengthInSeconds = settings.VALUEWINDOWS[i]
    #         purgeableWindowLengthInSeconds = windowLengthInSeconds - currentWindowLength.total_seconds()
    #
    #         purgeableWindowEnd = currentWindowStart
    #         purgeableWindowLength = datetime.timedelta(seconds=purgeableWindowLengthInSeconds)
    #         purgeableWindowStart = purgeableWindowEnd - purgeableWindowLength
    #
    #         purgeableWindowPoints = [] # TODO: Get the data points
    #         purgeableWindowNPoints = len(purgeableWindowPoints)
    #
    #         # Math trick: the number of points in the purgeable area should be equal to the number of pts in the same fraction of the smaller area
    #         purgeableWindowAsFractionOfTotalWindow = purgeableWindowLengthInSeconds / float(windowLengthInSeconds)
    #         mergeEvery = int(purgeableWindowNPoints / (targetNPoints * purgeableWindowAsFractionOfTotalWindow))
    #
    #         # Get the largest multiple of mergeEvery items out of the points list
    #         purgeableWindowPoints = purgeableWindowPoints[:(int(purgeableWindowNPoints / mergeEvery) * mergeEvery)]
    #
    #         pointValues = np.array([p.value for p in purgeableWindowPoints])
    #         pointTimes = [p.datetime for p in purgeableWindowPoints]
    #         minPointTime = min(pointTimes)
    #         pointDeltaTimes = np.array([(p - minPointTime).total_seconds() for p in pointTimes])
    #
    #         # Get the arithmetic means
    #         meanValues = list(np.mean(pointValues.reshape(-1, mergeEvery), axis=1))
    #         meanDeltaTimes = list(np.mean(pointDeltaTimes.reshape(-1, mergeEvery), axis=1))
    #         meanTimes = [minPointTime + datetime.timedelta(seconds=s) for s in meanDeltaTimes]
    #         meanValueTimeTuples = zip(meanValues, meanTimes)
    #
    #         # Get rid of the existing value points
    #         for p in purgeableWindowPoints:
    #             session.delete(p)
    #
    #         # Add the new ones
    #         for value, time in meanValueTimeTuples:
    #             vp = ValuePoint(value=value, datetime=time, company_code=company.code)
    #             session.add(vp)
    #
    #     # TODO: Update company page.
    #
    #     # TODO: Update graphs
    #
    # # TODO: Update main listing with Federal Reserve funds and company names / values
