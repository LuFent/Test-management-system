import {
  autocompletion,
  closeCompletion,
  startCompletion,
} from "@codemirror/autocomplete";
import {syntaxTree} from "@codemirror/language"
import { gherkin } from '@codemirror/legacy-modes/mode/gherkin';


export default function getAutoCompletion(vales)
{

    function myCompletions(context) {
     let word = context.matchBefore(/\w*/)
      if (word.from == word.to && !context.explicit)
        return null
      let text = context.state.doc.text;
      let charPos = context.pos;
      let length = 0;
      let currentLine = null;
      for (let lineNumber = 0; lineNumber < text.length; lineNumber++){
          length += text[lineNumber].length + 1;
          if (length >= charPos) {
            currentLine = text[lineNumber];
            break
          }
      }
      //console.log(currentLine);

      return {
        from: word.from,
        options: [

        ]
      }
    }

    return autocompletion({override: [myCompletions]})
}