#!/usr/bin/env python

import sys
from string import *
import os
import time

# FUNCTIONS

def check_keys( p_line, p_keys ):
	p_list = split( p_line, " " );
	if ( len( p_list ) < 1 ):
		return -1;

	for i in range( len(p_keys) ):
		if ( find( p_list[0], p_keys[i] ) != -1 ):
			return p_keys[i];
	return -1;

# END FUNCTIONS

# initialize globals
step_counter = 0

# flags
scp_flag = 1;
removedir_flag = 1;
remove_tar_flag = 0;


replacement_table = {
		"$g_hostname" 				: "$g_hostname      = \"localhost\";",
		"$g_port" 					: "$g_port          = 3306;         # 3306 is default",
		"$g_db_username" 			: "$g_db_username   = \"root\";",
		"$g_db_password" 			: "$g_db_password   = \"\";",
		"$g_database_name" 			: "$g_database_name = \"bugtracker\";",

		"$g_path" 					: "$g_path          = \"http://your_web_address/mantis/\";",

		"$g_use_iis"				: "$g_use_iis   = OFF;",

		"$g_show_version"			: "$g_show_version   = ON;",

		"$g_administrator_email"	: "$g_administrator_email  = \"administrator@nowhere\";",
		"$g_webmaster_email"		: "$g_webmaster_email      = \"webmaster@nowhere\";",
		"$g_from_email"				: "$g_from_email           = \"noreply@nowhere\";",
		"$g_to_email"				: "$g_to_email             = \"nobody@nowhere\";",
		"$g_return_path_email"		: "$g_return_path_email    = \"admin@nowhere\";",

		"$g_allow_signup"			: "$g_allow_signup              = ON;",
		"$g_enable_email_notification"	: "$g_enable_email_notification = ON;",
		"$g_notify_developers_on_new"	: "$g_notify_developers_on_new  = ON;",

		"$g_validate_email"			: "$g_validate_email            = ON;",
		"$g_check_mx_record"		: "$g_check_mx_record           = ON;",
		"$g_hide_user_email"		: "$g_hide_user_email           = OFF;",
		"$g_use_x_priority"			: "$g_use_x_priority            = ON;",

		"$g_use_bcc"				: "$g_use_bcc                   = ON;",
		"$g_use_phpMailer" 			: "$g_use_phpMailer = OFF;",
		"$g_phpMailer_method" 		: "$g_phpMailer_method = 0;",
		"$g_smtp_host" 				: "$g_smtp_host     = \"localhost\";",

		"$g_default_language"		: "$g_default_language     = \"english\";",

		"$g_window_title"			: "$g_window_title     = \"Mantis\";",
		"$g_page_title"				: "$g_page_title       = \"Mantis\";",

		"$g_show_report"			: "$g_show_report = BOTH;",
		"$g_show_update"			: "$g_show_update = BOTH;",
		"$g_show_view" 				: "$g_show_view   = BOTH;",

		"$g_show_source" 			: "$g_show_source   = OFF;",

		"$g_show_footer_menu"		: "$g_show_footer_menu = OFF;",


		"$g_show_project_in_title"	: "$g_show_project_in_title = ON;",

		"$g_show_assigned_names"	: "$g_show_assigned_names = ON;",
		"$g_show_priority_text"		: "$g_show_priority_text  = OFF;",

		"$g_use_jpgraph"			: "$g_use_jpgraph  = OFF;",
		"$g_jpgraph_path"			: "$g_jpgraph_path = \"./jpgraph/\";	# dont forget the ending slash!",

		"$g_cookie_time_length"		: "$g_cookie_time_length = 30000000;",

		"$g_wait_time"				: "$g_wait_time          = 2;",

		"$g_content_expire"			: "$g_content_expire     = 0;",

		"$g_short_date_format"		: "$g_short_date_format    = \"m-d\";",
		"$g_normal_date_format"		: "$g_normal_date_format   = \"m-d H:i\";",
		"$g_complete_date_format"	: "$g_complete_date_format = \"m-d-y H:i T\";",

		"$g_news_limit_method"		: "$g_news_limit_method    = BY_LIMIT;",
		"$g_news_view_limit"		: "$g_news_view_limit      = 7;",
		"$g_news_view_limit_days"	: "$g_news_view_limit_days = 30;",

		"$g_default_new_account_access_level" : "$g_default_new_account_access_level = REPORTER;",

		"$g_default_limit_view"		: "$g_default_limit_view         = 50;",
		"$g_default_show_changed"	: "$g_default_show_changed       = 6;",

		"$g_min_refresh_delay"		: "$g_min_refresh_delay          = 10;    # in minutes",

		"$g_default_advanced_report"	: "$g_default_advanced_report    = BOTH;",
		"$g_default_advanced_view"		: "$g_default_advanced_view      = BOTH;",
		"$g_default_advanced_update"	: "$g_default_advanced_update    = BOTH;",
		"$g_default_refresh_delay"		: "$g_default_refresh_delay      = 30;    # in minutes",
		"$g_default_redirect_delay"		: "$g_default_redirect_delay     = 2;     # in seconds",
		"$g_default_email_on_new"		: "$g_default_email_on_new       = ON;",
		"$g_default_email_on_assigned"	: "$g_default_email_on_assigned  = ON;",
		"$g_default_email_on_feedback"	: "$g_default_email_on_feedback  = ON;",
		"$g_default_email_on_resolved"	: "$g_default_email_on_resolved  = ON;",
		"$g_default_email_on_closed"	: "$g_default_email_on_closed    = ON;",
		"$g_default_email_on_reopened"	: "$g_default_email_on_reopened  = ON;",
		"$g_default_email_on_bugnote"	: "$g_default_email_on_bugnote   = ON;",
		"$g_default_email_on_status"	: "$g_default_email_on_status    = 0; # @@@ Unused",
		"$g_default_email_on_priority"	: "$g_default_email_on_priority  = 0; # @@@ Unused",

		"$g_reporter_summary_limit" : "$g_reporter_summary_limit = 10;",
		"$g_summary_pad"			: "$g_summary_pad            = 5;",

		"$g_date_partitions"		: "$g_date_partitions = array( 1, 2, 3, 7, 30, 60, 90, 180, 365);",

		"$g_bugnote_order"			: "$g_bugnote_order = \"ASC\";",

		"$g_allow_file_upload"		: "$g_allow_file_upload    = OFF;",
		"$g_file_upload_method"		: "$g_file_upload_method   = DISK;",
		"$g_max_file_size"			: "$g_max_file_size        = 5000000;",

		"$g_allow_html_tags"		: "$g_allow_html_tags        = ON;",
		"$g_allow_href_tags"		: "$g_allow_href_tags        = ON;",

		"$g_primary_table_tags" 	: "$g_primary_table_tags          = \"\";",

		"$g_hr_size"				: "$g_hr_size  = 1;",
		"$g_hr_width" 				: "$g_hr_width = 50;",

		"$g_ldap_server" 			: "$g_ldap_server = \"192.168.192.38\";",
		"$g_ldap_root_dn" 			: "$g_ldap_root_dn = \"dc=traffic,dc=redflex,dc=com,dc=au\";",
		"$g_ldap_organisation" 		: "$g_ldap_organisation = \"(organizationname=*Traffic)\";",
		"$g_use_ldap_email" 		: "$g_use_ldap_email = OFF;",

		"$g_reopen_bug_threshold"	: "$g_reopen_bug_threshold = DEVELOPER;",
		"$g_quick_proceed "			: "$g_quick_proceed        = ON;",
		"$g_login_method"			: "$g_login_method         = MD5;",
		"$g_limit_reporters"		: "$g_limit_reporters         = ON;",
		"$g_allow_close_immediately": "$g_allow_close_immediately = OFF;",
		"$g_allow_account_delete"	: "$g_allow_account_delete = OFF;",

		"$g_php" 					: "$g_php = \".php\";",
		"$g_icon_path" 				: "$g_icon_path = $g_path.\"images/\";"
	}

