const { ApolloClient, InMemoryCache, HttpLink } = require('@apollo/client');
const client = new ApolloClient({ link: new HttpLink({ uri: 'http://localhost:4000/graphql' }), cache: new InMemoryCache() });
console.log('with-link ok');
