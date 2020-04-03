module.exports = {
  siteMetadata: {
    title: 'K-Container Reference Implementation for EDA',
    description: 'A reference implementation solution for container shipment using Event-Driven Architecture principles and techniques by the IBM Garage for Cloud Solution Engineering Event-Driven Architecture squad.',
    keywords: 'gatsby,theme,carbon',
  },
  pathPrefix: `/refarch-kc`,
  plugins: [
    {
      resolve: 'gatsby-plugin-manifest',
      options: {
        name: 'Carbon Design Gatsby Theme',
        short_name: 'Gatsby Theme Carbon',
        start_url: '/',
        background_color: '#ffffff',
        theme_color: '#0062ff',
        display: 'browser',
      },
    },
    {
      resolve: 'gatsby-theme-carbon',
      options: {
        isSearchEnabled: true,
        titleType: 'append'
      },
    },
  ],
};
