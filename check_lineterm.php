<?php
	# -- GLOBAL VARIABLES --
	$lang_files = array();
	$english_strings = array();
	# - ---
	define( LF_ONLY,		0 );
	define( CR_ONLY,		1 );
	define( CRLF_ONLY,		2 );
	define( LFCR_MIXED,		3 );
	define( LFCRLF_MIXED,	4 );
	define( CRLFCR_MIXED,	5 );
	define( CRLFCRLF_MIXED,	6 );
	# - ---
	function print_result( $p_result ) {
		switch( $p_result ) {
			case CRLF_ONLY:	echo "*** Windows Format\n";
				break;
			case CR_ONLY:	echo "*** Mac Format\n";
				break;
			case LF_ONLY:	echo "UNIX Format\n";
				break;
			case LFCR_MIXED:	echo "### Mixed Format: LF and CR\n";
				break;
			case LFCRLF_MIXED:	echo "### Mixed Format: LF and CRLF\n";
				break;
			case CRLFCR_MIXED:	echo "### Mixed Format: CRLF and CR\n";
				break;
			case CRLFCRLF_MIXED:echo "### Mixed Format: CRLF and CR and LF\n";
				break;
		}
	}
	# - ---
	# read in all files
	function process_files( $p_dir ) {
		$cwd = getcwd();
		$cwd .= '\\'.$p_dir;
		chdir( $cwd );
		if ( $handle = opendir( $cwd ) ) {
			echo "Directory: ".getcwd()."\n";
			$file_arr = array();
		    while (false !== ( $file = readdir( $handle ) )) {
		    	$file_arr[] = $file;
			}
		    closedir( $handle );
		    foreach( $file_arr as $file ) {
		    	#echo "file: $file\n";
				if (( '.' == $file )||( '..' == $file )||( 'CVS' == $file )) {
					continue;
				}
			    if ( TRUE == is_dir( $file ) ) {
			    	# directory
					process_files( $file );
			    } else {
			    	echo "Procesing: ".getcwd()."\\".$file."";
			    	$result = check_lineterm( $file );
			    	echo "\n";
			    	if ( LF_ONLY != $result ) {
						print_result( $result );
					}
			    }
		    }
		}
		chdir( '..' );
	}
	# - ---
	function rewrite_file( $p_file ) {
		$strings = file( $p_file );
		$fp = fopen( $p_file, 'wb' );
		foreach( $strings as $string ) {
			fwrite( $fp, rtrim($string)."\n" );
		}
		fclose( $fp );
	}
	# - ---
	# reports if the line terms are LF, CR, CRLF, or a mix
	function check_lineterm( $p_file ) {
		$lf_count = 0;
		$cr_count = 0;
		$crlf_count = 0;

		$strings = file( $p_file );
		$counter = 0;
		foreach( $strings as $string ) {
			$counter++;
			$lf = strpos( $string, "\n" );
			$cr = strpos( $string, "\r" );
			$crlf = strpos( $string, "\r\n" );
			$strlen = strlen( $string )."\n";
			if ($crlf>0) {
				if ( $strlen-2 == $crlf ) {
					$crlf_count++;
				}
			} else if ($lf>0) {
				if ( $strlen-1 == $lf ) {
					$lf_count++;
				}
			} else if ($cr>0) {
				if ( $strlen-1 == $cr ) {
					$cr_count++;
				}
			}
		}
		# Windows is CRLF
		if ((0==$lf_count)&&(0==$cr_count)&&($crlf_count>0)) {
			return CRLF_ONLY;
		}
		# Mac is CR
		if ((0==$lf_count)&&($cr_count>0)&&(0==$crlf_count)) {
			return CR_ONLY;
		}
		# Unix is LF
		if (($lf_count>0)&&(0==$cr_count)&&(0==$crlf_count)) {
			return LF_ONLY;
		}
		if (($lf_count>0)&&($cr_count>0)) {
			return LFCR_MIXED;
		}
		if (($lf_count>0)&&($crlf_count>0)) {
			return LFCRLF_MIXED;
		}
		if (($crlf_count>0)&&($cr_count>0)) {
			return CRLFCR_MIXED;
		}
		if (($crlf_count>0)&&($cr_count>0)&&($lf_count>0)) {
			return CRLFCRLF_MIXED;
		}
	}
	# - ---
	# read in all files
	function process_files_rewrite( $p_dir ) {
		$cwd = getcwd();
		$cwd .= '\\'.$p_dir;
		chdir( $cwd );
		if ( $handle = opendir( $cwd ) ) {
			echo "Directory: ".getcwd()."\n";
			$file_arr = array();
		    while (false !== ( $file = readdir( $handle ) )) {
		    	$file_arr[] = $file;
			}
		    closedir( $handle );
		    foreach( $file_arr as $file ) {
				if (( '.' == $file )||( '..' == $file )||( 'CVS' == $file )) {
					continue;
				}
			    if ( TRUE == is_dir( $file ) ) {
			    	# directory
					process_files_rewrite( $file );
			    } else {
			    	echo "Procesing: ".getcwd()."\\".$file."";
					rewrite_file( getcwd()."\\".$file );
			    }
		    }
		}
		chdir( '..' );
	}
	# - ---
	function print_usage() {
		echo "\nUsage:\n        php -q check_lineterm.php <option> <path/folder>\n        -c check files\n        -f fix file\n        -a fix all files\n";
	}
	# - ---

	# -- MAIN --
	$argv = $_SERVER['argv'];
	$argc = $_SERVER['argc'];

	# too few arguments?
	if ( $argc < 2 ) {
		print_usage();
		exit;
	}

	if ( '-c' == $argv[1] ) {
		if ( isset( $argv[2] ) ) {
			process_files( $argv[2] );
		} else {
			process_files( '.' );
		}
	} else if ( '-f' == $argv[1] ) {
		rewrite_file( $argv[2] );
	} else if ( '-a' == $argv[1] ) {
		process_files_rewrite( $argv[2] );
	} else {
		print_usage();
	}
?>