//#strict on
//#target indesign
//#targetengine "session"
var InDesignMode = false;
if (typeof app !== 'undefined') {
   app.scriptPreferences.version = 7.0;
   InDesignMode = true;
}

var debug = true;

var charsToInsert = {
   'TDC': '-',//'༔',
   'custom': ' ',
   'error': '!',
   'unknown': '?',
   'suffix': '+',
   'particle': '+',
   'verb': '-',
};

var charsToInsertRev = {};
for (var type in charsToInsert) {
   charsToInsertRev[charsToInsert[type]] = true;
}

var suffixes = ['འི', 'འོ', 'འང', 'འམ', 'ར', 'ས'];

var verbs, particles;

/*! https://mths.be/codepointat v0.2.0 by @mathias */
if (!String.prototype.codePointAt) {
(function() {
'use strict'; // needed to support `apply`/`call` with `undefined`/`null`
var defineProperty = (function() {
// IE 8 only supports `Object.defineProperty` on DOM elements
try {
var object = {};
var $defineProperty = Object.defineProperty;
var result = $defineProperty(object, object, object) && $defineProperty;
} catch(error) {}
return result;
}());
var codePointAt = function(position) {
if (this == null) {
throw TypeError();
}
var string = String(this);
var size = string.length;
// `ToInteger`
var index = position ? Number(position) : 0;
if (index != index) { // better `isNaN`
index = 0;
}
// Account for out-of-bounds indices:
if (index < 0 || index >= size) {
return undefined;
}
// Get the first code unit
var first = string.charCodeAt(index);
var second;
if ( // check if it’s the start of a surrogate pair
first >= 0xD800 && first <= 0xDBFF && // high surrogate
size > index + 1 // there is a next code unit
) {
second = string.charCodeAt(index + 1);
if (second >= 0xDC00 && second <= 0xDFFF) { // low surrogate
// https://mathiasbynens.be/notes/javascript-encoding#surrogate-formulae
return (first - 0xD800) * 0x400 + second - 0xDC00 + 0x10000;
}
}
return first;
};
if (defineProperty) {
defineProperty(String.prototype, 'codePointAt', {
'value': codePointAt,
'configurable': true,
'writable': true
});
} else {
String.prototype.codePointAt = codePointAt;
}
}());
}

function getSymbols(string) {
  var length = string.length;
  var index = -1;
  var output = [];
  var character;
  var charCode;
  while (++index < length) {
    character = string.charAt(index);
    charCode = character.charCodeAt(0);
    if (charCode >= 0xD800 && charCode <= 0xDBFF) {
      // Note: this doesn’t account for lone high surrogates;
      // you’d need even more code for that!
      output.push(character + string.charAt(++index));
    } else {
      output.push(character);
    }
  }
  return output;
}

function symbolIsTibetanText(symbol) {
   if (!symbol) {
      return false;
   }
   var cp = symbol.codePointAt(0);
   if((cp >= 0x0F00 && cp <= 0xF03) ||
      //(cp >= 0x0F0B && cp <= 0xF0C) ||
      (cp >= 0x0F40 && cp <= 0xFBC)
   ) {
      return true;
   }
   return false;
}

function escapeRegExp(string) {
    return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}

function replaceAll(string, find, replace) {
  return string.replace(new RegExp(escapeRegExp(find), 'g'), replace);
}

function removeInsertedChars(text) {
   for (var charToReplace in charsToInsertRev) {
      if (charToReplace != ' ') {
         text = replaceAll(text, charToReplace, '');
      }
   }
   return text;
}

