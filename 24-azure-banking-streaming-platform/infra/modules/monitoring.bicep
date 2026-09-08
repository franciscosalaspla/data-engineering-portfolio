@description('Azure region for Log Analytics.')
param location string

@description('Log Analytics workspace name.')
param name string

@description('Non-sensitive resource tags.')
param tags object

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    retentionInDays: 30
    sku: {
      name: 'PerGB2018'
    }
  }
}

output id string = workspace.id
output name string = workspace.name
