import {
  autocompletion,
  closeCompletion,
  startCompletion,
} from "@codemirror/autocomplete";
import {syntaxTree} from "@codemirror/language"
import { gherkin } from '@codemirror/legacy-modes/mode/gherkin';
import { keywords } from "./KeyWords";
import { stepTypes } from "./KeyWords";


function getLineByNumber(context, requiredLineNumber){
    if (context.state.doc.constructor.name == "TextLeaf")
    {
        return context.state.doc.text[requiredLineNumber];
    }
    else
    {
        let lines = 0;
        let currentLine;
        for(let leafNumber = 0; leafNumber < context.state.doc.children.length; leafNumber++)
        {
            let leafText = context.state.doc.children[leafNumber].text;
                for(let lineNumber = 0; lineNumber < leafText.length; lineNumber++) {
                  if(lines == requiredLineNumber) {
                    currentLine = leafText[lineNumber];
                    return currentLine;
                  }
                  lines += 1;
            }
        }
    }
}

function getTextLength(context){
    if (context.state.doc.constructor.name == "TextLeaf")
    {
        return context.state.doc.text.length;
    }
    else
    {
        return context.state.doc.lines;
    }
}

function getAutoCompletionOptions(context, values){
  let lan = "en";
  let word = context.matchBefore(/\w*/);
  let text = context.state.doc.text;
  let charPos = context.pos;
  let length = 0;
  let currentLine = null;
  let currentKeyword;
  let enteredText;
  let keyword;
  let keywordPrev;
  let lineNumber;
  for (lineNumber = 0; lineNumber < getTextLength(context); lineNumber++){

      let line = getLineByNumber(context, lineNumber);
      let lineLength = line.length;
      length += lineLength + 1;
      line = line.trim();

      if(line.startsWith("#")){
          let lineWithoutWhiteSpaces = line.trim().replaceAll(" ", "");
          if(lineWithoutWhiteSpaces.startsWith("#language:"))
          {
            lan = lineWithoutWhiteSpaces.replace("#language:", "").trim();
            if (!(lan in keywords)){
                return [];
            }
            continue;
          }
      }
      if(length >= charPos) {
        currentLine = line;
        break
      }
  }
  keyword = currentLine.split(/(\s+)/)[0].trim();

  if (!(keyword in keywords[lan]))
  {
    return []
  }
  if (keywords[lan][keyword] != "Conjunction")
  {
    currentKeyword = keywords[lan][keyword];
  }
  else
  {
      while(true){
          lineNumber--;
          if(lineNumber < 0){
            return []
          }
          let line = getLineByNumber(context, lineNumber).trim();
          keywordPrev = line.split(/(\s+)/)[0].trim();
          if (!(keywordPrev in keywords[lan])){
            return []
          }
          if (keywords[lan][keywordPrev] != "Conjunction") {
            currentKeyword = keywords[lan][keywordPrev];
            break
          }
      }
  }
  enteredText = currentLine.replace(keyword, "").trim();
  let autoCompletions = [];

  if (!!currentKeyword){
     autoCompletions = values[currentKeyword].map((opt) => {
     let label = opt.replaceAll("[^\n].*", "<...>");
     if (opt.search(enteredText) == 0)
     {
         return {apply: label.replace(enteredText, ""), type: "keyword", label: label}
     }
     else {
         return null
     }
    }).filter((opt) => opt != null)
  }
  return autoCompletions;
}


export default function getAutoCompletion(values)
{
    function myCompletions(context) {
      let word = context.matchBefore(/\w*/);
      let autoCompletions = getAutoCompletionOptions(context, values);
      return {
        from: word.from,
        options: autoCompletions
      }
    }
    return autocompletion({override: [myCompletions]})
}