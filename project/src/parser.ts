import { Token, Tokenizer } from './tokenizer';

export interface ASTNode {
    type: string;
    value?: string;
    children?: ASTNode[];
}

export class Parser {
    private tokens: Token[];
    private position: number = 0;

    constructor(tokens: Token[]) {
        this.tokens = tokens;
    }

    parse(): ASTNode[] {
        const nodes: ASTNode[] = [];
        while (this.position < this.tokens.length) {
            const node = this.parseStatement();
            if (node) {
                nodes.push(node);
            }
        }
        return nodes;
    }

    private parseStatement(): ASTNode | null {
        if (this.position >= this.tokens.length) {
            return null;
        }

        const token = this.tokens[this.position];

        if (token.type === 'KEYWORD' && token.value === 'function') {
            return this.parseFunction();
        }

        if (token.type === 'KEYWORD' && (token.value === 'const' || token.value === 'let' || token.value === 'var')) {
            return this.parseVariable();
        }

        if (token.type === 'KEYWORD' && token.value === 'class') {
            return this.parseClass();
        }

        this.position++;
        return {
            type: 'STATEMENT',
            value: token.value
        };
    }

    private parseFunction(): ASTNode {
        this.position++;
        const name = this.position < this.tokens.length ? this.tokens[this.position].value : 'anonymous';
        this.position++;
        
        const children: ASTNode[] = [];
        while (this.position < this.tokens.length && this.tokens[this.position].value !== '}') {
            const child = this.parseStatement();
            if (child) {
                children.push(child);
            } else {
                this.position++;
            }
        }
        
        if (this.position < this.tokens.length && this.tokens[this.position].value === '}') {
            this.position++;
        }

        return {
            type: 'FUNCTION',
            value: name,
            children
        };
    }

    private parseVariable(): ASTNode {
        const keyword = this.tokens[this.position].value;
        this.position++;
        const name = this.position < this.tokens.length ? this.tokens[this.position].value : '';
        this.position++;
        return {
            type: 'VARIABLE',
            value: `${keyword} ${name}`
        };
    }

    private parseClass(): ASTNode {
        this.position++;
        const name = this.position < this.tokens.length ? this.tokens[this.position].value : '';
        this.position++;
        return {
            type: 'CLASS',
            value: name
        };
    }
}

