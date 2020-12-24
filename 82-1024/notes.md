To get the styles the server is using the color parameter to include a css file with a simple echo.
If we put a relative path to wherever we want in the color parameter, the content of that location will be included in the style of the html.
Copy and paste to get the source code.

When a ranking is destroyed, a file is created under the $path variable to store the $ranking variable.

The "load game" function is taking a serialized php object. We can change the object to a Ranking with whatever we want and when it is destroyed, the file with the payload we need will be written.

A payload with php code echoing the flag env var should leak the flag.

The Ranking destructor can only write under the "games" directory, we cannot overwrite the other php files.
However, we can easily create a new php file and open it from the browser.
The problem: either on serialization or on file writing the server is removing all php tags so we cannot inject php code.
Solution: it was not removing anything you dummy, the flag was blank becuase the env var is "FLAG" not "flag"