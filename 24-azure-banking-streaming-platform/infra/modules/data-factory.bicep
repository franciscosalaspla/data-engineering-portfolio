@description('Azure region for Data Factory.')
param location string

@description('Globally unique Data Factory name.')
param factoryName string

@description('Non-sensitive resource tags.')
param tags object

resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: factoryName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

output id string = dataFactory.id
output name string = dataFactory.name
output principalId string = dataFactory.identity.principalId
