<?php
    $username = "root";
    $password = "password";
    $host = "localhost";
    $database="fishtank";

$server = mysql_connect($host, $username, $password);
    $connection = mysql_select_db($database, $server);

    $myquery = "
SELECT  `temperature`, `measurementTime` FROM  `temperature` ORDER BY measurementTime DESC LIMIT 10
";
    $query = mysql_query($myquery);
    
    if ( ! $query ) {
        echo mysql_error();
        die;
    }
    
    $data = array();
    
    for ($x = 0; $x < mysql_num_rows($query); $x++) {
        $data[] = mysql_fetch_assoc($query);
    }
    
    echo json_encode($data);     
     
    mysql_close($server);
?>