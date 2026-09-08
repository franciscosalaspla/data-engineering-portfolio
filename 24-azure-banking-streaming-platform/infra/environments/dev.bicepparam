using '../main.bicep'

param environment = 'dev'
param location = 'eastus2'
param namePrefix = 'p24'

// Static placeholders for compilation only. Hito 3 must replace them with verified Entra IDs.
param sqlEntraAdminLogin = 'replace-in-hito-3'
param sqlEntraAdminObjectId = '00000000-0000-0000-0000-000000000000'

param tags = {
  lifecycle: 'ephemeral'
  purpose: 'portfolio-learning'
}
