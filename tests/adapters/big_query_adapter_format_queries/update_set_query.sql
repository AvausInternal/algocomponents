MERGE `mocked_data.profile_component` AS tgt
USING `tmp.mock_model_output` AS src
    ON tgt.profileId = src.profileId
WHEN MATCHED THEN
    -- We cannot update one value in struct in BigQuery,
    -- so we need to replace the entire struct
    UPDATE SET
        behavioral = STRUCT(
            STRUCT(
                tgt.behavioral.commercial.firstPurchaseUtc
                , tgt.behavioral.commercial.lastPurchaseUtc
                , tgt.behavioral.commercial.orderAverageValue
                , tgt.behavioral.commercial.orderCount
                , tgt.behavioral.commercial.orderMedianValue
                , tgt.behavioral.commercial.orderTotalValue
            )
                AS commercial
                -- This is where the ltv_score is inserted
            , src.ltv_score AS customerLifetimeValue
            , tgt.behavioral.firstSeen
            , tgt.behavioral.lastSeen
            , tgt.behavioral.sessionAverageTimeInSeconds
            , tgt.behavioral.sessionCount
            , tgt.behavioral.subscriptionCountDoubleOptIn
            , tgt.behavioral.subscriptionCountSingleOptIn
            , tgt.behavioral.totalTimeSpentOnSiteInMilliseconds
            , tgt.behavioral.unsubscribeAll
            , tgt.behavioral.unsubscribeCount
        );
MERGE `avaus-academy.mocked_data.profile_component` AS tgt
USING `avaus-academy.tmp.mock_model_output` AS src
    ON tgt.profileId = src.profileId
WHEN MATCHED THEN
    -- We cannot update one value in struct in BigQuery,
    -- so we need to replace the entire struct
    UPDATE SET
        behavioral = STRUCT(
            STRUCT(
                tgt.behavioral.commercial.firstPurchaseUtc
                , tgt.behavioral.commercial.lastPurchaseUtc
                , tgt.behavioral.commercial.orderAverageValue
                , tgt.behavioral.commercial.orderCount
                , tgt.behavioral.commercial.orderMedianValue
                , tgt.behavioral.commercial.orderTotalValue
            )
                AS commercial
                -- This is where the ltv_score is inserted
            , src.ltv_score AS customerLifetimeValue
            , tgt.behavioral.firstSeen
            , tgt.behavioral.lastSeen
            , tgt.behavioral.sessionAverageTimeInSeconds
            , tgt.behavioral.sessionCount
            , tgt.behavioral.subscriptionCountDoubleOptIn
            , tgt.behavioral.subscriptionCountSingleOptIn
            , tgt.behavioral.totalTimeSpentOnSiteInMilliseconds
            , tgt.behavioral.unsubscribeAll
            , tgt.behavioral.unsubscribeCount
        )
