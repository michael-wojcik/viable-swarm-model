const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', { url: 'http://localhost' });
global.window = dom.window;
global.document = window.document;
global.location = window.location;
const { ApolloClient, InMemoryCache } = require('@apollo/client');
const client = new ApolloClient({ uri: 'http://localhost:4000/graphql', cache: new InMemoryCache() });
console.log('with-uri-jsdom-nofetch ok');
