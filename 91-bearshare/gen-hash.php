<?php
$nonce = "4044d95cd74a58237a8a668950bef8f9";

function global_f() {
    echo $S_KEY;
}

function gen_hash($n, $sv){
	$first = hash_hmac('sha256', $n, $S_KEY);
	return hash_hmac('sha256', $sv, $first);
}

function validate_hash($post_hash, $post_storagesv, $post_nonce){
	if(empty($post_hash) || empty($post_storagesv)){
		die('Cannot verify server');
	}
	// if(isset($_POST['nonce'])){
    $S_KEY = hash_hmac('sha256',$post_nonce,$S_KEY);
	// }
	$final_hash = hash_hmac('sha256',$post_storagesv,$S_KEY);
	if ($final_hash !== $post_hash){
		die('Cannot verify server');
	}
}

$storagesv = "gimmeflag";

$hash = gen_hash($nonce, $storagesv);

validate_hash($hash, $storagesv, $nonce);

echo "nonce: " . $nonce . "\n";
echo "storagesv: " . $storagesv . "\n";
echo "hash: " . $hash . "\n";
echo "messid: " . "whatever" . "\n";

echo "payload: nonce=" . $nonce . "&hash=" . $hash . "&storagesv=" . $storagesv . "&messid=dasdas\n"; 

?>