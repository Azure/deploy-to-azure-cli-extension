from knack.help_files import helps

def load_aci_help():
    helps['aci'] = """
    type: group
    short-summary: Commands to Manage Azure Container Instances App
    long-summary:
    """

    helps['aci up'] = """
    type: command
    short-summary: Deploy to Azure Container Instances using GitHub Actions
    long-summary:
    """