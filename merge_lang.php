<?php
	# -- GLOBAL VARIABLES --
	$new_strings = array();
	$old_strings = array();
	# - ---
	function load_files( $p_old_file, $p_new_file ) {
		global $new_strings, $old_strings;

		$new_strings = file( $p_new_file );
		$old_strings = file( $p_old_file );
	}
	# - ---
	function found( $p_haystack, $p_needle ) {
		if ( strpos( $p_haystack, $p_needle ) > 0 ) {
			return true;
		} else {
			return false;
		}
	}
	# - ---
	# parse the string and grab the variable
	function get_key( $p_string ) {
		$p_string = trim( $p_string );
		if ( '$' != $p_string[0] ) {
			return '';
		}
		$p_string = str_replace( ' ', '', $p_string );
		$p_array = explode('=', $p_string);
		return $p_array[0];
	}
	# - ---
	# parse the string and grab the variable
	function get_data( $p_string ) {
		$p_string = trim( $p_string );
		if ( '$' != $p_string[0] ) {
			return '';
		}
		$p_string = str_replace( ' ', '', $p_string );
		$p_array = explode('=', $p_string);
		return $p_array[1];
	}
	# - ---
	function compare_files() {
		global $new_strings, $old_strings;

		# create keyed array of the new strings
		$strings = $new_strings;
		$new_strings = array();
		foreach( $strings as $string ) {
			$string = trim( $string );
			$key = get_key( $string );
			if ( strlen( $key ) > 0 ) {
				$new_strings[$key] = $string;
			}
		}

		# loop over original strings
		# report if new strings are different, same, or missing.
		$skip = 0;
		$counter = 0;
		$diff_counter = 0;
		$missing_counter = 0;
		foreach ( $old_strings as $original_string ) {
			$original_string = trim( $original_string );
			$p_original_string = trim( $original_string );
			$counter++;
			$t_counter = str_pad( $counter, 3, ' ', STR_PAD_LEFT );
			# ignore header section
			if ( 0 == $skip ) {
				if ( '?>' == $p_original_string ) {
					$skip = 1;
				}
			} else {
				# grab the key
				$key = get_key( $original_string );
				if ( empty( $key ) ) {
					continue;
				}
				if ( array_key_exists( $key, $new_strings ) ) {
					if ( $new_strings[$key] != $original_string ) {
						$diff_counter++;
						echo "[$t_counter] [O] $original_string\n";
						echo "      [N] ".$new_strings[$key]."\n\n";
					}
				} else {
					$missing_counter++;
					echo "[$t_counter] NEWFILE IS MISSING: $original_string \n\n";
				}
			}
		}
		echo "Different: $diff_counter\t\tMissing: $missing_counter\n";
	}
	# - ---
	function merge_files( $p_old_file ) {
		global $new_strings, $old_strings;

		# create keyed array of the new strings
		$strings = $new_strings;
		$new_strings = array();
		foreach( $strings as $string ) {
			$string = trim( $string );
			$key = get_key( $string );
			if ( strlen( $key ) > 0 ) {
				$new_strings[$key] = $string;
			}
		}

		$fp = fopen( $p_old_file, 'wb' );
		# print out header
		$strings = $old_strings;
		foreach( $strings as $string ) {
			$p_string = trim( $string );
			if ( '?>' === $p_string ) {
				fwrite( $fp, rtrim($string)."\n" );
				break;
			}
			fwrite( $fp, rtrim($string)."\n" );
		}

		# loop over original strings
		# report if new strings are different, same, or missing.
		$skip = 0;
		$diff_counter = 0;
		$missing_counter = 0;
		foreach ( $old_strings as $original_string ) {
			$original_string = trim( $original_string );
			$p_original_string = trim( $original_string );
			# ignore header section
			if ( 0 == $skip ) {
				if ( '?>' == $p_original_string ) {
					$skip = 1;
				}
			} else {
				# grab the key
				$key = get_key( $original_string );
				if ( empty( $key ) ) {
					fwrite( $fp, $p_original_string."\n" );
					continue;
				}
				if ( array_key_exists( $key, $new_strings ) ) {
					if ( $new_strings[$key] != $original_string ) {
						# diff
						$diff_counter++;
						fwrite( $fp, $new_strings[$key]."\n" );
					} else {
						fwrite( $fp, $p_original_string."\n" );
					}
				} else {
					$missing_counter++;
					fwrite( $fp, $p_original_string."\n" );
				}
			}
		}
		fclose( $fp );
		echo "Different: $diff_counter\t\tMissing from Newfile: $missing_counter\n";
		echo "Merged\n";
	}
	# - ---
	function print_usage() {
		echo "\nUsage:\n        php -q merge_lang.php <option> <oldfile> <newfile>\n        -c compare only\n        -m merge\n";
	}
	# - ---

	# -- MAIN --
	$argv = $_SERVER['argv'];
	$argc = $_SERVER['argc'];

	# too few arguments?
	if ( $argc < 4 ) {
		print_usage();
		exit;
	}

	if ( '-c' == $argv[1] ) {
		load_files( $argv[2], $argv[3] );
		compare_files();
	} else if ( '-m' == $argv[1] ) {
		load_files( $argv[2], $argv[3] );
		merge_files( $argv[2] );
	} else {
		print_usage();
	}
?>