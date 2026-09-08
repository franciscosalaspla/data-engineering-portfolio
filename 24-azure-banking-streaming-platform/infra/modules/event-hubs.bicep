@description('Azure region for Event Hubs resources.')
param location string

@description('Globally unique Event Hubs namespace name.')
param namespaceName string

@description('Non-sensitive resource tags.')
param tags object

@description('Transaction event hub name.')
param eventHubName string = 'transactions-v1'

@description('Consumer group reserved for the streaming processor.')
param consumerGroupName string = 'databricks-streaming'

resource eventHubsNamespace 'Microsoft.EventHub/namespaces@2024-01-01' = {
  name: namespaceName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    capacity: 1
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    disableLocalAuth: true
    isAutoInflateEnabled: false
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    zoneRedundant: false
  }
}

resource transactionHub 'Microsoft.EventHub/namespaces/eventhubs@2024-01-01' = {
  parent: eventHubsNamespace
  name: eventHubName
  properties: {
    messageRetentionInDays: 1
    partitionCount: 2
    status: 'Active'
  }
}

resource streamingConsumerGroup 'Microsoft.EventHub/namespaces/eventhubs/consumergroups@2024-01-01' = {
  parent: transactionHub
  name: consumerGroupName
  properties: {
    userMetadata: 'Project 24 Structured Streaming consumer'
  }
}

output eventHubId string = transactionHub.id
output eventHubName string = transactionHub.name
output namespaceId string = eventHubsNamespace.id
output namespaceName string = eventHubsNamespace.name
