MERGE `mocked_data.profile_component` AS target
USING `tmp.mock_model_output` AS source
    ON target.profileId = source.profileId
WHEN MATCHED THEN
    -- We cannot update one value in struct in BigQuery,
    -- so we need to replace the entire struct
    UPDATE SET
        behavioral = STRUCT(
            STRUCT(
                target.behavioral.commercial.firstPurchaseUtc
                , target.behavioral.commercial.lastPurchaseUtc
                , target.behavioral.commercial.orderAverageValue
                , target.behavioral.commercial.orderCount
                , target.behavioral.commercial.orderMedianValue
                , target.behavioral.commercial.orderTotalValue
            )
                AS commercial
                -- This is where the ltv_score is inserted
            , source.ltv_score AS customerLifetimeValue
            , target.behavioral.firstSeen
            , target.behavioral.lastSeen
            , target.behavioral.sessionAverageTimeInSeconds
            , target.behavioral.sessionCount
            , target.behavioral.subscriptionCountDoubleOptIn
            , target.behavioral.subscriptionCountSingleOptIn
            , target.behavioral.totalTimeSpentOnSiteInMilliseconds
            , target.behavioral.unsubscribeAll
            , target.behavioral.unsubscribeCount
        );
MERGE `avaus-academy.mocked_data.profile_component` AS target
USING `avaus-academy.tmp.mock_model_output` AS source
    ON target.profileId = source.profileId
WHEN MATCHED THEN
    -- We cannot update one value in struct in BigQuery,
    -- so we need to replace the entire struct
    UPDATE SET
        behavioral = STRUCT(
            STRUCT(
                target.behavioral.commercial.firstPurchaseUtc
                , target.behavioral.commercial.lastPurchaseUtc
                , target.behavioral.commercial.orderAverageValue
                , target.behavioral.commercial.orderCount
                , target.behavioral.commercial.orderMedianValue
                , target.behavioral.commercial.orderTotalValue
            )
                AS commercial
                -- This is where the ltv_score is inserted
            , source.ltv_score AS customerLifetimeValue
            , target.behavioral.firstSeen
            , target.behavioral.lastSeen
            , target.behavioral.sessionAverageTimeInSeconds
            , target.behavioral.sessionCount
            , target.behavioral.subscriptionCountDoubleOptIn
            , target.behavioral.subscriptionCountSingleOptIn
            , target.behavioral.totalTimeSpentOnSiteInMilliseconds
            , target.behavioral.unsubscribeAll
            , target.behavioral.unsubscribeCount
        )
