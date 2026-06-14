const { ApolloClient, InMemoryCache } = require('@apollo/client');
const client = new ApolloClient({ uri: 'http://localhost:4000/graphql', cache: new InMemoryCache() });
console.log('with-uri ok');
