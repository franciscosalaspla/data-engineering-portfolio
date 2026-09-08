@description('Azure region for Key Vault.')
param location string

@minLength(3)
@maxLength(24)
@description('Globally unique Key Vault name.')
param name string

@description('Microsoft Entra tenant ID.')
param tenantId string

@description('Non-sensitive resource tags.')
param tags object

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    enablePurgeProtection: true
    enableRbacAuthorization: true
    enableSoftDelete: true
    publicNetworkAccess: 'Enabled'
    sku: {
      family: 'A'
      name: 'standard'
    }
    softDeleteRetentionInDays: 7
    tenantId: tenantId
  }
}

output id string = keyVault.id
output name string = keyVault.name
output uri string = keyVault.properties.vaultUri
