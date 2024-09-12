<?php
/**
 * This helper program generates a SQL script to help recovering individual
 * issues from a database backup, e.g. after accidental deletion.
 *
 * The overall process is as follows:
 * 1. Restore the backup into a new database
 * 2. Identify the ID(s) of the issue(s) to recover
 * 3. Generate the recovery script
 *    - Setup a temporary MantisBT code base in a directory of your choice
 *    - Update config_inc.php to point to the DB restored in 1.
 *    - Populate the $t_bug_list variable below with the list of issue IDs
 *      identified in 2.
 *    - Save the modified script at root of temp MantisBT dir
 *    - Run the script
 * 4. Review the generated SQL script
 * 5. Backup the target database as needed
 * 5. Manually execute the script in the target database
 */

# List of issue IDs to recover
$g_bug_list = array(

);

/**
 * @global string $g_filename Path where to save the generated SQL script.
 */
$g_filename = 'restore.sql';


# ----------------------------------------------------------------------------
# No edit below this line
#

echo "Generating restore script...\n";

if( !$g_bug_list ) {
	echo "Update the '\$g_bug_list' array with the issues to restore\n";
	exit( 1 );
}
echo "Issues to restore: " . implode( ', ', $g_bug_list ) . "\n";

if( file_exists( $g_filename ) ) {
	$t_reply = readline( "File '$g_filename' already exists. Overwrite ? " );
	if( strtolower( $t_reply[0] ?? '' ) !== 'y' ) {
		echo "Aborting." . PHP_EOL;
		exit( 1 );
	}
}

global $g_bypass_headers;
$g_bypass_headers = 1;

include 'core.php';

# List of tables to restore with corresponding key field for bug id
$t_tables = array(
	'bug'                 => 'id',
	'bug_text'            => 'id',            # requires special handling
	'bug_file'            => 'bug_id',
	'bugnote'             => 'bug_id',
	'bugnote_text'        => 'bug_id',        # requires special handling
	'bug_relationship'    => 'source_bug_id', # requires special handling
	'sponsorship'         => 'bug_id',
	'bug_revision'        => 'bug_id',
	'bug_history'         => 'bug_id',
	'bug_monitor'         => 'bug_id',
	'bug_tag'             => 'bug_id',
	'custom_field_string' => 'bug_id',
);
$t_has_attachments = false;

$t_file = fopen( $g_filename, 'w' );
fwrite( $t_file, "-- MantisBT Issue Restore script" . PHP_EOL );
fwrite( $t_file, "-- Generated by " . basename( __FILE__ )
	. " on " . date( "c" ) . PHP_EOL
);
fwrite( $t_file, "-- Issues to restore: " . implode( ', ', $g_bug_list ) . PHP_EOL . PHP_EOL );

# Main loop
foreach( $t_tables as $t_table => $t_field ) {
	# Build query to retrieve rows to recover
	$t_query = 'SELECT t.* FROM {' . $t_table . '} t';
	$t_where = '';
	switch( $t_table ) {
		case 'bug_text':
			$t_query .= ' JOIN {bug} b ON b.bug_text_id = t.id';
			$t_field = 'b.' . $t_field;
			break;
		case 'bugnote_text':
			$t_query .= ' JOIN {bugnote} n ON n.bugnote_text_id = t.id';
			$t_field = 'n.' . $t_field;
			break;
		case 'bug_relationship':
			$t_where = ' OR ' . where_clause( 'destination_bug_id' );
			break;
	}
	$t_query .= ' WHERE ' . where_clause( $t_field ) . $t_where;

	$t_result = db_query( $t_query );
	$t_row = db_fetch_array( $t_result );

	# Nothing to recover for this table
	if( !$t_row ) {
		continue;
	}

	if( $t_table == 'bug_file' ) {
		$t_has_attachments = true;
	};

	# Generate Insert statement SQL
	fwrite( $t_file,
		'INSERT INTO ' . db_get_table( $t_table )
		. ' VALUES ' . PHP_EOL . insert_values( $t_row )
	);
	while( $t_row = db_fetch_array( $t_result ) ) {
		fwrite( $t_file, ',' . PHP_EOL . insert_values( $t_row ) );
	};
	fwrite( $t_file, ';' . PHP_EOL . PHP_EOL );
}

fclose( $t_file );

echo "Restore script saved in: $g_filename\n";

if( $t_has_attachments ) {
	echo "WARNING: Issues with attachments - restore these to the file system manually\n";
}


/**
 * Generate where clause to select issue IDs.
 * @param string $p_field Field name for Bug ID
 * @return string SQL where clause
 */
function where_clause( $p_field ) {
	static $s_where;
	if( !$s_where ) {
		global $g_bug_list;
		$s_where = ' IN (' . implode( ',', $g_bug_list ) . ')';
	}
	return $p_field . $s_where;
}

/**
 * Returns row data ready for use in insert statement values.
 * @param array $p_row Data row
 * @return string Escaped list of values
 */
function insert_values( $p_row ) {
	array_walk( $p_row,
		function( &$p_str ) {
			global $g_db;
			if( !is_numeric( $p_str ) ) {
				$p_str = $g_db->qStr( $p_str );
			}
			echo $p_str, "\n";
		}
	);
	return '(' . implode( ',', $p_row ) . ')';

}