function cutWordsInText() {
   var text;
   if (InDesignMode) {
      text = app.selection[0].contents;
   } else {
      text = document.getElementById('text').value;
   }
   if (!text) return;
   text = removeInsertedChars(text);
   var beginIndex = 0;
   var symbols = getSymbols(text);
   if (debug) {
      console.log('initial symbols:');
      console.log(symbols);
   }
   while (beginIndex < symbols.length) {
      // begin at first encountered text character
      while(beginIndex < symbols.length && !symbolIsTibetanText(symbols[beginIndex])) {
         beginIndex = beginIndex + 1;
      }
      if (beginIndex >= symbols.length) { break; }
      var foundSyllables = getNextSyllables(symbols, beginIndex, 4);
      var nbSyllables = foundSyllables.nbSyllables;
      if (nbSyllables < 1) {
         beginIndex = beginIndex + 1;
         continue;
      }
      while (nbSyllables >= 1) {
         var lookupRes = lookupStr(symbols, nbSyllables, foundSyllables.str);
         if (debug) {
            console.log('result:');
            console.log(lookupRes);
         }
         if (lookupRes !== false) {
            // insert charToInsert at index beginIndex + foundSyllables.strLen
//            var charToInsertAfter = lookupRes.suffixLength ? charsToInsert['suffix'] : charsToInsert[lookupRes.type];
            var charToInsertAfter = lookupRes.type == 'particle' ? charsToInsert['TDC'] : charsToInsert[lookupRes.type];
            if (lookupRes.type == 'particle' && symbols[beginIndex -1]) {
               if (symbols[beginIndex -1] == charsToInsert['TDC'] || symbols[beginIndex -1] == charsToInsert['verb'] || symbols[beginIndex -1] == charsToInsert['custom']) {
                  symbols[beginIndex -1] = charsToInsert['particle'];
               } else if (symbols[beginIndex -1] == charsToInsert['error'] || symbols[beginIndex -1] == charsToInsert['unknown']) {
                  symbols.splice(beginIndex, 0, charsToInsert['particle']);
                  beginIndex = beginIndex + 1;
               }
            }
            var nextSymbol = symbols[beginIndex + foundSyllables.strLen + 1];
            var indexShift = 1;
            if (nextSymbol == '་' || nextSymbol == '༌') {
               indexShift = 2;
            }
            symbols.splice(beginIndex+foundSyllables.strLen+indexShift, 0, charToInsertAfter);
            beginIndex = beginIndex + foundSyllables.strLen+indexShift;
            if (lookupRes.suffixLength != 0) {
               if (lookupRes.ashung) {
                  symbols.splice(beginIndex-indexShift-lookupRes.suffixLength, 0, 'འ');
                  beginIndex = beginIndex + 1;
                  symbols.splice(beginIndex-indexShift-lookupRes.suffixLength, 0, charsToInsert['suffix']);
                  beginIndex = beginIndex + 1;
               } else {
                  symbols.splice(beginIndex-indexShift-lookupRes.suffixLength, 0, charsToInsert['suffix']);
                  beginIndex = beginIndex + 1;
               }
            }
            break;
         } else {
            nbSyllables = nbSyllables - 1;
            foundSyllables = getNextSyllables(symbols, beginIndex, nbSyllables);
            if (nbSyllables == 0) {
               if (debug) {
                  console.log('nextSymbol:'+symbols[beginIndex + foundSyllables.strLen + 1]);
               }
               var nextSymbol = symbols[beginIndex + foundSyllables.strLen + 1];
               var indexShift = 1;
               if (nextSymbol == '་' || nextSymbol == '༌') {
                  indexShift = 2;
               }
               symbols.splice(beginIndex+foundSyllables.strLen+indexShift, 0, charsToInsert['unknown']);
               beginIndex = beginIndex + foundSyllables.strLen+indexShift;
            }
         }
      }
   }
   var resStr = symbols.join('');
   for (var i=0; i < custom_rules.length; i++){
      resStr = replaceAll(resStr, custom_rules[i][0]+custom_rules[i][1]+custom_rules[i][2], custom_rules[i][0]+custom_rules[i][3]+custom_rules[i][2]);
   }
   if (InDesignMode) {
      app.selection[0].contents=resStr;
   } else {
      document.getElementById('text').value = resStr;
   }
}