# check to see if parameter is properly supplied
print ''
print '[ 00 ]  Checking number of parameters'
print '[ 01 ]  Number of parameters: ' + str(len(sys.argv))
if ( len(sys.argv) < 2 ):
	print 'You must supply a release number'
	sys.exit()

print '[ 02 ]  Release number: ' + str(len(sys.argv))
release = sys.argv[1]
release_name = 'mantis-' + str(sys.argv[1])

mantis_directory = '/home/www/mantis-' + str(release)
mantis_image_directory = mantis_directory + '/images'
mantis_doc_directory = mantis_directory + '/doc'
mantis_lang_directory = mantis_directory + '/lang'
mantis_default_directory = mantis_directory + '/default'
mantis_sql_directory = mantis_directory + '/sql'

print '[ 03 ]  Making directory: ' + mantis_directory
res = os.system( 'mkdir ' + mantis_directory )

print '[ 04 ]  Making Mantis image directory'
res = os.system( 'mkdir ' + mantis_image_directory )
print '[ 04a]  Making Mantis doc directory'
res = os.system( 'mkdir ' + mantis_doc_directory )
print '[ 04b]  Making Mantis lang directory'
res = os.system( 'mkdir ' + mantis_lang_directory )
print '[ 04c]  Making Mantis default directory'
res = os.system( 'mkdir ' + mantis_default_directory )
print '[ 04d]  Making Mantis sql directory'
res = os.system( 'mkdir ' + mantis_sql_directory )

