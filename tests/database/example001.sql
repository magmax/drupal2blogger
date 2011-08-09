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
