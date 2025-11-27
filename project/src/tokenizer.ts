export interface Token {
    type: string;
    value: string;
    line: number;
    column: number;
}

export class Tokenizer {
    private content: string;
    private position: number = 0;
    private line: number = 1;
    private column: number = 1;

    constructor(content: string) {
        this.content = content;
    }

    tokenize(): Token[] {
        const tokens: Token[] = [];
        
        while (this.position < this.content.length) {
            const token = this.nextToken();
            if (token) {
                tokens.push(token);
            }
        }
        
        return tokens;
    }

    private nextToken(): Token | null {
        this.skipWhitespace();
        
        if (this.position >= this.content.length) {
            return null;
        }

        const char = this.content[this.position];
        const startLine = this.line;
        const startColumn = this.column;

        if (this.isLetter(char) || char === '_' || char === '$') {
            return this.readIdentifier(startLine, startColumn);
        }

        if (this.isDigit(char)) {
            return this.readNumber(startLine, startColumn);
        }

        if (char === '"' || char === "'") {
            return this.readString(startLine, startColumn);
        }

        if (this.isOperator(char)) {
            return this.readOperator(startLine, startColumn);
        }

        this.advance();
        return {
            type: 'UNKNOWN',
            value: char,
            line: startLine,
            column: startColumn
        };
    }

    private readIdentifier(line: number, column: number): Token {
        let value = '';
        while (this.position < this.content.length && 
               (this.isLetter(this.content[this.position]) || 
                this.isDigit(this.content[this.position]) ||
                this.content[this.position] === '_' ||
                this.content[this.position] === '$')) {
            value += this.content[this.position];
            this.advance();
        }
        return {
            type: this.isKeyword(value) ? 'KEYWORD' : 'IDENTIFIER',
            value,
            line,
            column
        };
    }

    private readNumber(line: number, column: number): Token {
        let value = '';
        while (this.position < this.content.length && this.isDigit(this.content[this.position])) {
            value += this.content[this.position];
            this.advance();
        }
        return {
            type: 'NUMBER',
            value,
            line,
            column
        };
    }

    private readString(line: number, column: number): Token {
        const quote = this.content[this.position];
        let value = quote;
        this.advance();

        while (this.position < this.content.length && this.content[this.position] !== quote) {
            if (this.content[this.position] === '\\') {
                value += this.content[this.position];
                this.advance();
            }
            value += this.content[this.position];
            this.advance();
        }

        if (this.position < this.content.length) {
            value += this.content[this.position];
            this.advance();
        }

        return {
            type: 'STRING',
            value,
            line,
            column
        };
    }

    private readOperator(line: number, column: number): Token {
        const char = this.content[this.position];
        this.advance();
        return {
            type: 'OPERATOR',
            value: char,
            line,
            column
        };
    }

    private skipWhitespace(): void {
        while (this.position < this.content.length) {
            const char = this.content[this.position];
            if (char === ' ' || char === '\t') {
                this.advance();
            } else if (char === '\n') {
                this.line++;
                this.column = 1;
                this.advance();
            } else {
                break;
            }
        }
    }

    private advance(): void {
        this.position++;
        this.column++;
    }

    private isLetter(char: string): boolean {
        return /[a-zA-Z]/.test(char);
    }

    private isDigit(char: string): boolean {
        return /[0-9]/.test(char);
    }

    private isOperator(char: string): boolean {
        return /[+\-*/=<>!&|{}[\]();,.:]/.test(char);
    }

    private isKeyword(value: string): boolean {
        const keywords = [
            'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
            'return', 'import', 'export', 'class', 'interface', 'type', 'async',
            'await', 'try', 'catch', 'throw', 'new', 'this', 'super', 'extends'
        ];
        return keywords.includes(value);
    }
}

