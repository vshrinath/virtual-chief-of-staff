import click
import os
import webbrowser
from pathlib import Path
from vcos.config import get_vault

@click.command()
@click.option("--key-type", type=click.Choice(["anthropic", "openai"]), help="The provider to authenticate with.")
def auth(key_type):
    """Guide the user through API key configuration."""
    if not key_type:
        key_type = click.prompt("Which provider do you want to configure?", type=click.Choice(["anthropic", "openai"]))

    urls = {
        "anthropic": "https://console.anthropic.com/settings/keys",
        "openai": "https://platform.openai.com/api-keys"
    }

    env_vars = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY"
    }

    click.echo(f"\nOpening {key_type.capitalize()} dashboard to get your API key...")
    webbrowser.open(urls[key_type])
    
    key = click.prompt(f"Please paste your {key_type.capitalize()} API Key", hide_input=True)
    
    if not key.strip():
        click.echo("Error: Empty key provided.")
        return

    # Save to vault .env if it exists
    try:
        vault_path = get_vault()
        env_path = Path(vault_path) / ".env"
        
        lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        var_name = env_vars[key_type]
        new_line = f"{var_name}={key}\n"
        
        found = False
        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith(f"{var_name}="):
                    f.write(new_line)
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(new_line)
        
        click.echo(f"✅ Successfully saved {var_name} to {env_path}")
    except RuntimeError as e:
        click.echo(f"⚠️ Warning: Could not find vault to save key. {e}")
        click.echo(f"Please set {env_vars[key_type]}={key} manually.")

    click.echo("\nAuthentication complete! You can now run 'vcos status' to verify.")
