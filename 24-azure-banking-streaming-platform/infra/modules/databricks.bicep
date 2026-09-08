@description('Azure region for the Databricks workspace.')
param location string

@description('Databricks workspace name.')
param workspaceName string

@description('Dedicated managed resource group name for Databricks-managed resources.')
param managedResourceGroupName string

@description('Non-sensitive resource tags.')
param tags object

resource workspace 'Microsoft.Databricks/workspaces@2024-05-01' = {
  name: workspaceName
  location: location
  tags: tags
  sku: {
    name: 'standard'
  }
  properties: {
    managedResourceGroupId: '${subscription().id}/resourceGroups/${managedResourceGroupName}'
    parameters: {
      enableNoPublicIp: {
        value: true
      }
    }
    publicNetworkAccess: 'Enabled'
    requiredNsgRules: 'AllRules'
  }
}

output id string = workspace.id
output name string = workspace.name
output workspaceUrl string = workspace.properties.workspaceUrl