// returns false or the length of the suffix it had to remove to find the string
function lookupStr(symbols, nbSyllables, str) {
   if (debug) {
      console.log('lookup '+str+', nbSyllables = '+nbSyllables);
      console.log(symbols);
   }
   if (!str) return false;
   if (particles[str]) {
      return {suffixLength: 0, type: 'particle'};
   }
   if (verbs[str]) {
      return {suffixLength: 0, type: 'verb'};
   }
   if (words[nbSyllables][str]) {
      return {suffixLength: 0, type: 'TDC'};
   }
   if (custom_words[str]) {
      return {suffixLength: 0, type: 'custom'};
   }
   if (error_words[str]) {
      return {suffixLength: 0, type: 'error'};
   }
   var suffixLength = getSuffixLength(str, suffixes);
   if (!suffixLength) {
      return false;
   }
   str = str.slice(0, -suffixLength);
   if (!str) {return false;}
   if (verbs_ashung[str]) {
      return {suffixLength: suffixLength, type: 'verb', ashung: true};
   }
   if (words_ashung[str]) {
      return {suffixLength: suffixLength, type: 'TDC', ashung: true};
   }
   if (verbs[str]) {
      return {suffixLength: suffixLength, type: 'verb'};
   }
   if (particles[str]) {
      return {suffixLength: suffixLength, type: 'particle'};
   }
   if (words[nbSyllables][str]) {
      return {suffixLength: suffixLength, type: 'TDC'};
   }
   if (custom_words[str]) {
      return {suffixLength: suffixLength, type: 'custom'};
   }
   if (error_words[str]) {
      return {suffixLength: suffixLength, type: 'error'};
   }
   return false;
}

// simple polyfill for ES6 endsWith
// http://stackoverflow.com/questions/280634/endswith-in-javascript
if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}

second_suffixes = {
   'གས': true,
   'ངས': true,
   'བས': true,
   'མས': true,
};

// get the length of the suffix (or 0)
function getSuffixLength(str, suffixes) {
   for (var i=0; i < suffixes.length; i++){
      if (str.endsWith(suffixes[i])) {
         if (suffixes[i] == 'ས' && second_suffixes[str.slice(-2)] && str.length > 2 && str.slice(-3).indexOf('་') == -1) {
            if (debug) {
               console.log('detecting second suffix ས, not considering it grammatical suffix');
            }
            continue;
         } else {
            console.log('detecting grammatical suffix '+suffixes[i]);
            return suffixes[i].length;
         }
      }
   }
   return 0;
}

function getNextSyllables(symbols, beginIndex, nbSyllables) {
   var resNbSyllables = 1;
   var resStr = '';
   var resStrLen = 0;
   var lastIsTsheg = false;
   if (debug) {
      console.log('getNextSyllables, nbSyllables = '+nbSyllables);
   }
   while(beginIndex < symbols.length && (symbolIsTibetanText(symbols[beginIndex]) || symbols[beginIndex] == '་' || symbols[beginIndex] == '༌')) {
      if (lastIsTsheg) {
         resStrLen = resStrLen + 1;
         resStr = resStr + '་';
      }
      if (symbols[beginIndex] == '་' || symbols[beginIndex] == '༌') {
         lastIsTsheg = true;
         if (resNbSyllables >= nbSyllables) {
            break;
         }
         resNbSyllables = resNbSyllables + 1;
      } else {
         lastIsTsheg = false;
         resStrLen = resStrLen + 1;
         resStr = resStr + symbols[beginIndex];
      }
      beginIndex = beginIndex + 1;
   }
//   if (lastIsTsheg) {
//      resNbSyllables = resNbSyllables - 1;
//   }
   if (debug) {
      console.log('returning:');
      console.log({str: resStr, nbSyllables: resNbSyllables, strLen: resStrLen});
   }
   return {str: resStr, nbSyllables: resNbSyllables, strLen: resStrLen};
}

function mainInDesign(){
  if (app.documents.length != 0){
    if (app.selection.length == 1){
      //Evaluate the selection based on its type.
      switch (app.selection[0].constructor.name){
        case "InsertionPoint":
        case "Character":
        case "Word":
        case "TextStyleRange":
        case "Line":
        case "Paragraph":
        case "TextColumn":
        case "Text":
        case "Story":
          //The object is a text object; pass it on to a function.
          cutWordsInText();
        break;
        //In addition to checking for the above text objects, we can
        //also continue if the selection is a text frame selected with
        //the Selection tool or the Direct Selection tool.
       // case "TextFrame":
          //If the selection is a text frame, get a reference to the
          //text in the text frame.
       //   myProcessText(app.selection[0].texts.item(0));
       //   break;
        default:
          alert("The selected object is not a text object. Select some text and try again.");
          break;
      }
    }
    else{
      alert("Please select some text and try again.");
    }
  }
}

function main() {
   if(InDesignMode) {
      mainInDesign();
   }
}

var words = [{}, {}, {}, {}, {}];

// INSERT DATA HERE!
