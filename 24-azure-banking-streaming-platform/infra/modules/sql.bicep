@description('Azure region for Azure SQL resources.')
param location string

@description('Globally unique Azure SQL logical server name.')
param serverName string

@description('Azure SQL database name.')
param databaseName string

@description('Microsoft Entra administrator login label.')
param entraAdminLogin string

@description('Microsoft Entra administrator object ID.')
param entraAdminObjectId string

@description('Microsoft Entra tenant ID.')
param tenantId string

@description('Non-sensitive resource tags.')
param tags object

resource sqlServer 'Microsoft.Sql/servers@2023-08-01' = {
  name: serverName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    administrators: {
      administratorType: 'ActiveDirectory'
      azureADOnlyAuthentication: true
      login: entraAdminLogin
      principalType: 'User'
      sid: entraAdminObjectId
      tenantId: tenantId
    }
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    restrictOutboundNetworkAccess: 'Disabled'
    version: '12.0'
  }
}

resource database 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: sqlServer
  name: databaseName
  location: location
  tags: tags
  sku: {
    capacity: 1
    family: 'Gen5'
    name: 'GP_S_Gen5_1'
    tier: 'GeneralPurpose'
  }
  properties: {
    autoPauseDelay: 60
    createMode: 'Default'
    licenseType: 'LicenseIncluded'
    readScale: 'Disabled'
    requestedBackupStorageRedundancy: 'Local'
    zoneRedundant: false
  }
}

output databaseId string = database.id
output databaseName string = database.name
output serverId string = sqlServer.id
output serverName string = sqlServer.name
