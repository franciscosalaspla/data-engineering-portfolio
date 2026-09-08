targetScope = 'resourceGroup'

@description('Azure region used by all Project 24 resources.')
param location string = resourceGroup().location

@allowed([
  'dev'
])
@description('Deployment environment. The MVP supports only an ephemeral dev environment.')
param environment string = 'dev'

@minLength(2)
@maxLength(8)
@description('Short lowercase prefix used to identify Project 24 resources.')
param namePrefix string = 'p24'

@description('Microsoft Entra login displayed for the Azure SQL administrator.')
param sqlEntraAdminLogin string

@description('Microsoft Entra object ID used as the Azure SQL administrator SID.')
param sqlEntraAdminObjectId string

@description('Microsoft Entra tenant ID associated with the Azure SQL administrator.')
param tenantId string = tenant().tenantId

@description('Additional non-sensitive tags merged with the required Project 24 tags.')
param tags object = {}

var uniqueSuffix = take(uniqueString(subscription().subscriptionId, resourceGroup().id), 8)
var compactStem = toLower('${namePrefix}${environment}${uniqueSuffix}')
var hyphenStem = toLower('${namePrefix}-${environment}-${uniqueSuffix}')
var commonTags = union(tags, {
  environment: environment
  managedBy: 'bicep'
  project: '24'
  workload: 'banking-streaming'
})

module storage './modules/storage.bicep' = {
  name: 'storage-${uniqueSuffix}'
  params: {
    location: location
    name: 'st${compactStem}'
    tags: commonTags
  }
}

module eventHubs './modules/event-hubs.bicep' = {
  name: 'event-hubs-${uniqueSuffix}'
  params: {
    location: location
    namespaceName: 'evhns-${hyphenStem}'
    tags: commonTags
  }
}

module dataFactory './modules/data-factory.bicep' = {
  name: 'data-factory-${uniqueSuffix}'
  params: {
    factoryName: 'adf-${hyphenStem}'
    location: location
    tags: commonTags
  }
}

module databricks './modules/databricks.bicep' = {
  name: 'databricks-${uniqueSuffix}'
  params: {
    location: location
    managedResourceGroupName: 'rg-${hyphenStem}-databricks-managed'
    tags: commonTags
    workspaceName: 'dbw-${hyphenStem}'
  }
}

module sql './modules/sql.bicep' = {
  name: 'sql-${uniqueSuffix}'
  params: {
    databaseName: 'banking'
    entraAdminLogin: sqlEntraAdminLogin
    entraAdminObjectId: sqlEntraAdminObjectId
    location: location
    serverName: 'sql-${hyphenStem}'
    tags: commonTags
    tenantId: tenantId
  }
}

module keyVault './modules/key-vault.bicep' = {
  name: 'key-vault-${uniqueSuffix}'
  params: {
    location: location
    name: 'kv-${hyphenStem}'
    tags: commonTags
    tenantId: tenantId
  }
}

module monitoring './modules/monitoring.bicep' = {
  name: 'monitoring-${uniqueSuffix}'
  params: {
    location: location
    name: 'log-${hyphenStem}'
    tags: commonTags
  }
}

output resourceNames object = {
  dataFactory: dataFactory.outputs.name
  databricksWorkspace: databricks.outputs.name
  eventHub: eventHubs.outputs.eventHubName
  eventHubsNamespace: eventHubs.outputs.namespaceName
  keyVault: keyVault.outputs.name
  logAnalyticsWorkspace: monitoring.outputs.name
  sqlDatabase: sql.outputs.databaseName
  sqlServer: sql.outputs.serverName
  storageAccount: storage.outputs.name
}

output resourceIds object = {
  dataFactory: dataFactory.outputs.id
  databricksWorkspace: databricks.outputs.id
  eventHubsNamespace: eventHubs.outputs.namespaceId
  keyVault: keyVault.outputs.id
  logAnalyticsWorkspace: monitoring.outputs.id
  sqlDatabase: sql.outputs.databaseId
  sqlServer: sql.outputs.serverId
  storageAccount: storage.outputs.id
}