print '[ 05 ]  Copying Mantis files'
res = os.system( 'cp /home/www/mantis/* ' + mantis_directory )
res = os.system( 'rm '+mantis_directory+'/config_inc.php' )

print '[ 06 ]  Copying Mantis image files'
res = os.system( 'cp /home/www/mantis/images/* ' + mantis_image_directory )
print '[ 06a]  Copying Mantis doc files'
res = os.system( 'cp /home/www/mantis/doc/* ' + mantis_doc_directory )
print '[ 06b]  Copying Mantis lang files'
res = os.system( 'cp /home/www/mantis/lang/* ' + mantis_lang_directory )
print '[ 06c]  Copying Mantis default files'
res = os.system( 'cp /home/www/mantis/default/* ' + mantis_default_directory )
print '[ 06d]  Copying Mantis sql files'
res = os.system( 'cp /home/www/mantis/sql/* ' + mantis_sql_directory )

# read in config file
#print '[ 07 ]  Reading in original config file'
#infile = open( '/home/www/mantis/default/config_inc.php', 'r' )
#config_file = infile.readlines()
#infile.close()

# open config file for writing
#print '[ 08 ]  Opening new config file'
#outfile = open( mantis_default_directory + '/config_inc.php', 'w' )

#print '[ 09 ]  Processing file... Inserting default values'

#config_file_len = len( config_file )

### BEGIN REPLACEMENTS
# perform replacements for default values
#for i in range ( config_file_len ):
#	line = strip( config_file[i] )

#	DO common replacements
#	check to see if a replacement is needed
#	key = check_keys ( line, replacement_table.keys() )
#	if ( key != -1 ):
#		print '[ 10 ]  Processing Value : ' + key
#		config_file[i] = replacement_table[key];

#	DO specialized replacements
#	set version
#	if ( find( line, '$g_mantis_version' ) != -1 ):
#		config_file[i] = "$g_mantis_version = \"" + release + "\";"

#	comment out error_reporting()
#	if ( find( line, 'error_reporting' ) != -1 ):
#		if ( find( line, '#' ) == -1 ):
#			config_file[i] = "#" + line

### END REPLACEMENTS

# write out the new config file
#print '[ 11 ]  Writing new config file'
#for i in range ( config_file_len ):
#	line = strip( config_file[i] )

#	skip empty lines
#	if (len(line)==0):
#		outfile.write( '\n' )
#		continue

#	print properly formatted output
#	if (line[0]=="<"):
#		outfile.write( line + '\n' )
#	elif (line[0]=="?"):
#		outfile.write( line )
#	else:
#		outfile.write( '\t' + line + '\n' )

# close config file
#print '[ 12 ]  Closing new config file'
#outfile.close()

print '[ 13 ]  Creating TAR archive'
res =  os.system( 'tar cf ' + release_name + '.tar ' + release_name )
print '[ 14 ]  GZIPping TAR archive'
res =  os.system( 'gzip ' + release_name + '.tar' )

if ( scp_flag==1 ):
	print '[ 15 ]  SCP\'ing file to SourceForge'
	res =  os.system( 'scp ' + release_name + '.tar.gz prescience@shell.sourceforge.net:/home/groups/m/ma/mantisbt/htdocs/' )

print '[ 16 ]  Performing cleanup'

if ( removedir_flag==1 ):
	print '[ 17 ]  Removing directory'
	res =  os.system( 'rm -rf ' + mantis_directory )

if ( remove_tar_flag==1 ):
	print '[ 17 ]  Removing TAR archive'
	res =  os.system( 'rm ' + release_name + '.tar.gz' )


print "[ 18 ]  Finished\n"
