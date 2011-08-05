CREATE TABLE IF NOT EXISTS `drupal_comments` (
  `cid` int(11) NOT NULL auto_increment,
  `pid` int(11) NOT NULL default '0',
  `nid` int(11) NOT NULL default '0',
  `uid` int(11) NOT NULL default '0',
  `subject` varchar(64) NOT NULL default '',
  `comment` longtext NOT NULL,
  `hostname` varchar(128) NOT NULL default '',
  `timestamp` int(11) NOT NULL default '0',
  `status` tinyint(3) unsigned NOT NULL default '0',
  `format` smallint(6) NOT NULL default '0',
  `thread` varchar(255) NOT NULL,
  `name` varchar(60) default NULL,
  `mail` varchar(64) default NULL,
  `homepage` varchar(255) default NULL,
  PRIMARY KEY  (`cid`),
  KEY `pid` (`pid`),
  KEY `nid` (`nid`),
  KEY `status` (`status`)
) ENGINE=MyISAM AUTO_INCREMENT=2367 DEFAULT CHARSET=utf8 AUTO_INCREMENT=2367 ;


INSERT INTO `drupal_comments` VALUES (1, 0, 38, 0, 'Ejemplo 1 de comentario', 'Esto es un ejemplo de comentario.', '127.0.0.1', 1262969466, 0, 2, '01/', '', '', '');
INSERT INTO `drupal_comments` VALUES (2, 0, 38, 1, 'Ejemplo 2 de comentario', 'Esto es otro ejemplo de comentario', '127.0.0.1', 1263028149, 0, 2, '02/', '', '', '');
