export interface Token {
    text: string;
    kind: string;
}

export class Tokenizer {
    tokenize(input: string): Token[] {
        const tokens: Token[] = [];
        const words = input.match(/\b[a-zA-Z_][a-zA-Z0-9_]*\b/g) || [];
        
        for (const word of words) {
            tokens.push({
                text: word,
                kind: 'IDENTIFIER'
            });
        }
        
        return tokens;
    }
}

