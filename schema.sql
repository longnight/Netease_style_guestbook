SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+08:00";

CREATE TABLE IF NOT EXISTS `netease_style_guestbook` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author` varchar(65) DEFAULT NULL,
  `quote_who` int(11) DEFAULT NULL,
  `comment` longtext NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=17 ;


INSERT INTO `netease_style_guestbook` (`id`, `author`, `quote_who`, `comment`, `created_time`) VALUES
(1, 'someone', NULL, 'this is first comment.', '2014-09-19 11:23:15');

