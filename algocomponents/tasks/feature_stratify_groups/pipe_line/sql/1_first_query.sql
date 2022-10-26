-- This sql file is not generalized and is adjusted for GCP!
DROP TABLE IF EXISTS tmp.Stratified_groups;
CREATE TABLE tmp.Stratified_groups AS
    (SELECT * FROM tmp.Customer ORDER BY `SupportRepId` DESC);
ALTER TABLE tmp.Stratified_groups ADD COLUMN `SGroups` INT;

-- This part of code works on GCP console but not here!
-- It did not work with or without ; after queries outside while loop
BEGIN
    DECLARE nbr INT64 DEFAULT 0
    DECLARE LoopCounter INT64 DEFAULT 1
    SET nbr = (SELECT COUNT(*) FROM tmp.Stratified_groups)

    -- Hitting the database with many requests equals to the number of  records in the table
    -- is not efficient. The solution here is proposed should be solved, if possible.
    WHILE LoopCounter <= nbr
        DO
            UPDATE tmp.Stratified_groups
                        SET SGroups = (MOD(LoopCounter, 3) + 1)
                        WHERE CUstomerID = LoopCounter
            SET LoopCounter = LoopCounter + 1
    END WHILE
END;

-- TEST
SELECT CUstomerID, SGroups FROM `tmp.Stratified_groups` 
            ORDER BY CUstomerID LIMIT 5;
SELECT COUNT(SGroups) FROM `tmp.Stratified_groups` GROUP BY SGroups;