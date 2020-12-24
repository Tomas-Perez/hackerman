Trying to access a random page gave a 404 with links to a gitlab and twitter.
This gave me the idea that the challenge was solved before. Googling gives the solution to the challenge, but let's get a hint and continue.
https://ctftime.org/writeup/8574

The solution says to check /robots.txt which gives the following output
User-Agent: *
Disallow: /backup-files

If we look in backup-files we get index.txt and download.txt which are the source files for the server.

Note: php does not have implicit global variables.
This case will not work:

$something = "Hi!";

function whatever() {
    echo $something;
}

So $S_KEY is useless in most of the code, except when it is initialized in validate_hash.

Taking gen_hash we can generate a hash with whatever storagesv we want.
In download.php we can see that if we request storagesv "gimmeflag" we will get the flag value with a die() function.

We generate a hash with "gimmeflag", which we can also validate with validate_hash to make sure it is right and send it on a request.