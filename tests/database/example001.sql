CREATE TABLE IF NOT EXISTS `drupal_node_revisions` (
  `nid` int(10) unsigned NOT NULL default '0',
  `vid` int(10) unsigned NOT NULL auto_increment,
  `uid` int(11) NOT NULL default '0',
  `title` varchar(255) NOT NULL default '',
  `body` longtext NOT NULL,
  `teaser` longtext NOT NULL,
  `log` longtext NOT NULL,
  `timestamp` int(11) NOT NULL default '0',
  `format` int(11) NOT NULL default '0',
  PRIMARY KEY  (`vid`),
  KEY `nid` (`nid`),
  KEY `uid` (`uid`)
) ENGINE=MyISAM AUTO_INCREMENT=183 DEFAULT CHARSET=utf8 AUTO_INCREMENT=183 ;


INSERT INTO `drupal_node_revisions` VALUES (1, 1, 1, 'Bienvenida', 'Probando...', 'Probando...', '', 1261126931, 2);
INSERT INTO `drupal_node_revisions` VALUES (2, 2, 1, 'Bienvenida2', 'Probando2...', 'Probando2...', '', 1261126931, 2);
INSERT INTO `drupal_node_revisions` VALUES (3, 3, 1, 'Con código', 'Ejemplo con código: \n[code language="python"]\nprint "hello, world"\n[/code] y fin', 'A', '', 1261126931, 2);

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


INSERT INTO `drupal_comments` VALUES (1, 0, 1, 0, 'Ejemplo 1 de comentario', 'Esto es un ejemplo de comentario.', '127.0.0.1', 1262969466, 0, 2, '01/', '', '', '');
INSERT INTO `drupal_comments` VALUES (2, 0, 2, 1, 'Ejemplo 2 de comentario', 'Esto es otro ejemplo de comentario', '127.0.0.1', 1263028149, 0, 2, '02/', '', '', '');
INSERT INTO `drupal_comments` VALUES (3, 0, 3, 1, 'Ejemplo 2 de comentario', 'Ejemplo con codigo: \n[code language="python"]\nprint "hello, comment"\n[/code] y fin', '127.0.0.1', 1263028149, 0, 2, '02/', '', '', '');
