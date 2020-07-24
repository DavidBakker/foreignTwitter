USE `twitterwords`;
DROP procedure IF EXISTS `Consolidate_Words`;

DELIMITER $$
USE `twitterwords`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `Consolidate_Words`()
BEGIN

WITH indexedWords AS(
	SELECT *
	, row_number() OVER (partition by word, language, country, translation) as wordIndex
	FROM words
),
summedWords AS (
	SELECT word
	, sum(wordcount) as summedCount
	, language
	, country
	, translation
	FROM words
	GROUP BY word, language, country, translation
),
finalWords AS (
	SELECT 
	iw.*
	, sw.summedCount
	FROM indexedWords iw
	JOIN summedWords sw on sw.word = iw.word
		AND sw.language = iw.language
		AND sw.country = iw.country
		AND sw.translation = iw.translation
)

UPDATE words, finalwords
SET 
	words.rank = finalwords.wordIndex,
	words.wordcount = finalwords.summedCount
WHERE words.idwords = finalwords.idwords;

DELETE FROM words WHERE words.rank > 1;

END$$

DELIMITER ;

