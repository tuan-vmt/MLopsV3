
def create_services_string(ws_config, service_key):
    subscription_id = ws_config['subscription_id']
    resource_group = ws_config['resource_group']
    service_name = ws_config[service_key]
    service_type = None
    if service_key == 'storage_account':
        service_type = 'Microsoft.Storage/storageAccounts'
    elif service_key == 'container_registry':
        service_type = 'Microsoft.ContainerRegistry/registries'
    elif service_key == 'key_vault':
        service_type = 'Microsoft.KeyVault/vaults'
    elif service_key == 'app_insights':
        service_type = 'Microsoft.insights/components'
    return "/subscriptions/{}/resourceGroups/{}/providers/{}/{}".format(subscription_id, resource_group, service_type, service_name)

def read_config(config_file):
    # read config file
    with open(config_file, encoding='utf-8-sig') as f:
        return json.load(f)['workspace']['configuration']

def create_workspace(ws_config):
    # Create ML client with default azure credential
    ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id=ws_config['subscription_id'],
            resource_group_name=ws_config['resource_group'],
            workspace_name=ws_config['name']
        )
    try:
        ws = ml_client.workspaces.get(ws_config['name'])
    except:
        print('Workspace is not exist, creating at the first time ...!')
        # Change the following variables to resource ids of your existing storage account, key vault, application insights
        # and container registry. Here we reuse the ones we just created for the basic workspace
        storage_account = create_services_string(ws_config, 'storage_account')
        existing_storage_account = (
            # e.g. "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.Storage/storageAccounts/<STORAGE_ACCOUNT>"
            storage_account
        )

        container_registry = create_services_string(ws_config, 'container_registry')
        existing_container_registry = (
            # e.g. "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.ContainerRegistry/registries/<CONTAINER_REGISTRY>"
            container_registry
        )

        key_vault = create_services_string(ws_config, 'key_vault')
        existing_key_vault = (
            # e.g. "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.KeyVault/vaults/<KEY_VAULT>"
            key_vault
        )

        app_insights = create_services_string(ws_config, 'app_insights')
        existing_application_insights = (
            # e.g. "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.insights/components/<APP_INSIGHTS>"
            app_insights
        )

        ws = Workspace(
            name=ws_config['name'],
            location=ws_config['location'],
            display_name="Bring your own dependent resources-example",
            description="This sample specifies a workspace configuration with existing dependent resources",
            storage_account=existing_storage_account,
            container_registry=existing_container_registry,
            key_vault=existing_key_vault,
            application_insights=existing_application_insights,
            tags=ws_config['tags'],
        )

        ws_result = ml_client.workspaces.begin_create(
            ws
        ).result()

        print(ws_result)
    return ws

def get_workspace(ws_config):
    ws_name = ws_config['name']
    ws_subscription_id = ws_config['subscription_id']
    ws_rg = ws_config['resource_group']
    ws_location = ws_config['location']

    ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id=ws_subscription_id,
            resource_group_name=ws_rg,
            workspace_name=ws_name
        )
    ws = ml_client.workspaces.get(ws_config['name'])
    print(f'Existing ML workspace {ws_name} found')
    return ws

def save_workspace_config(workspace, folder):
    # create json format
    ws_json = {}
    ws_json['subscription_id'] = workspace.subscription_id
    ws_json['resource_group'] = workspace.resource_group
    ws_json['workspace_name'] = workspace.name
    ws_json['location'] = workspace.location
    # save json file
    os.makedirs(folder, exist_ok=True)
    with open(folder + '/config.json', "w+") as outfile:
        json.dump(ws_json, outfile)

def main():
    args = sys.argv[1:]
    print('args: ', args)
    if len(args) >= 2 and args[0] == '-config':
        # execute load config file and workspace creation
        ws_config = read_config(args[1])
        
        # if creation allowed, use create_workspace
        # otherwise, use get_workspace
        #ws = create_workspace(ws_config)
        ws = get_workspace(ws_config)

        # print Workspace details
        print(ws.subscription_id, ws.resource_group, ws.name, ws.location, sep="\n")
        # save workspace to aml_config (default)
        out_folder = 'aml_config'
        if len(args) >= 4 and args[2] == '-outfolder':
            out_folder = args[3]
        save_workspace_config(ws, out_folder)
    else:
        print('Usage: -config <config file name> [-outfolder <Azure ML config folder>]')

if __name__ == '__main__':
    main()
